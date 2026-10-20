"""Train, tune, track (MLflow) and package the heart disease classifiers."""
from __future__ import annotations

import argparse
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
import sklearn
from mlflow.models import infer_signature
from sklearn.model_selection import train_test_split

from . import config, data, modeling, plots

log = logging.getLogger("heart.train")


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", help="Path to a cleaned CSV (default: build from UCI)")
    p.add_argument("--model-dir", default=str(config.MODEL_DIR))
    p.add_argument("--figures-dir", default=str(config.FIGURES_DIR))
    p.add_argument("--tracking-uri",
                   default=os.getenv("MLFLOW_TRACKING_URI",
                                     (config.ROOT / "mlruns").as_uri()))
    p.add_argument("--experiment", default="heart-disease-risk")
    p.add_argument("--test-size", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=config.RANDOM_STATE)
    p.add_argument("--outer-folds", type=int, default=5)
    p.add_argument("--inner-folds", type=int, default=3)
    p.add_argument("--fast", action="store_true", help="Small grids (CI / smoke tests)")
    return p.parse_args(argv)


def main(argv=None) -> dict:
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    model_dir, fig_dir = Path(args.model_dir), Path(args.figures_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.data) if args.data else data.ensure_clean_data()
    X, y = data.split_xy(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, stratify=y, random_state=args.seed)
    log.info("Train rows: %d, test rows: %d", len(X_train), len(X_test))

    mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.set_experiment(args.experiment)

    results: dict = {}
    for name, (pipe, grid) in modeling.candidate_models(args.fast, args.seed).items():
        with mlflow.start_run(run_name=name):
            log.info("Training %s", name)
            mlflow.set_tags({"stage": "experiment", "model_family": name})
            mlflow.log_params({
                "model": name, "seed": args.seed, "test_size": args.test_size,
                "outer_folds": args.outer_folds, "inner_folds": args.inner_folds,
                "n_train": len(X_train), "n_test": len(X_test),
                "grid_size": sum(len(v) for v in grid.values()),
            })

            cv_summary = modeling.nested_cv(pipe, grid, X_train, y_train,
                                            args.outer_folds, args.inner_folds, args.seed)
            search = modeling.make_search(pipe, grid, args.inner_folds, args.seed)
            search.fit(X_train, y_train)
            best = search.best_estimator_
            test_metrics = modeling.evaluate(best, X_test, y_test)

            mlflow.log_params({f"best_{k}": v for k, v in search.best_params_.items()})
            mlflow.log_metrics(cv_summary)
            mlflow.log_metric("tuning_best_cv_roc_auc", float(search.best_score_))
            mlflow.log_metrics({f"test_{k}": v for k, v in test_metrics.items()})

            cm = plots.save_confusion_matrix(best, X_test, y_test,
                                             fig_dir / f"{name}_confusion_matrix.png",
                                             f"{name}: test confusion matrix")
            roc = plots.save_roc_curve(best, X_test, y_test, fig_dir / f"{name}_roc.png",
                                       f"{name}: test ROC")
            mlflow.log_artifact(str(cm), artifact_path="plots")
            mlflow.log_artifact(str(roc), artifact_path="plots")

            mlflow.sklearn.log_model(
                best, artifact_path="model",
                signature=infer_signature(X_train, best.predict(X_train)),
                input_example=X_train.head(3))

            results[name] = {"estimator": best, "cv": cv_summary, "test": test_metrics,
                             "params": search.best_params_}
            log.info("%s nested-CV ROC-AUC %.3f | test ROC-AUC %.3f", name,
                     cv_summary["cv_roc_auc_mean"], test_metrics["roc_auc"])

    best_name = max(results, key=lambda n: results[n]["cv"]["cv_roc_auc_mean"])
    chosen = results[best_name]
    stamp = datetime.now(timezone.utc)
    metadata = {
        "model_name": best_name,
        "version": f"{best_name}-{stamp:%Y%m%d%H%M%S}",
        "trained_at": stamp.isoformat(),
        "sklearn_version": sklearn.__version__,
        "features": config.FEATURES,
        "n_train": len(X_train), "n_test": len(X_test), "seed": args.seed,
        "best_params": chosen["params"],
        "cv_metrics": chosen["cv"], "test_metrics": chosen["test"],
        "git_sha": os.getenv("GITHUB_SHA", "local"),
    }
    model_path = model_dir / "model.joblib"
    meta_path = model_dir / "metadata.json"
    joblib.dump(chosen["estimator"], model_path)
    meta_path.write_text(json.dumps(metadata, indent=2, default=str))

    with mlflow.start_run(run_name="final_model_selection"):
        mlflow.set_tags({"stage": "production-candidate", "selected_model": best_name})
        mlflow.log_param("selected_model", best_name)
        mlflow.log_metrics({f"test_{k}": v for k, v in chosen["test"].items()})
        mlflow.log_metrics({k: v for k, v in chosen["cv"].items() if k.endswith("_mean")})
        comparison = plots.save_model_comparison(results, fig_dir / "model_comparison.png")
        mlflow.log_artifact(str(comparison), artifact_path="plots")
        mlflow.log_artifact(str(meta_path), artifact_path="packaging")
        mlflow.log_artifact(str(model_path), artifact_path="packaging")

    log.info("Selected %s -> %s", best_name, model_path)
    results["selected"] = best_name
    return results


if __name__ == "__main__":
    main()
