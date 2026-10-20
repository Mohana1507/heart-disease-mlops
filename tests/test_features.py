import numpy as np
import pandas as pd

from heart import config
from heart.features import build_preprocessor


def test_preprocessor_outputs_no_nan(synthetic_df):
    X = synthetic_df[config.FEATURES]
    out = build_preprocessor().fit_transform(X)
    assert not np.isnan(np.asarray(out.todense() if hasattr(out, "todense") else out)).any()


def test_numeric_columns_are_standardised(synthetic_df):
    X = synthetic_df[config.FEATURES]
    pre = build_preprocessor().fit(X)
    num = pre.named_transformers_["num"].transform(X[config.NUMERIC_FEATURES])
    assert np.allclose(num.mean(axis=0), 0, atol=1e-6)
    assert np.allclose(num.std(axis=0), 1, atol=1e-6)


def test_unseen_category_is_ignored(synthetic_df):
    X = synthetic_df[config.FEATURES]
    pre = build_preprocessor().fit(X)
    odd = X.head(1).copy()
    odd["cp"] = 99.0
    assert pre.transform(odd).shape[0] == 1


def test_all_features_covered():
    covered = set(config.NUMERIC_FEATURES) | set(config.CATEGORICAL_FEATURES)
    assert covered == set(config.FEATURES)
    assert isinstance(pd.Series(config.FEATURES), pd.Series)
