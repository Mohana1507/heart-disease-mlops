"""Exploratory data analysis: writes figures and a text summary."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

from . import config, data  # noqa: E402

sns.set_theme(style="whitegrid", context="notebook")


def class_balance(df: pd.DataFrame, out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(4.5, 3.8))
    counts = df[config.TARGET].value_counts().sort_index()
    ax.bar(["No disease (0)", "Disease (1)"], counts.values, color=["#4c9f70", "#d9534f"])
    for i, v in enumerate(counts.values):
        ax.text(i, v + 1, f"{v} ({v / len(df):.1%})", ha="center")
    ax.set_ylabel("Patients")
    ax.set_title("Class balance")
    fig.tight_layout()
    path = out / "eda_class_balance.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def numeric_histograms(df: pd.DataFrame, out: Path) -> Path:
    cols = config.NUMERIC_FEATURES
    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    for ax, col in zip(axes.ravel(), cols):
        sns.histplot(data=df, x=col, hue=config.TARGET, kde=True, ax=ax,
                     palette=["#4c9f70", "#d9534f"], element="step")
        ax.set_title(f"{col}: {config.FEATURE_DESCRIPTIONS[col]}", fontsize=9)
    axes.ravel()[-1].axis("off")
    fig.suptitle("Numeric feature distributions by outcome", y=1.0)
    fig.tight_layout()
    path = out / "eda_numeric_histograms.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def categorical_counts(df: pd.DataFrame, out: Path) -> Path:
    cols = config.CATEGORICAL_FEATURES
    fig, axes = plt.subplots(2, 4, figsize=(15, 7))
    for ax, col in zip(axes.ravel(), cols):
        sns.countplot(data=df, x=col, hue=config.TARGET, ax=ax,
                      palette=["#4c9f70", "#d9534f"])
        ax.set_title(col)
        ax.legend(title="target", fontsize=7)
    fig.suptitle("Categorical features by outcome", y=1.0)
    fig.tight_layout()
    path = out / "eda_categorical_counts.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def correlation_heatmap(df: pd.DataFrame, out: Path) -> Path:
    corr = df.corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(9, 7.5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
                square=True, linewidths=0.5, ax=ax, cbar_kws={"shrink": 0.8})
    ax.set_title("Correlation matrix (Pearson)")
    fig.tight_layout()
    path = out / "eda_correlation_heatmap.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def numeric_boxplots(df: pd.DataFrame, out: Path) -> Path:
    cols = config.NUMERIC_FEATURES
    fig, axes = plt.subplots(1, len(cols), figsize=(15, 4))
    for ax, col in zip(axes, cols):
        sns.boxplot(data=df, x=config.TARGET, y=col, ax=ax,
                    palette=["#4c9f70", "#d9534f"], hue=config.TARGET, legend=False)
        ax.set_title(col)
    fig.tight_layout()
    path = out / "eda_boxplots.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def summary_text(df: pd.DataFrame) -> str:
    lines = [
        f"Rows: {len(df)}  Columns: {df.shape[1]}",
        "", "Missing values per column:", df.isna().sum().to_string(),
        "", "Class balance:", df[config.TARGET].value_counts().sort_index().to_string(),
        "", "Descriptive statistics:", df.describe().T.round(2).to_string(),
    ]
    return "\n".join(lines)


def run(out_dir: Path = config.FIGURES_DIR, df: pd.DataFrame | None = None) -> list[Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df = data.ensure_clean_data() if df is None else df
    paths = [
        class_balance(df, out_dir), numeric_histograms(df, out_dir),
        categorical_counts(df, out_dir), correlation_heatmap(df, out_dir),
        numeric_boxplots(df, out_dir),
    ]
    summary = out_dir.parent / "eda_summary.txt"
    summary.write_text(summary_text(df))
    return paths + [summary]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default=str(config.FIGURES_DIR))
    args = parser.parse_args()
    for p in run(Path(args.out_dir)):
        print("wrote", p)
