"""Small synthetic data generator with the same schema as the UCI file.

Used only so that unit tests run offline and deterministically.
"""
import numpy as np
import pandas as pd

from heart import config


def make_synthetic(n: int = 240, seed: int = 0, raw_target: bool = False) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "age": rng.integers(29, 78, n).astype(float),
        "sex": rng.integers(0, 2, n).astype(float),
        "cp": rng.integers(1, 5, n).astype(float),
        "trestbps": rng.normal(131, 17, n).clip(90, 200),
        "chol": rng.normal(246, 52, n).clip(126, 564),
        "fbs": rng.integers(0, 2, n).astype(float),
        "restecg": rng.integers(0, 3, n).astype(float),
        "thalach": rng.normal(149, 22, n).clip(71, 202),
        "exang": rng.integers(0, 2, n).astype(float),
        "oldpeak": rng.gamma(1.2, 0.9, n).clip(0, 6),
        "slope": rng.integers(1, 4, n).astype(float),
        "ca": rng.integers(0, 4, n).astype(float),
        "thal": rng.choice([3.0, 6.0, 7.0], n),
    })
    logit = (0.04 * (df["age"] - 54) + 0.9 * df["sex"] + 0.5 * (df["cp"] - 2.5)
             + 1.0 * df["exang"] + 0.7 * df["oldpeak"] - 0.03 * (df["thalach"] - 150)
             + 0.6 * df["ca"] - 0.3)
    disease = rng.random(n) < 1 / (1 + np.exp(-logit))
    if raw_target:
        df["target"] = np.where(disease, rng.integers(1, 5, n), 0)
    else:
        df["target"] = disease.astype(int)
    df.loc[rng.choice(n, 4, replace=False), "ca"] = np.nan
    df.loc[rng.choice(n, 2, replace=False), "thal"] = np.nan
    return df[config.COLUMNS]
