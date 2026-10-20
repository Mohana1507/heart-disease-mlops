import numpy as np
import pandas as pd
import pytest

from heart import config, data
from synthetic import make_synthetic


def test_clean_binarises_target_and_casts_floats():
    raw = make_synthetic(raw_target=True)
    out = data.clean(raw)
    assert set(out[config.TARGET].unique()) <= {0, 1}
    assert all(out[c].dtype == "float64" for c in config.FEATURES)


def test_clean_preserves_nan_and_drops_duplicates():
    raw = make_synthetic(n=50)
    raw = pd.concat([raw, raw.iloc[[0]]], ignore_index=True)
    out = data.clean(raw)
    assert len(out) <= 50
    assert out[["ca", "thal"]].isna().any().any()


def test_clean_rejects_missing_columns():
    with pytest.raises(ValueError):
        data.clean(pd.DataFrame({"age": [1.0]}))


def test_load_raw_parses_question_marks(tmp_path):
    row = "63.0,1.0,1.0,145.0,233.0,1.0,2.0,150.0,0.0,2.3,3.0,?,6.0,0\n"
    path = tmp_path / "raw.data"
    path.write_text(row * 2)
    df = data.load_raw(path)
    assert list(df.columns) == config.COLUMNS
    assert np.isnan(df.loc[0, "ca"])


def test_split_xy_shapes(synthetic_df):
    X, y = data.split_xy(synthetic_df)
    assert list(X.columns) == config.FEATURES
    assert len(X) == len(y)
