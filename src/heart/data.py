"""Data acquisition and cleaning for the Cleveland heart disease data."""
from __future__ import annotations

import logging
import os
import urllib.request
from pathlib import Path

import pandas as pd

from . import config

log = logging.getLogger(__name__)


def download_raw(dest: Path = config.RAW_PATH, url: str | None = None,
                 timeout: int = 30) -> Path:
    """Download the raw UCI file. The URL can be overridden with HEART_DATA_URL."""
    url = url or os.getenv("HEART_DATA_URL", config.DATA_URL)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            payload = resp.read()
    except Exception as exc:
        raise RuntimeError(
            f"Could not download the dataset from {url} ({exc}). Download "
            f"processed.cleveland.data manually from the UCI repository and "
            f"place it at {dest}."
        ) from exc
    dest.write_bytes(payload)
    log.info("Downloaded %d bytes to %s", len(payload), dest)
    return dest


def load_raw(path: Path = config.RAW_PATH) -> pd.DataFrame:
    """Read the headerless raw file; '?' marks a missing value."""
    return pd.read_csv(path, header=None, names=config.COLUMNS,
                       na_values="?", skipinitialspace=True)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Type-cast, de-duplicate and binarise the target.

    Missing feature values are deliberately kept as NaN here; they are imputed
    inside the modelling pipeline so that no statistics leak from validation
    folds into training.
    """
    absent = [c for c in config.COLUMNS if c not in df.columns]
    if absent:
        raise ValueError(f"Missing expected columns: {absent}")

    out = df[config.COLUMNS].copy()
    for col in config.COLUMNS:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    out = out.dropna(subset=[config.TARGET]).drop_duplicates().reset_index(drop=True)
    out[config.TARGET] = (out[config.TARGET] > 0).astype(int)
    out = out.astype({c: "float64" for c in config.FEATURES})
    return out


def ensure_clean_data(path: Path = config.CLEAN_PATH, force: bool = False) -> pd.DataFrame:
    """Return the cleaned dataset, downloading and building it if necessary."""
    path = Path(path)
    if path.exists() and not force:
        return pd.read_csv(path)
    if not config.RAW_PATH.exists():
        download_raw(config.RAW_PATH)
    df = clean(load_raw(config.RAW_PATH))
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df


def split_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    return df[config.FEATURES], df[config.TARGET]
