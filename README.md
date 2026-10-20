# Heart Disease Risk Prediction - End-to-End MLOps Project

Predicts the presence of heart disease from 13 clinical features (UCI Cleveland data) and serves the
model as a containerised, monitored FastAPI service deployable to Kubernetes.

```
UCI data -> clean + EDA -> sklearn pipelines (nested CV, tuning) -> MLflow tracking
        -> model.joblib + metadata.json -> Docker (FastAPI) -> Kubernetes -> Prometheus/Grafana
GitHub Actions: lint -> unit tests -> train -> docker build + smoke test
```

## 1. Setup (clean machine, Python 3.11)

```bash
git clone <your-repo-url> && cd heart-disease-mlops
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt                       # also installs the local package (-e .)
```

## 2. Data

```bash
python scripts/download_data.py     # downloads processed.cleveland.data and writes data/processed/heart_clean.csv
```
If the download fails (firewall), fetch `processed.cleveland.data` manually from
https://archive.ics.uci.edu/dataset/45/heart+disease and save it as `data/raw/processed.cleveland.data`,
then rerun the script. Cleaning: `?` -> NaN, numeric casting, de-duplication, target binarised (0 = no disease,
1-4 = disease). Imputation happens inside the model pipeline to avoid leakage.

## 3. EDA, training, tracking

```bash
python -m heart.eda                 # figures -> reports/figures/, summary -> reports/eda_summary.txt
python -m heart.train               # 3 models, nested CV, tuning, MLflow logging, writes models/
mlflow ui --backend-store-uri ./mlruns      # http://127.0.0.1:5000
```
Notebook version of the EDA: `notebooks/01_eda.ipynb`. Inference demo: `python scripts/predict_sample.py`.

## 4. Tests and lint

```bash
pytest                              # unit tests (offline, synthetic data)
flake8 src tests scripts
```

## 5. Docker

```bash
docker build -t heart-disease-api:1.0.0 .         # requires models/model.joblib (step 3)
docker run --rm -p 8000:8000 heart-disease-api:1.0.0
bash scripts/smoke_test.sh http://localhost:8000
```
Manual call:
```bash
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{
  "age":63,"sex":1,"cp":1,"trestbps":145,"chol":233,"fbs":1,"restecg":2,
  "thalach":150,"exang":0,"oldpeak":2.3,"slope":3,"ca":0,"thal":6}'
```
Response: `{"prediction":1,"label":"disease","probability_disease":0.87,"confidence":0.87,"model_version":"..."}`
Interactive docs: http://localhost:8000/docs . Other endpoints: `/health`, `/model-info`, `/metrics`.

## 6. Kubernetes (Docker Desktop or Minikube)

```bash
# Minikube only: build inside the cluster's Docker daemon
minikube start
eval $(minikube docker-env)             # PowerShell: & minikube -p minikube docker-env | Invoke-Expression
docker build -t heart-disease-api:1.0.0 .

kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml
kubectl get pods,svc
minikube tunnel                          # separate terminal; Docker Desktop serves on localhost directly
curl http://<EXTERNAL-IP>/health
kubectl logs -l app=heart-disease-api --tail=20
```
Optional: `k8s/ingress.yaml` (nginx ingress) and `k8s/hpa.yaml` (autoscaling, needs metrics-server).

## 7. Monitoring

```bash
docker compose up --build               # API :8000, Prometheus :9090, Grafana :3000 (admin/admin)
python scripts/load_test.py --requests 300
```
Open Grafana -> dashboard "Heart Disease API" (request rate, p95 latency, predictions by class, 5xx).
Every request is also logged as one JSON line (request id, path, status, latency); only the model output is logged,
never the patient inputs.

## 8. CI/CD

`.github/workflows/ci.yml` runs on every push/PR: **lint -> test -> train -> docker**. Any failure stops the pipeline
and the logs show the failing step. Test reports, MLflow runs, trained model and figures are uploaded as artifacts.

## Repository layout

```
src/heart/      config, data, features, modeling, plots, eda, train, api
scripts/        download_data, predict_sample, load_test, smoke_test, make_architecture
tests/          pytest unit tests (data, features, model, API)
k8s/            deployment, service, ingress, hpa
monitoring/     prometheus.yml, Grafana provisioning + dashboard
docs/           architecture.png, report
screenshots/    evidence for the report (checklist inside)
```

## References
- Detrano R. et al. (1989). International application of a new probability algorithm for the diagnosis of
  coronary artery disease. *American Journal of Cardiology*, 64(5), 304-310.
- Janosi A., Steinbrunn W., Pfisterer M., Detrano R. Heart Disease [Dataset]. UCI Machine Learning Repository.
- Pedregosa F. et al. (2011). Scikit-learn: Machine learning in Python. *JMLR*, 12, 2825-2830.
- Zaharia M. et al. (2018). Accelerating the machine learning lifecycle with MLflow. *IEEE Data Eng. Bull.*, 41(4), 39-45.

*Educational project. The model is not a medical device and must not be used for clinical decisions.*
