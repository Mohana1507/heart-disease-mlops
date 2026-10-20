"""Model definitions, tuning, cross-validation and evaluation (no MLflow here)."""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline

from . import config
from .features import build_preprocessor

SCORING = ["accuracy", "precision", "recall", "f1", "roc_auc"]


def make_pipeline(clf) -> Pipeline:
    return Pipeline([("preprocess", build_preprocessor()), ("clf", clf)])


def candidate_models(fast: bool = False, seed: int = config.RANDOM_STATE) -> dict:
    """Return {name: (pipeline, param_grid)}. `fast` shrinks the grids for CI/tests."""
    if fast:
        lr_grid = {"clf__C": [0.1, 1.0]}
        rf_grid = {"clf__n_estimators": [50], "clf__max_depth": [3, None]}
        gb_grid = {"clf__n_estimators": [50], "clf__max_depth": [2]}
    else:
        lr_grid = {"clf__C": [0.01, 0.1, 1.0, 10.0], "clf__penalty": ["l1", "l2"]}
        rf_grid = {
            "clf__n_estimators": [100, 300],
            "clf__max_depth": [3, 6, None],
            "clf__min_samples_leaf": [1, 3, 5],
        }
        gb_grid = {
            "clf__n_estimators": [100, 200],
            "clf__learning_rate": [0.05, 0.1],
            "clf__max_depth": [2, 3],
        }
    return {
        "logistic_regression": (
            make_pipeline(LogisticRegression(solver="liblinear", max_iter=2000,
                                             random_state=seed)),
            lr_grid,
        ),
        "random_forest": (
            make_pipeline(RandomForestClassifier(random_state=seed)),
            rf_grid,
        ),
        "gradient_boosting": (
            make_pipeline(GradientBoostingClassifier(random_state=seed)),
            gb_grid,
        ),
    }


def make_search(pipe, grid, folds: int, seed: int = config.RANDOM_STATE,
                n_jobs: int | None = None) -> GridSearchCV:
    if n_jobs is None:
        n_jobs = int(os.getenv("N_JOBS", "1"))
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    return GridSearchCV(pipe, grid, scoring="roc_auc", cv=cv, n_jobs=n_jobs, refit=True)


def nested_cv(pipe, grid, X, y, outer: int = 5, inner: int = 3,
              seed: int = config.RANDOM_STATE, n_jobs: int | None = None) -> dict:
    """Nested CV: the inner loop tunes, the outer loop gives unbiased estimates."""
    outer_cv = StratifiedKFold(n_splits=outer, shuffle=True, random_state=seed)
    scores = cross_validate(make_search(pipe, grid, inner, seed, n_jobs=n_jobs), X, y,
                            cv=outer_cv, scoring=SCORING)
    summary = {}
    for metric in SCORING:
        vals = scores[f"test_{metric}"]
        summary[f"cv_{metric}_mean"] = float(np.mean(vals))
        summary[f"cv_{metric}_std"] = float(np.std(vals))
    return summary


def evaluate(model, X: pd.DataFrame, y) -> dict:
    """Hold-out metrics at the default 0.5 decision threshold."""
    proba = model.predict_proba(X)[:, 1]
    pred = (proba >= 0.5).astype(int)
    return {
        "accuracy": float(accuracy_score(y, pred)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, proba)),
    }
