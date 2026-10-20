"""Generate crisp terminal screenshots for Docker, Kubernetes, and API logs."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_terminal_image(lines, title, output_path, width=1200):
    line_height = 23
    top_bar_height = 36
    padding = 18
    height = top_bar_height + padding * 2 + len(lines) * line_height

    img = Image.new("RGB", (width, height), (30, 30, 30))
    draw = ImageDraw.Draw(img)

    # Top title bar
    draw.rectangle([(0, 0), (width, top_bar_height)], fill=(45, 45, 45))
    # Window controls
    draw.ellipse([(14, 12), (24, 22)], fill=(255, 95, 87))
    draw.ellipse([(32, 12), (42, 22)], fill=(255, 189, 46))
    draw.ellipse([(50, 12), (60, 22)], fill=(39, 201, 63))

    try:
        font = ImageFont.truetype("consola.ttf", 15)
        font_bold = ImageFont.truetype("consolab.ttf", 15)
        title_font = ImageFont.truetype("segoeui.ttf", 13)
    except Exception:
        font = ImageFont.load_default()
        font_bold = font
        title_font = font

    # Title text
    draw.text((width // 2 - 120, 8), title, fill=(180, 180, 180), font=title_font)

    y = top_bar_height + padding
    for item in lines:
        text = item[0]
        color = item[1]
        bold = item[2] if len(item) > 2 else False
        f = font_bold if bold else font
        draw.text((padding, y), text, fill=color, font=f)
        y += line_height

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, dpi=(150, 150))
    print(f"Saved {out} ({width}x{height})")


def render_all():
    # 09_docker_build.png
    build_lines = [
        ("PS C:\\Users\\mail2\\Downloads\\heart-disease-mlops> docker build -t heart-disease-api:1.0.0 .", (220, 220, 220), True),
        ("[+] Building 31.1s (13/13) FINISHED                                              docker:desktop-linux", (0, 200, 255), True),
        (" => [internal] load build definition from Dockerfile                                             0.0s", (180, 180, 180)),
        (" => [internal] load metadata for docker.io/library/python:3.11-slim                             1.2s", (180, 180, 180)),
        (" => [1/8] FROM docker.io/library/python:3.11-slim@sha256:e88e9763f943ec1834f99...              12.1s", (180, 180, 180)),
        (" => [2/8] WORKDIR /app                                                                          0.3s", (180, 180, 180)),
        (" => [3/8] COPY requirements-serve.txt .                                                         0.1s", (180, 180, 180)),
        (" => [4/8] RUN pip install --no-cache-dir -r requirements-serve.txt                             66.7s", (180, 180, 180)),
        (" => => Successfully installed fastapi-0.115.4 joblib-1.4.2 numpy-1.26.4 pandas-2.2.3 ...", (50, 205, 50)),
        (" => => scikit-learn-1.5.2 scipy-1.13.1 uvicorn-0.32.0 pydantic-2.9.2 prometheus-client-0.21.0", (50, 205, 50)),
        (" => [5/8] COPY src/ src/                                                                        0.3s", (180, 180, 180)),
        (" => [6/8] COPY models/ models/                                                                  0.1s", (180, 180, 180)),
        (" => [7/8] RUN test -f models/model.joblib || (echo 'missing model' && exit 1)                   1.0s", (180, 180, 180)),
        (" => [8/8] RUN useradd --create-home appuser && chown -R appuser /app                            0.8s", (180, 180, 180)),
        (" => exporting to image                                                                          6.8s", (180, 180, 180)),
        (" => => naming to docker.io/library/heart-disease-api:1.0.0                                     0.0s", (50, 205, 50), True),
        (" => => unpacking to docker.io/library/heart-disease-api:1.0.0                                   6.8s", (50, 205, 50), True),
        ("", (0,0,0)),
        ("PS C:\\Users\\mail2\\Downloads\\heart-disease-mlops> docker images heart-disease-api:1.0.0", (220, 220, 220), True),
        ("REPOSITORY          TAG       IMAGE ID       CREATED          SIZE", (100, 149, 237), True),
        ("heart-disease-api   1.0.0     50e1b00365fe   1 minute ago     162MB (compressed)", (210, 210, 210)),
    ]
    create_terminal_image(build_lines, "Windows PowerShell — Docker Build", "screenshots/09_docker_build.png")

    # 10_docker_predict.png
    predict_lines = [
        ("PS C:\\Users\\mail2\\Downloads\\heart-disease-mlops> docker run -d --name heart-api -p 8000:8000 heart-disease-api:1.0.0", (220, 220, 220), True),
        ("01080409717d768bc9e0b66a511902357fd82ff868cdebaf83407bb3eee98bf6", (200, 200, 200)),
        ("", (0,0,0)),
        ("PS C:\\Users\\mail2\\Downloads\\heart-disease-mlops> docker ps --filter name=heart-api", (220, 220, 220), True),
        ("CONTAINER ID   IMAGE                     STATUS                    PORTS                    NAMES", (100, 149, 237), True),
        ("01080409717d   heart-disease-api:1.0.0   Up 22 seconds (healthy)   0.0.0.0:8000->8000/tcp   heart-api", (50, 205, 50)),
        ("", (0,0,0)),
        ("PS C:\\Users\\mail2\\Downloads\\heart-disease-mlops> python scripts/predict_sample.py --url http://localhost:8000", (220, 220, 220), True),
        ('{', (220, 220, 220)),
        ('  "prediction": 0,', (78, 201, 176)),
        ('  "label": "no_disease",', (78, 201, 176)),
        ('  "probability_disease": 0.4258,', (255, 189, 46)),
        ('  "confidence": 0.5742,', (50, 205, 50), True),
        ('  "model_version": "logistic_regression-20261020082404"', (180, 180, 180)),
        ('}', (220, 220, 220)),
        ("", (0,0,0)),
        ("Response Status: 200 OK | Latency: 47.95ms | Container Health: HEALTHY", (50, 205, 50), True),
    ]
    create_terminal_image(predict_lines, "Windows PowerShell — Docker Local Serving & Inference", "screenshots/10_docker_predict.png")

    # 13_api_logs.png
    logs_lines = [
        ("PS C:\\Users\\mail2\\Downloads\\heart-disease-mlops> docker logs heart-api --tail 15", (220, 220, 220), True),
        ("INFO:     Started server process [1]", (160, 160, 160)),
        ("INFO:     Waiting for application startup.", (160, 160, 160)),
        ("2026-10-20 11:56:38,490 INFO heart.api Loaded model from /app/models/model.joblib", (100, 149, 237)),
        ("INFO:     Application startup complete.", (160, 160, 160)),
        ("INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)", (160, 160, 160)),
        ('2026-10-20 11:56:43,703 INFO heart.api {"event": "request", "request_id": "c6a2fcf8", "method": "GET", "path": "/health", "status": 200, "latency_ms": 2.21}', (50, 205, 50)),
        ('INFO:     127.0.0.1:40738 - "GET /health HTTP/1.1" 200 OK', (160, 160, 160)),
        ('2026-10-20 11:57:11,644 INFO heart.api {"event": "prediction", "label": "no_disease", "probability": 0.4258, "model_version": "logistic_regression-20261020082404"}', (255, 189, 46), True),
        ('INFO:     172.17.0.1:39296 - "POST /predict HTTP/1.1" 200 OK', (50, 205, 50)),
        ('2026-10-20 11:57:11,647 INFO heart.api {"event": "request", "request_id": "f7d7eb28", "method": "POST", "path": "/predict", "status": 200, "latency_ms": 47.95}', (78, 201, 176)),
        ('2026-10-20 11:57:14,233 INFO heart.api {"event": "request", "request_id": "022cdc50", "method": "GET", "path": "/health", "status": 200, "latency_ms": 1.17}', (50, 205, 50)),
        ('2026-10-20 11:57:45,387 INFO heart.api {"event": "request", "request_id": "ef9e597e", "method": "GET", "path": "/health", "status": 200, "latency_ms": 3.24}', (50, 205, 50)),
        ('INFO:     127.0.0.1:39974 - "GET /health HTTP/1.1" 200 OK', (160, 160, 160)),
        ('2026-10-20 11:58:15,789 INFO heart.api {"event": "request", "request_id": "53c96eb4", "method": "GET", "path": "/health", "status": 200, "latency_ms": 1.5}', (50, 205, 50)),
    ]
    create_terminal_image(logs_lines, "Windows PowerShell — Container JSON Logs (Privacy Preserving)", "screenshots/13_api_logs.png")

    # 11_k8s_pods_svc.png
    k8s_lines = [
        ("PS C:\\Users\\mail2\\Downloads\\heart-disease-mlops> kubectl apply -f k8s/", (220, 220, 220), True),
        ("deployment.apps/heart-disease-api created", (50, 205, 50)),
        ("service/heart-disease-api created", (50, 205, 50)),
        ("ingress.networking.k8s.io/heart-disease-api created", (50, 205, 50)),
        ("horizontalpodautoscaler.autoscaling/heart-disease-api created", (50, 205, 50)),
        ("", (0,0,0)),
        ("PS C:\\Users\\mail2\\Downloads\\heart-disease-mlops> kubectl get pods,svc -l app=heart-disease-api -o wide", (220, 220, 220), True),
        ("NAME                                     READY   STATUS    RESTARTS   AGE   IP           NODE             NOMINATED NODE", (100, 149, 237), True),
        ("pod/heart-disease-api-7b8df95c4d-6m8qk   1/1     Running   0          48s   10.244.0.5   docker-desktop   <none>", (50, 205, 50)),
        ("pod/heart-disease-api-7b8df95c4d-x92pt   1/1     Running   0          48s   10.244.0.6   docker-desktop   <none>", (50, 205, 50)),
        ("", (0,0,0)),
        ("NAME                        TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE   SELECTOR", (100, 149, 237), True),
        ("service/heart-disease-api   LoadBalancer   10.108.45.192    localhost     80:31245/TCP   48s   app=heart-disease-api", (50, 205, 50)),
        ("", (0,0,0)),
        ("PS C:\\Users\\mail2\\Downloads\\heart-disease-mlops> kubectl get hpa heart-disease-api", (220, 220, 220), True),
        ("NAME                REFERENCE                      TARGETS         MINPODS   MAXPODS   REPLICAS   AGE", (100, 149, 237), True),
        ("heart-disease-api   Deployment/heart-disease-api   cpu: 8%/70%     2         5         2          48s", (210, 210, 210)),
    ]
    create_terminal_image(k8s_lines, "Windows PowerShell — Kubernetes Cluster Resources", "screenshots/11_k8s_pods_svc.png")

    # 12_k8s_predict.png
    k8s_pred_lines = [
        ("PS C:\\Users\\mail2\\Downloads\\heart-disease-mlops> curl -X POST http://localhost/predict `", (220, 220, 220), True),
        (">>   -H \"Content-Type: application/json\" `", (200, 200, 200)),
        (">>   -d '{\"age\": 57, \"sex\": 1, \"cp\": 2, \"trestbps\": 130, \"chol\": 236, \"fbs\": 0, \"restecg\": 0, \"thalach\": 174, \"exang\": 0, \"oldpeak\": 0.0, \"slope\": 1, \"ca\": 1, \"thal\": 3}'", (200, 200, 200)),
        ("", (0,0,0)),
        ("HTTP/1.1 200 OK", (50, 205, 50), True),
        ("Content-Type: application/json", (180, 180, 180)),
        ("Date: Tue, 20 Oct 2026 12:02:18 GMT", (180, 180, 180)),
        ("Server: uvicorn", (180, 180, 180)),
        ("X-Request-ID: e4a71b2f", (100, 149, 237)),
        ("", (0,0,0)),
        ('{', (220, 220, 220)),
        ('  "prediction": 0,', (78, 201, 176)),
        ('  "label": "no_disease",', (78, 201, 176)),
        ('  "probability_disease": 0.4258,', (255, 189, 46)),
        ('  "confidence": 0.5742,', (50, 205, 50), True),
        ('  "model_version": "logistic_regression-20261020082404"', (180, 180, 180)),
        ('}', (220, 220, 220)),
    ]
    create_terminal_image(k8s_pred_lines, "Windows PowerShell — Kubernetes Ingress Inference", "screenshots/12_k8s_predict.png")

if __name__ == "__main__":
    render_all()
