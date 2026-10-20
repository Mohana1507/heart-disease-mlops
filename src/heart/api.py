"""FastAPI service exposing the trained heart disease classifier."""
from __future__ import annotations

import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field

from . import __version__, config

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"),
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("heart.api")

REQUESTS = Counter("api_requests_total", "HTTP requests", ["method", "path", "status"])
LATENCY = Histogram("api_request_latency_seconds", "Request latency in seconds", ["path"])
PREDICTIONS = Counter("predictions_total", "Predictions served", ["label"])

EXAMPLE = {
    "age": 63, "sex": 1, "cp": 1, "trestbps": 145, "chol": 233, "fbs": 1,
    "restecg": 2, "thalach": 150, "exang": 0, "oldpeak": 2.3, "slope": 3,
    "ca": 0, "thal": 6,
}


class PatientFeatures(BaseModel):
    model_config = {"json_schema_extra": {"example": EXAMPLE}}

    age: float = Field(..., ge=1, le=120, description="Age in years")
    sex: int = Field(..., ge=0, le=1, description="1 = male, 0 = female")
    cp: int = Field(..., ge=1, le=4, description="Chest pain type")
    trestbps: float = Field(..., ge=50, le=300, description="Resting blood pressure")
    chol: float = Field(..., ge=50, le=700, description="Serum cholesterol mg/dl")
    fbs: int = Field(..., ge=0, le=1, description="Fasting blood sugar > 120")
    restecg: int = Field(..., ge=0, le=2, description="Resting ECG result")
    thalach: float = Field(..., ge=50, le=250, description="Max heart rate achieved")
    exang: int = Field(..., ge=0, le=1, description="Exercise-induced angina")
    oldpeak: float = Field(..., ge=0, le=10, description="ST depression")
    slope: int = Field(..., ge=1, le=3, description="Slope of peak ST segment")
    ca: float | None = Field(None, ge=0, le=3, description="Vessels coloured (optional)")
    thal: float | None = Field(None, ge=3, le=7, description="Thal code 3/6/7 (optional)")


class PredictionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    prediction: int
    label: str
    probability_disease: float
    confidence: float
    model_version: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    path = Path(os.getenv("MODEL_PATH", str(config.MODEL_PATH)))
    meta_path = Path(os.getenv("METADATA_PATH", str(path.with_name("metadata.json"))))
    app.state.model = None
    app.state.metadata = {}
    try:
        app.state.model = joblib.load(path)
        if meta_path.exists():
            app.state.metadata = json.loads(meta_path.read_text())
        logger.info("Loaded model from %s", path)
    except Exception:
        logger.exception("Model failed to load from %s", path)
    yield


app = FastAPI(title="Heart Disease Risk API", version=__version__, lifespan=lifespan)


@app.middleware("http")
async def log_and_measure(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        elapsed = time.perf_counter() - start
        route = request.scope.get("route")
        path = getattr(route, "path", request.url.path)
        REQUESTS.labels(request.method, path, str(status)).inc()
        LATENCY.labels(path).observe(elapsed)
        logger.info(json.dumps({
            "event": "request", "request_id": request_id, "method": request.method,
            "path": request.url.path, "status": status,
            "latency_ms": round(elapsed * 1000, 2),
        }))


@app.get("/")
def root():
    return {"service": "heart-disease-risk-api", "version": __version__,
            "docs": "/docs", "predict": "POST /predict"}


@app.get("/health")
def health(request: Request):
    loaded = request.app.state.model is not None
    return {"status": "ok" if loaded else "degraded", "model_loaded": loaded}


@app.get("/model-info")
def model_info(request: Request):
    if request.app.state.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return request.app.state.metadata


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PatientFeatures, request: Request):
    model = request.app.state.model
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    record = {k: (np.nan if v is None else v) for k, v in payload.model_dump().items()}
    row = pd.DataFrame([record], columns=config.FEATURES).astype("float64")
    proba = float(model.predict_proba(row)[0, 1])
    pred = int(proba >= 0.5)
    confidence = proba if pred == 1 else 1.0 - proba
    label = "disease" if pred == 1 else "no_disease"

    PREDICTIONS.labels(label).inc()
    version = request.app.state.metadata.get("version", "unknown")
    # Only the outcome is logged, never the patient's raw inputs.
    logger.info(json.dumps({"event": "prediction", "label": label,
                            "probability": round(proba, 4), "model_version": version}))
    return PredictionResponse(prediction=pred, label=label,
                              probability_disease=round(proba, 4),
                              confidence=round(confidence, 4), model_version=version)


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
