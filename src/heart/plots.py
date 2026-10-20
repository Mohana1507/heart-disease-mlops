"""Plot helpers (headless backend) used by training and EDA."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay  # noqa: E402


def save_confusion_matrix(model, X, y, path: Path, title: str) -> Path:
    fig, ax = plt.subplots(figsize=(4.5, 4))
    ConfusionMatrixDisplay.from_estimator(
        model, X, y, ax=ax, display_labels=["No disease", "Disease"],
        colorbar=False, cmap="Blues")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def save_roc_curve(model, X, y, path: Path, title: str) -> Path:
    fig, ax = plt.subplots(figsize=(4.5, 4))
    RocCurveDisplay.from_estimator(model, X, y, ax=ax)
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="Chance")
    ax.legend(loc="lower right")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def save_model_comparison(results: dict, path: Path) -> Path:
    names = list(results)
    means = [results[n]["cv"]["cv_roc_auc_mean"] for n in names]
    stds = [results[n]["cv"]["cv_roc_auc_std"] for n in names]
    fig, ax = plt.subplots(figsize=(6, 3.8))
    ax.bar(names, means, yerr=stds, capsize=5, color="#3b7dd8")
    ax.set_ylabel("Nested CV ROC-AUC")
    ax.set_ylim(0.5, 1.0)
    ax.set_title("Model comparison (mean ± std over outer folds)")
    plt.setp(ax.get_xticklabels(), rotation=15)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path
