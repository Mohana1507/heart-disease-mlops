import json

import joblib
import pytest
from sklearn.linear_model import LogisticRegression

from heart import config, modeling
from synthetic import make_synthetic


@pytest.fixture(scope="session")
def synthetic_df():
    return make_synthetic()


@pytest.fixture(scope="session")
def model_dir(tmp_path_factory, synthetic_df):
    """A tiny trained model + metadata on disk, used by the API tests."""
    d = tmp_path_factory.mktemp("model")
    pipe = modeling.make_pipeline(LogisticRegression(max_iter=1000))
    pipe.fit(synthetic_df[config.FEATURES], synthetic_df[config.TARGET])
    joblib.dump(pipe, d / "model.joblib")
    (d / "metadata.json").write_text(json.dumps({"version": "test-1", "model_name": "lr"}))
    return d
