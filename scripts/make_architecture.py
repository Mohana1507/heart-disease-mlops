"""Draw the architecture diagram used in the report (docs/architecture.png)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "docs" / "architecture.png"

BOXES = {
    "uci": (0.2, 3.2, "UCI repository\n(Cleveland data)", "#e8eef9"),
    "data": (2.4, 3.2, "Data prep + EDA\n(clean, split)", "#e8eef9"),
    "train": (4.6, 3.2, "Training\nsklearn pipelines\nnested CV + tuning", "#e8eef9"),
    "mlflow": (4.6, 1.6, "MLflow tracking\nparams / metrics /\nplots / models", "#fdf0d5"),
    "model": (6.8, 3.2, "Packaged model\nmodel.joblib +\nmetadata.json", "#e8eef9"),
    "git": (0.2, 0.0, "GitHub repo", "#eeeeee"),
    "ci": (2.4, 0.0, "GitHub Actions\nlint > test > train", "#eeeeee"),
    "docker": (4.6, 0.0, "Docker image\n(FastAPI + model)", "#e3f4e8"),
    "k8s": (6.8, 0.0, "Kubernetes\n2 pods + LoadBalancer", "#e3f4e8"),
    "prom": (6.8, 1.6, "Prometheus\n+ Grafana", "#fbe3e3"),
    "client": (9.0, 0.0, "Client\nPOST /predict", "#ffffff"),
}
ARROWS = [("uci", "data"), ("data", "train"), ("train", "mlflow"), ("train", "model"),
          ("git", "ci"), ("ci", "train"), ("model", "docker"), ("ci", "docker"),
          ("docker", "k8s"), ("k8s", "prom"), ("client", "k8s")]
W, H = 1.9, 1.1


def centre(key):
    x, y, *_ = BOXES[key]
    return x + W / 2, y + H / 2


def edge_point(src, dst, gap=0.06):
    """Point where the line src->dst leaves src's box (plus a small gap)."""
    (x1, y1), (x2, y2) = centre(src), centre(dst)
    dx, dy = x2 - x1, y2 - y1
    t = min((W / 2) / abs(dx) if dx else float("inf"),
            (H / 2) / abs(dy) if dy else float("inf"))
    length = (dx ** 2 + dy ** 2) ** 0.5
    t += gap / length
    return x1 + dx * t, y1 + dy * t


def main() -> None:
    fig, ax = plt.subplots(figsize=(12, 5.2))
    for x, y, text, colour in BOXES.values():
        ax.add_patch(FancyBboxPatch((x, y), W, H, boxstyle="round,pad=0.03",
                                    fc=colour, ec="#333333", lw=1.2))
        ax.text(x + W / 2, y + H / 2, text, ha="center", va="center", fontsize=8.5)
    for a, b in ARROWS:
        ax.add_patch(FancyArrowPatch(edge_point(a, b), edge_point(b, a),
                                     arrowstyle="-|>", mutation_scale=12, lw=1.2,
                                     color="#444444", shrinkA=0, shrinkB=0))
    ax.set_xlim(-0.2, 11.2)
    ax.set_ylim(-0.3, 4.6)
    ax.axis("off")
    ax.set_title("Heart disease MLOps pipeline - architecture", fontsize=12)
    OUT.parent.mkdir(exist_ok=True)
    fig.savefig(OUT, dpi=170, bbox_inches="tight")


if __name__ == "__main__":
    main()
