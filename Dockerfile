FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    MODEL_PATH=/app/models/model.joblib

WORKDIR /app

COPY requirements-serve.txt .
RUN pip install --no-cache-dir -r requirements-serve.txt

COPY src/ src/
COPY models/ models/
# Fail the build early with a clear message if the model has not been trained.
RUN test -f models/model.joblib || \
    (echo "models/model.joblib missing: run 'python -m heart.train' first" && exit 1)

RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status == 200 else 1)"

CMD ["uvicorn", "heart.api:app", "--host", "0.0.0.0", "--port", "8000"]
