"""Send random /predict traffic so the Grafana dashboard has data to show."""
import argparse
import json
import random
import time
import urllib.error
import urllib.request


def random_patient() -> dict:
    return {
        "age": random.randint(30, 75), "sex": random.randint(0, 1),
        "cp": random.randint(1, 4), "trestbps": random.randint(95, 190),
        "chol": random.randint(150, 400), "fbs": random.randint(0, 1),
        "restecg": random.randint(0, 2), "thalach": random.randint(90, 195),
        "exang": random.randint(0, 1), "oldpeak": round(random.uniform(0, 4), 1),
        "slope": random.randint(1, 3), "ca": random.randint(0, 3),
        "thal": random.choice([3, 6, 7]),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url", default="http://localhost:8000")
    p.add_argument("--requests", type=int, default=200)
    p.add_argument("--delay", type=float, default=0.05)
    args = p.parse_args()
    ok = 0
    for i in range(args.requests):
        body = random_patient()
        if i % 25 == 24:          # an occasional invalid request shows up as 422
            body["age"] = -1
        req = urllib.request.Request(
            args.url + "/predict", data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"})
        try:
            urllib.request.urlopen(req, timeout=10)
            ok += 1
        except urllib.error.HTTPError:
            pass
        time.sleep(args.delay)
    print(f"sent {args.requests} requests, {ok} succeeded")


if __name__ == "__main__":
    main()
