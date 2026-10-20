import joblib
import numpy as np
import pytest
from sklearn.model_selection import train_test_split

from heart import config, data, modeling


def test_at_least_two_candidates():
    assert len(modeling.candidate_models(fast=True)) >= 2


def test_evaluate_returns_valid_metrics(synthetic_df):
    X, y = data.split_xy(synthetic_df)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, stratify=y, random_state=1)
    pipe, grid = modeling.candidate_models(fast=True)["logistic_regression"]
    search = modeling.make_search(pipe, grid, folds=3)
    search.fit(Xtr, ytr)
    metrics = modeling.evaluate(search.best_estimator_, Xte, yte)
    assert set(metrics) == {"accuracy", "precision", "recall", "f1", "roc_auc"}
    assert all(0.0 <= v <= 1.0 for v in metrics.values())
    assert metrics["roc_auc"] > 0.6  # the synthetic signal is learnable


def test_nested_cv_summary_keys(synthetic_df):
    X, y = data.split_xy(synthetic_df)
    pipe, grid = modeling.candidate_models(fast=True)["logistic_regression"]
    summary = modeling.nested_cv(pipe, grid, X, y, outer=3, inner=2)
    assert "cv_roc_auc_mean" in summary and "cv_recall_std" in summary


def test_training_is_reproducible(synthetic_df):
    X, y = data.split_xy(synthetic_df)
    runs = []
    for _ in range(2):
        pipe, _ = modeling.candidate_models(fast=True, seed=7)["random_forest"]
        pipe.fit(X, y)
        runs.append(pipe.predict_proba(X)[:, 1])
    assert np.allclose(runs[0], runs[1])


def test_saved_model_round_trip(model_dir, synthetic_df):
    model = joblib.load(model_dir / "model.joblib")
    proba = model.predict_proba(synthetic_df[config.FEATURES].head(5))
    assert proba.shape == (5, 2)


def test_train_script_end_to_end(tmp_path, synthetic_df):
    pytest.importorskip("mlflow")
    from heart import train
    csv = tmp_path / "clean.csv"
    synthetic_df.to_csv(csv, index=False)
    results = train.main([
        "--data", str(csv), "--model-dir", str(tmp_path / "m"),
        "--figures-dir", str(tmp_path / "f"),
        "--tracking-uri", (tmp_path / "mlruns").as_uri(),
        "--outer-folds", "3", "--inner-folds", "2", "--fast",
    ])
    assert (tmp_path / "m" / "model.joblib").exists()
    assert (tmp_path / "m" / "metadata.json").exists()
    assert results["selected"] in results
