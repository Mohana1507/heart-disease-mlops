import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

PAYLOAD = {
    "age": 63, "sex": 1, "cp": 1, "trestbps": 145, "chol": 233, "fbs": 1,
    "restecg": 2, "thalach": 150, "exang": 0, "oldpeak": 2.3, "slope": 3,
    "ca": 0, "thal": 6,
}


@pytest.fixture()
def client(model_dir, monkeypatch):
    monkeypatch.setenv("MODEL_PATH", str(model_dir / "model.joblib"))
    from heart.api import app
    with TestClient(app) as c:
        yield c


def test_health(client):
    body = client.get("/health").json()
    assert body == {"status": "ok", "model_loaded": True}


def test_predict_returns_prediction_and_confidence(client):
    r = client.post("/predict", json=PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert body["prediction"] in (0, 1)
    assert 0.0 <= body["probability_disease"] <= 1.0
    assert 0.5 <= body["confidence"] <= 1.0
    assert body["model_version"] == "test-1"


def test_optional_fields_may_be_omitted(client):
    payload = {k: v for k, v in PAYLOAD.items() if k not in ("ca", "thal")}
    assert client.post("/predict", json=payload).status_code == 200


def test_invalid_input_rejected(client):
    bad = dict(PAYLOAD, age=-5)
    assert client.post("/predict", json=bad).status_code == 422
    missing = {k: v for k, v in PAYLOAD.items() if k != "chol"}
    assert client.post("/predict", json=missing).status_code == 422


def test_metrics_endpoint_exposes_counters(client):
    client.post("/predict", json=PAYLOAD)
    text = client.get("/metrics").text
    assert "api_requests_total" in text and "predictions_total" in text


def test_missing_model_gives_503(monkeypatch, tmp_path):
    monkeypatch.setenv("MODEL_PATH", str(tmp_path / "nope.joblib"))
    from heart.api import app
    with TestClient(app) as c:
        assert c.get("/health").json()["status"] == "degraded"
        assert c.post("/predict", json=PAYLOAD).status_code == 503
