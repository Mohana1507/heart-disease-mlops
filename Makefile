.PHONY: install data eda train test lint docker-build docker-run smoke k8s-up k8s-down
install:      ; pip install -r requirements.txt
data:         ; python scripts/download_data.py
eda:          ; python -m heart.eda
train:        ; python -m heart.train
test:         ; pytest
lint:         ; flake8 src tests scripts
docker-build: ; docker build -t heart-disease-api:1.0.0 .
docker-run:   ; docker run --rm -p 8000:8000 heart-disease-api:1.0.0
smoke:        ; bash scripts/smoke_test.sh http://localhost:8000
k8s-up:       ; kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml
k8s-down:     ; kubectl delete -f k8s/deployment.yaml -f k8s/service.yaml
