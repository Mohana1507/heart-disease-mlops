"""Lightweight script to launch MLflow UI cleanly on Windows without memory overhead."""
import os
from pathlib import Path
from mlflow.server import app
import waitress

if __name__ == "__main__":
    os.environ["MLFLOW_BACKEND_STORE_URI"] = str(Path("mlruns").resolve())
    print("Serving MLflow UI on http://127.0.0.1:5000 ...")
    waitress.serve(app, host="127.0.0.1", port=5000, threads=4)
