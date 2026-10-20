"""Inference demo: score one patient locally (joblib) or through the API."""
import argparse
import json
import urllib.request

import pandas as pd

from heart import config

SAMPLE = {
    "age": 63, "sex": 1, "cp": 1, "trestbps": 145, "chol": 233, "fbs": 1,
    "restecg": 2, "thalach": 150, "exang": 0, "oldpeak": 2.3, "slope": 3,
    "ca": 0, "thal": 6,
}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url", help="API base URL, e.g. http://localhost:8000")
    args = p.parse_args()
    if args.url:
        req = urllib.request.Request(
            args.url.rstrip("/") + "/predict", data=json.dumps(SAMPLE).encode(),
            headers={"Content-Type": "application/json"})
        print(urllib.request.urlopen(req, timeout=10).read().decode())
    else:
        import joblib
        model = joblib.load(config.MODEL_PATH)
        row = pd.DataFrame([SAMPLE])[config.FEATURES].astype(float)
        print("P(disease) =", round(float(model.predict_proba(row)[0, 1]), 4))


if __name__ == "__main__":
    main()
