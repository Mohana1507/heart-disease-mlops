"""Generate the publication-quality, 15-page MLOps Assignment 1 Final Report.

Standardized to the BITS Pilani AIMLCZG523 MLOps Assignment 01 format.
Features comprehensive visual evidence screenshots, exact measured experimental
metrics from MLflow, hyperparameter tuning grids, and production Kubernetes manifests.

Outputs:
  - docs/MLOps_Report.docx (primary)
  - MLOps_Report_Updated.docx (root fallback)
"""
import os
from pathlib import Path

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Inches, Pt, RGBColor


def set_cell_background(cell, fill_hex):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=70, bottom=70, left=110, right=110):
    """Set inner cell padding in twentieths of a point (dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    """Apply clean subtle borders to a table."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def format_table_header(row, col_widths, bg_hex="1B365D"):
    """Format table header row with bold white text on dark navy background."""
    for i, cell in enumerate(row.cells):
        set_cell_background(cell, bg_hex)
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        cell.width = col_widths[i]
        for p in cell.paragraphs:
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
                r.font.size = Pt(8.5)


def format_table_rows(table, col_widths, alternate_bg=True):
    """Format table body cells with clean padding, alternating shading, and crisp font."""
    for r_idx, row in enumerate(table.rows[1:], start=1):
        bg = "F7F9FB" if (r_idx % 2 == 1 and alternate_bg) else "FFFFFF"
        for c_idx, cell in enumerate(row.cells):
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=55, bottom=55, left=100, right=100)
            cell.width = col_widths[c_idx]
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                for r in p.runs:
                    r.font.size = Pt(8.5)
                    r.font.color.rgb = RGBColor(40, 40, 40)


def add_callout_box(doc, title, content_lines, border_color="1B365D", bg_color="F0F4F8"):
    """Create a high-visibility, professional callout panel for commands and metrics."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.8)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=80, bottom=80, left=130, right=130)

    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="20" w:space="0" w:color="{border_color}"/>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

    p0 = cell.paragraphs[0]
    p0.paragraph_format.space_before = Pt(1)
    p0.paragraph_format.space_after = Pt(2)
    r0 = p0.add_run(f"■ {title}")
    r0.font.bold = True
    r0.font.size = Pt(9)
    r0.font.color.rgb = RGBColor(27, 54, 93)

    for line in content_lines:
        p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(line)
        r.font.name = "Consolas"
        r.font.size = Pt(8)
        r.font.color.rgb = RGBColor(30, 30, 30)

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(1)
    p_spacer.paragraph_format.space_after = Pt(2)


def add_heading_with_spacing(doc, text, level):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.keep_with_next = True
    if level == 1:
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(2)
        for r in h.runs:
            r.font.color.rgb = RGBColor(27, 54, 93)
            r.font.size = Pt(13)
            r.font.bold = True
    elif level == 2:
        h.paragraph_format.space_before = Pt(7)
        h.paragraph_format.space_after = Pt(2)
        for r in h.runs:
            r.font.color.rgb = RGBColor(41, 74, 110)
            r.font.size = Pt(10.5)
            r.font.bold = True
    return h


def add_p(doc, text="", bold_prefix=None, space_after=2):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.12
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(27, 54, 93)
    if text:
        r_txt = p.add_run(text)
        r_txt.font.color.rgb = RGBColor(35, 35, 35)
        r_txt.font.size = Pt(9.5)
    return p


def add_bullet_p(doc, bold_prefix, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(1.5)
    p.paragraph_format.line_spacing = 1.12
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(27, 54, 93)
    r_txt = p.add_run(text)
    r_txt.font.color.rgb = RGBColor(35, 35, 35)
    r_txt.font.size = Pt(9.5)
    return p


def add_figure_if_exists(doc, img_path_str, caption, width=Inches(6.4)):
    p = Path(img_path_str)
    if p.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(3)
        p_img.paragraph_format.space_after = Pt(1)
        p_img.add_run().add_picture(str(p), width=width)
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(4)
        r_cap = p_cap.add_run(caption)
        r_cap.font.size = Pt(8)
        r_cap.font.italic = True
        r_cap.font.color.rgb = RGBColor(80, 80, 80)


def add_side_by_side_figures(doc, left_path, right_path, caption, left_w=Inches(3.3), right_w=Inches(3.3)):
    pl = Path(left_path)
    pr = Path(right_path)
    if pl.exists() and pr.exists():
        t = doc.add_table(rows=1, cols=2)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.rows[0].cells[0].width = left_w
        t.rows[0].cells[1].width = right_w
        for c in t.rows[0].cells:
            set_cell_background(c, "FFFFFF")
            set_cell_margins(c, 0, 0, 0, 0)
        p0 = t.rows[0].cells[0].paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p0.add_run().add_picture(str(pl), width=left_w)
        p1 = t.rows[0].cells[1].paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.add_run().add_picture(str(pr), width=right_w)

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(1)
        p_cap.paragraph_format.space_after = Pt(4)
        r_cap = p_cap.add_run(caption)
        r_cap.font.size = Pt(8)
        r_cap.font.italic = True
        r_cap.font.color.rgb = RGBColor(80, 80, 80)


def build_full_report():
    doc = docx.Document()

    # Configure Margins & Page Size (A4)
    sec = doc.sections[0]
    sec.page_width = Inches(8.27)
    sec.page_height = Inches(11.69)
    sec.top_margin = Inches(0.65)
    sec.bottom_margin = Inches(0.65)
    sec.left_margin = Inches(0.7)
    sec.right_margin = Inches(0.7)

    # Configure Header
    header = sec.header
    p_hdr = header.paragraphs[0]
    p_hdr.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_hdr = p_hdr.add_run("Mohanapriya M · 2025AE05482 · AIMLCZG523 MLOps Assignment 01")
    r_hdr.font.size = Pt(8.5)
    r_hdr.font.color.rgb = RGBColor(120, 120, 120)

    # Base Font
    style_normal = doc.styles["Normal"]
    style_normal.font.name = "Calibri"
    style_normal.font.size = Pt(9.5)
    style_normal.font.color.rgb = RGBColor(35, 35, 35)

    # =============================================================
    # PAGE 1: TITLE, METADATA & TABLE OF CONTENTS
    # =============================================================
    p_univ = doc.add_paragraph()
    p_univ.paragraph_format.space_before = Pt(0)
    p_univ.paragraph_format.space_after = Pt(2)
    r_univ = p_univ.add_run("MACHINE LEARNING OPERATIONS (MLOps) · AIMLCZG523")
    r_univ.font.size = Pt(9)
    r_univ.font.bold = True
    r_univ.font.color.rgb = RGBColor(0, 102, 204)

    p_assign = doc.add_paragraph()
    p_assign.paragraph_format.space_before = Pt(0)
    p_assign.paragraph_format.space_after = Pt(12)
    r_assign = p_assign.add_run("Assignment 01 · MLOps Experimental Learning Assignment · Total Marks: 50")
    r_assign.font.size = Pt(8.5)
    r_assign.font.color.rgb = RGBColor(100, 100, 100)

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("Heart Disease Risk Prediction\nEnd-to-End MLOps Pipeline")
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(27, 54, 93)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(16)
    r_sub = p_sub.add_run("Model development, experiment tracking, CI/CD, containerization, Kubernetes deployment and monitoring")
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = RGBColor(70, 70, 70)

    # Metadata Table
    meta_table = doc.add_table(rows=9, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(meta_table, color="B0C4DE", sz="6")
    meta_widths = [Inches(1.8), Inches(5.0)]

    meta_rows = [
        ("Student name", "Mohanapriya M"),
        ("Student ID", "2025AE05482"),
        ("Course", "Machine Learning Operations (MLOps), AIMLCZG523"),
        ("Dataset", "UCI Heart Disease (Cleveland), 303 patients, 13 features"),
        ("Final model", "Logistic Regression (C = 0.1, penalty = l2), CV ROC-AUC 0.9018, test ROC-AUC 0.9665"),
        ("Serving", "FastAPI in Docker, with Docker Compose and Kubernetes (Deployment, Service, HPA, Ingress)"),
        ("Tooling", "scikit-learn, MLflow, pytest, flake8, GitHub Actions, Prometheus, Grafana"),
        ("Repository", "https://github.com/Mohana1507/heart-disease-mlops"),
        ("Date", "20 October 2026")
    ]
    for r_idx, (k, v) in enumerate(meta_rows):
        row = meta_table.rows[r_idx]
        row.cells[0].text = k
        row.cells[1].text = v
        set_cell_background(row.cells[0], "F4F7FA")
        set_cell_background(row.cells[1], "FFFFFF")
        set_cell_margins(row.cells[0], top=40, bottom=40, left=80, right=80)
        set_cell_margins(row.cells[1], top=40, bottom=40, left=80, right=80)
        row.cells[0].width = meta_widths[0]
        row.cells[1].width = meta_widths[1]
        for p in row.cells[0].paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.size = Pt(8.5)
                r.font.color.rgb = RGBColor(27, 54, 93)
        for p in row.cells[1].paragraphs:
            for r in p.runs:
                r.font.size = Pt(8.5)
                r.font.color.rgb = RGBColor(30, 30, 30)

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(14)

    add_heading_with_spacing(doc, "Contents", level=2)
    toc_items = [
        "1. Problem, dataset and solution overview",
        "2. Setup and installation",
        "3. Data acquisition and exploratory data analysis",
        "4. Feature engineering and model development (with Hyperparameter Tuning)",
        "5. Experiment tracking (MLflow)",
        "6. Model packaging and reproducibility",
        "7. CI/CD pipeline and automated testing (pytest & GitHub Actions)",
        "8. Containerization and API (Docker & FastAPI)",
        "9. Production deployment (Kubernetes manifests & LoadBalancer)",
        "10. Monitoring and logging (Prometheus & Grafana)",
        "11. Architecture, deliverables and video demonstration"
    ]
    for item in toc_items:
        p_toc = doc.add_paragraph()
        p_toc.paragraph_format.space_before = Pt(1)
        p_toc.paragraph_format.space_after = Pt(1)
        r = p_toc.add_run(item)
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(40, 40, 40)

    doc.add_page_break()

    # =============================================================
    # PAGE 2: PROBLEM, DATASET AND SOLUTION OVERVIEW
    # =============================================================
    add_heading_with_spacing(doc, "1. Problem, dataset and solution overview", level=1)
    add_p(doc,
        "Predict whether a patient has coronary heart disease from routine non-invasive clinical diagnostics, "
        "and serve that prediction through a hardened, monitored REST microservice designed for production cloud environments.",
        bold_prefix="Problem Statement: ")

    add_p(doc,
        "The canonical UCI Cleveland Heart Disease benchmark (Janosi et al., 1989; Dua & Graff, 2019) is the primary cohort "
        "in clinical machine learning literature. The dataset contains 303 patient records and 13 clinical predictors alongside the "
        "angiographic disease diagnosis 'num' (0 = absence; 1–4 = presence of coronary artery disease). Under standard clinical AI protocol, "
        "num > 0 is binarized to target = 1.", bold_prefix="Dataset Context: ")

    # Schema Table
    t_schema = doc.add_table(rows=15, cols=3)
    t_schema.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_schema)
    w_sch = [Inches(1.1), Inches(4.3), Inches(1.4)]
    for i, h in enumerate(["Feature", "Clinical Description", "Type"]):
        t_schema.rows[0].cells[i].text = h
    format_table_header(t_schema.rows[0], w_sch)

    schema_data = [
        ("age", "Patient age in years", "numeric"),
        ("sex", "Biological sex (1 = male, 0 = female)", "binary"),
        ("cp", "Chest pain type (1: typical angina, 2: atypical, 3: non-anginal, 4: asymptomatic)", "nominal"),
        ("trestbps", "Resting blood pressure (mm Hg on admission)", "numeric"),
        ("chol", "Serum cholesterol in mg/dl", "numeric"),
        ("fbs", "Fasting blood sugar > 120 mg/dl (1 = true, 0 = false)", "binary"),
        ("restecg", "Resting electrocardiographic findings (0: normal, 1: ST-T wave, 2: LV hypertrophy)", "nominal"),
        ("thalach", "Maximum heart rate achieved during exercise treadmill test", "numeric"),
        ("exang", "Exercise-induced angina (1 = yes, 0 = no)", "binary"),
        ("oldpeak", "ST depression induced by exercise relative to rest (mm)", "numeric"),
        ("slope", "Slope of peak exercise ST segment (1: upsloping, 2: flat, 3: downsloping)", "nominal"),
        ("ca", "Number of major vessels (0–3) colored by fluoroscopy (4 missing codes)", "categorical (count)"),
        ("thal", "Thallium-201 myocardial scintigraphy (3: normal, 6: fixed, 7: reversible defect)", "nominal"),
        ("target (num)", "Angiographic coronary artery disease (0 = healthy, 1 = disease)", "binary target")
    ]
    for r_idx, (f, desc, tp) in enumerate(schema_data, start=1):
        row = t_schema.rows[r_idx]
        row.cells[0].text = f
        row.cells[1].text = desc
        row.cells[2].text = tp
    format_table_rows(t_schema, w_sch)

    add_p(doc, "Key operational components of the engineering lifecycle:", bold_prefix="Solution at a Glance: ")
    add_bullet_p(doc, "Data: ", "scripts/download_data.py downloads UCI data; src/heart/data.py cleans and preserves missing values without data leakage.")
    add_bullet_p(doc, "Modelling: ", "scikit-learn Pipeline (ColumnTransformer + Classifier) evaluated across LR, RF, and GB using 5x3 nested cross-validation.")
    add_bullet_p(doc, "Tracking: ", "MLflow logs hyperparameter grids, cross-validation metrics, test scores, ROC/PR curves, and serialized MLmodel packages.")
    add_bullet_p(doc, "Quality gates: ", "flake8 linting and 21 automated pytest unit tests executed locally and across a 4-stage GitHub Actions CI/CD workflow.")
    add_bullet_p(doc, "Serving: ", "FastAPI /predict microservice packaged in a 162 MB non-root container image, orchestrated via Docker Compose and Kubernetes.")
    add_bullet_p(doc, "Observability: ", "Privacy-conscious JSON access logs (no patient PII), Prometheus telemetry (/metrics), and pre-provisioned Grafana dashboard.")

    add_p(doc, "Table 2 summarizes the unbiased hold-out test set performance across 61 test patients.", bold_prefix="Headline Results (Held-Out Test Set, N = 61): ")

    # Headline Results Table
    t_head = doc.add_table(rows=4, cols=6)
    t_head.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_head)
    w_head = [Inches(2.2), Inches(0.9), Inches(0.9), Inches(0.9), Inches(0.9), Inches(1.0)]
    for i, h in enumerate(["Model", "Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"]):
        t_head.rows[0].cells[i].text = h
    format_table_header(t_head.rows[0], w_head)

    head_data = [
        ("Logistic Regression (Champion)", "0.8852", "0.8387", "0.9286", "0.8814", "0.9665"),
        ("Random Forest", "0.8361", "0.8000", "0.8571", "0.8276", "0.9416"),
        ("Gradient Boosting", "0.9016", "0.8667", "0.9286", "0.8966", "0.9610")
    ]
    for r_idx, r_vals in enumerate(head_data, start=1):
        row = t_head.rows[r_idx]
        for c_idx, v in enumerate(r_vals):
            row.cells[c_idx].text = v
    format_table_rows(t_head, w_head)

    doc.add_page_break()

    # =============================================================
    # PAGE 3: SETUP AND INSTALLATION
    # =============================================================
    add_heading_with_spacing(doc, "2. Setup and installation", level=1)
    add_p(doc, "Prerequisites: Python 3.11/3.12, Docker Desktop, kubectl, Git.")

    add_callout_box(doc, "Repository Layout Hierarchy (https://github.com/Mohana1507/heart-disease-mlops)", [
        "heart-disease-mlops/",
        "├── data/                    # raw/ (UCI download) · processed/heart_clean.csv",
        "├── notebooks/               # 01_eda.ipynb · 02_training.ipynb · 03_inference.ipynb",
        "├── src/heart/               # config · data · eda · features · modeling · train · api",
        "├── tests/                   # 21 pytest unit tests (test_data, test_features, test_model, test_api)",
        "├── models/                  # model.joblib · metadata.json",
        "├── k8s/                     # deployment.yaml · service.yaml · hpa.yaml · ingress.yaml",
        "├── monitoring/              # prometheus.yml · grafana/dashboards/heart-api.json",
        "├── .github/workflows/ci.yml # 4-stage GitHub Actions pipeline (lint, test, train, docker)",
        "├── scripts/                 # download_data.py · load_test.py · predict_sample.py",
        "├── screenshots/             # 14 required visual evidence screenshots",
        "└── Dockerfile · docker-compose.yml · requirements.txt · requirements-serve.txt"
    ])

    add_p(doc, "Step 1: Environment and Training (Clean Setup)", bold_prefix="1. Local Setup: ")
    add_callout_box(doc, "Terminal Execution Commands", [
        "python -m venv .venv",
        ".venv\\Scripts\\activate  # Linux/macOS: source .venv/bin/activate",
        "pip install -r requirements.txt",
        "python scripts/download_data.py  # Download UCI data -> data/raw/",
        "python -m heart.eda              # Export 5 diagnostic figures -> reports/figures/",
        "python -m heart.train            # Run nested CV, log to MLflow, export model.joblib",
        "pytest -v                        # Run 21 automated unit tests",
        "flake8 src tests scripts         # Run PEP 8 static analysis"
    ])

    add_p(doc, "Step 2: Run the Stack in Docker", bold_prefix="2. Docker Compose: ")
    add_callout_box(doc, "Docker Stack Launch Commands", [
        "docker compose up -d --build",
        "python scripts/predict_sample.py --url http://localhost:8000",
        "python scripts/load_test.py --requests 300  # Send synthetic traffic to Grafana"
    ])

    add_p(doc, "Step 3: Deploy to Local Kubernetes", bold_prefix="3. Kubernetes Deployment: ")
    add_callout_box(doc, "Kubernetes Manifest Commands", [
        "kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml -f k8s/hpa.yaml",
        "kubectl get pods,svc -l app=heart-disease-api"
    ])

    add_p(doc, "Table 3 details local endpoints and service ports.", bold_prefix="Access Instructions (Local Cluster & Services): ")

    t_acc = doc.add_table(rows=6, cols=2)
    t_acc.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_acc)
    w_acc = [Inches(2.8), Inches(4.0)]
    for i, h in enumerate(["Endpoint / Service", "URL"]):
        t_acc.rows[0].cells[i].text = h
    format_table_header(t_acc.rows[0], w_acc)

    acc_data = [
        ("API Swagger Interactive Documentation", "http://localhost:8000/docs"),
        ("Direct API Health Check Endpoint", "http://localhost:8000/health"),
        ("Kubernetes LoadBalancer Service", "http://localhost:80/predict  (or port 8000)"),
        ("Prometheus Metrics Exposition", "http://localhost:9090"),
        ("Grafana Production Dashboard", "http://localhost:3000/d/heart-api  (admin/admin)"),
    ]
    for r_idx, (ep, url) in enumerate(acc_data, start=1):
        row = t_acc.rows[r_idx]
        row.cells[0].text = ep
        row.cells[1].text = url
    format_table_rows(t_acc, w_acc)

    doc.add_page_break()

    # =============================================================
    # PAGE 4: DATA ACQUISITION AND EDA
    # =============================================================
    add_heading_with_spacing(doc, "3. Data acquisition and exploratory data analysis", level=1)
    add_p(doc,
        "The automated ingestion script (scripts/download_data.py) retrieves processed.cleveland.data directly from the UCI archive. "
        "Missing values represented by '?' are parsed to IEEE NaN floats. Crucially, zero duplicate records exist in the raw Cleveland data; "
        "all 303 original clinical cases are retained: 164 healthy subjects (54.1%) and 139 heart disease subjects (45.9%). "
        "Six total feature values are missing across the cohort (4 in 'ca', 2 in 'thal'). Missing values are deliberately kept as NaNs "
        "in data/processed/heart_clean.csv to prevent data leakage prior to machine learning pipeline cross-validation.",
        bold_prefix="Acquisition and Cleaning (src/heart/data.py): ")

    add_side_by_side_figures(doc,
        "screenshots/01_eda_class_balance.png",
        "screenshots/02_eda_correlation.png",
        "Fig 1. Class balance: 164 healthy vs 139 disease (close to even, avoiding majority-class bias) | Fig 2. Pearson correlation heatmap across 14 clinical attributes.",
        left_w=Inches(3.3), right_w=Inches(3.3))

    add_figure_if_exists(doc,
        "screenshots/02b_eda_histograms.png",
        "Fig 3. Continuous feature distributions (age, trestbps, chol, thalach, oldpeak) grouped by target diagnosis (0 = healthy, 1 = disease).",
        width=Inches(6.4))

    add_p(doc, "Key statistical and clinical insights derived from exploratory analysis:", bold_prefix="Key Findings: ")
    add_bullet_p(doc, "Maximum Heart Rate (thalach): ", "Exhibits strong negative correlation with disease (r = -0.42). Healthy patients reach a significantly higher median heart rate (158 bpm) than diseased patients (142 bpm), demonstrating chronotropic incompetence.")
    add_bullet_p(doc, "Exercise ST Depression (oldpeak): ", "Positively correlated with coronary disease (r = +0.42). Diseased patients exhibit marked ST depression (median 1.4 mm vs 0.0 mm for healthy subjects).")
    add_bullet_p(doc, "Chest Pain Presentation (cp): ", "Asymptomatic presentation (cp = 4) exhibits the highest disease incidence (>72%), demonstrating that advanced coronary obstruction frequently manifests insidiously.")
    add_bullet_p(doc, "Discrete Feature Codings: ", "cp, restecg, slope, ca, and thal are discrete categorical codes; they are one-hot encoded inside the pipeline rather than treated as ordinal numbers.")

    doc.add_page_break()

    # =============================================================
    # PAGE 5: FEATURE ENGINEERING & MODEL SELECTION / TUNING
    # =============================================================
    add_figure_if_exists(doc,
        "screenshots/02c_eda_boxplots.png",
        "Fig 4. Clinical feature boxplots partitioned by target diagnosis. Significant median separation is observed in thalach, oldpeak, and age.",
        width=Inches(6.4))

    add_heading_with_spacing(doc, "4. Feature Engineering and Model Development", level=1)
    add_p(doc,
        "To guarantee reproducibility and eliminate train-serving skew, all transformations are encapsulated in a single scikit-learn "
        "ColumnTransformer (src/heart/features.py). Following src/heart/config.py, 'ca' is categorized with nominal features:",
        bold_prefix="Preprocessing Architecture (src/heart/features.py): ")

    # Preprocessing Table
    t_prep = doc.add_table(rows=3, cols=3)
    t_prep.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_prep)
    w_pr = [Inches(1.2), Inches(2.6), Inches(3.0)]
    for i, h in enumerate(["Group", "Columns", "Pipeline Transformation Steps"]):
        t_prep.rows[0].cells[i].text = h
    format_table_header(t_prep.rows[0], w_pr)

    prep_data = [
        ("Numeric", "age, trestbps, chol, thalach, oldpeak", "SimpleImputer(strategy='median') → StandardScaler()"),
        ("Categorical", "sex, cp, fbs, restecg, exang, slope, ca, thal", "SimpleImputer(strategy='most_frequent') → OneHotEncoder(handle_unknown='ignore')")
    ]
    for r_idx, (g, cols, st) in enumerate(prep_data, start=1):
        row = t_prep.rows[r_idx]
        row.cells[0].text = g
        row.cells[1].text = cols
        row.cells[2].text = st
    format_table_rows(t_prep, w_pr)

    add_p(doc,
        "The dataset is partitioned into an 80% training set (N = 242) and a 20% hold-out test set (N = 61) with stratification (seed 42). "
        "Hyperparameter optimization is performed via GridSearchCV inside 5-fold StratifiedKFold cross-validation optimizing ROC-AUC.",
        bold_prefix="Model Selection and Hyperparameter Tuning (src/heart/modeling.py): ")

    # Grid Search Table
    t_grid = doc.add_table(rows=4, cols=3)
    t_grid.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_grid)
    w_gr = [Inches(1.8), Inches(2.8), Inches(2.2)]
    for i, h in enumerate(["Candidate Model", "Hyperparameter Search Grid", "Optimal Hyperparameters Selected"]):
        t_grid.rows[0].cells[i].text = h
    format_table_header(t_grid.rows[0], w_gr)

    grid_data = [
        ("Logistic Regression", "C ∈ {0.01, 0.1, 1.0, 10.0}\npenalty ∈ {'l1', 'l2'}", "C = 0.1, penalty = 'l2'"),
        ("Random Forest", "n_estimators ∈ {100, 300}\nmax_depth ∈ {3, 6, None}\nmin_samples_leaf ∈ {1, 3, 5}", "n_estimators = 100, max_depth = None,\nmin_samples_leaf = 5"),
        ("Gradient Boosting", "n_estimators ∈ {100, 200}\nlearning_rate ∈ {0.05, 0.1}\nmax_depth ∈ {2, 3}", "n_estimators = 100, learning_rate = 0.05,\nmax_depth = 2")
    ]
    for r_idx, (m, gr, bst) in enumerate(grid_data, start=1):
        row = t_grid.rows[r_idx]
        row.cells[0].text = m
        row.cells[1].text = gr
        row.cells[2].text = bst
    format_table_rows(t_grid, w_gr)

    doc.add_page_break()

    # =============================================================
    # PAGE 6: MODEL EVALUATION & COMPARISON
    # =============================================================
    add_heading_with_spacing(doc, "Evaluation", level=2)
    add_p(doc, "Evaluation across 5-fold cross-validation and unbiased 61-patient hold-out test set (measured MLflow values):")

    # Complete Evaluation Table matching MLflow exactly
    t_eval = doc.add_table(rows=4, cols=8)
    t_eval.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_eval)
    w_ev = [Inches(1.6), Inches(0.75), Inches(0.75), Inches(0.75), Inches(0.75), Inches(1.0), Inches(0.75), Inches(0.95)]
    for i, h in enumerate(["Model", "CV Acc", "CV Prec", "CV Rec", "CV F1", "CV ROC-AUC", "Test Acc", "Test ROC-AUC"]):
        t_eval.rows[0].cells[i].text = h
    format_table_header(t_eval.rows[0], w_ev)

    eval_data = [
        ("Logistic Regression (Selected)", "0.8305", "0.8594", "0.7652", "0.8054", "0.9018 ± 0.0156", "0.8852", "0.9665"),
        ("Random Forest", "0.8096", "0.8152", "0.7644", "0.7838", "0.8914 ± 0.0316", "0.8361", "0.9416"),
        ("Gradient Boosting", "0.8016", "0.7900", "0.7830", "0.7818", "0.8744 ± 0.0249", "0.9016", "0.9610")
    ]
    for r_idx, r_vals in enumerate(eval_data, start=1):
        row = t_eval.rows[r_idx]
        for c_idx, val in enumerate(r_vals):
            row.cells[c_idx].text = val
    format_table_rows(t_eval, w_ev)

    add_side_by_side_figures(doc,
        "screenshots/logistic_regression_roc.png",
        "screenshots/logistic_regression_confusion_matrix.png",
        "Fig 5. Champion Logistic Regression ROC curve (Test AUC = 0.9665) | Fig 6. Hold-out test Confusion Matrix on 61 patients (26 TP, 28 TN, 5 FP, 2 FN).",
        left_w=Inches(3.3), right_w=Inches(3.3))

    add_figure_if_exists(doc,
        "screenshots/model_comparison.png",
        "Fig 7. Algorithmic comparison of nested cross-validation ROC-AUC scores across candidate model families.",
        width=Inches(5.0))

    add_p(doc,
        "L2-regularized Logistic Regression achieved the highest cross-validated discrimination (mean ROC-AUC of 0.9018) "
        "and demonstrated lower estimation variance across folds (std = 0.0156 vs 0.0316 for Random Forest). "
        "On the independent 61-patient test cohort, Logistic Regression achieved 88.52% Accuracy, 92.86% Recall (catching 26 of 28 "
        "diseased patients with only 2 false negatives), and a test ROC-AUC of 0.9665. Furthermore, linear model coefficients provide "
        "direct interpretability essential for clinical decision-support systems.", bold_prefix="Why Logistic Regression: ")

    doc.add_page_break()

    # =============================================================
    # PAGE 7: EXPERIMENT TRACKING (MLFLOW)
    # =============================================================
    add_heading_with_spacing(doc, "5. Experiment tracking", level=1)
    add_p(doc,
        "MLflow Tracking (local store ./mlruns, experiment namespace 'heart-disease-risk') records every training run:",
        bold_prefix="MLflow Tracking Server Architecture: ")
    add_bullet_p(doc, "Parameters: ", "Model type, random seed (42), test split (0.2), outer folds (5), inner folds (3), best hyperparameters (best_clf__C, best_clf__penalty).")
    add_bullet_p(doc, "Metrics: ", "Mean and standard deviation for 5 cross-validation metrics (accuracy, precision, recall, F1, ROC-AUC) plus hold-out test metrics.")
    add_bullet_p(doc, "Artifacts: ", "ROC curve and confusion matrix plots, serialized Pipeline model, Conda environment descriptor (conda.yaml), and MLmodel signature.")

    add_figure_if_exists(doc,
        "screenshots/03_mlflow_runs.png",
        "Fig 8. MLflow experiment dashboard showing tracked candidate runs (logistic_regression, random_forest, gradient_boosting, final_model_selection).",
        width=Inches(6.4))

    add_figure_if_exists(doc,
        "screenshots/04_mlflow_run_detail.png",
        "Fig 9. MLflow run detail view: Logged parameters (10) and cross-validation/test metrics (16) for champion Logistic Regression.",
        width=Inches(6.4))

    add_figure_if_exists(doc,
        "screenshots/04b_mlflow_artifacts.png",
        "Fig 10. MLflow Artifacts browser: Packaged model directory, MLmodel descriptor, conda.yaml, and exported diagnostic plots.",
        width=Inches(6.0))

    doc.add_page_break()

    # =============================================================
    # PAGE 8: MODEL PACKAGING & TESTING (PYTEST)
    # =============================================================
    add_heading_with_spacing(doc, "6. Model packaging and reproducibility", level=1)
    add_bullet_p(doc, "Format: ", "The fitted Pipeline (preprocessing + classifier) is serialized to models/model.joblib and logged as an MLflow model.")
    add_bullet_p(doc, "Metadata: ", "models/metadata.json stores the selected model architecture, optimal hyperparameters, Git commit SHA, feature ordering, and validation metrics.")
    add_bullet_p(doc, "Environment: ", "Strict dependency pinning in requirements.txt (development) and requirements-serve.txt (runtime).")
    add_bullet_p(doc, "Determinism: ", "RANDOM_STATE = 42 is enforced across splits, folds, and estimators, verified by unit test test_training_is_reproducible.")
    add_bullet_p(doc, "Unified Code Path: ", "Serving microservice calls the identical pipeline transform; train-serving skew is eliminated by construction.")

    add_heading_with_spacing(doc, "7. CI/CD pipeline and automated testing", level=1)
    add_p(doc, "The automated test suite comprises 21 offline unit tests executed via pytest:", bold_prefix="Unit Tests (tests/, 21 tests): ")

    # Unit Tests Table
    t_test = doc.add_table(rows=5, cols=2)
    t_test.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_test)
    w_tst = [Inches(1.8), Inches(5.0)]
    for i, h in enumerate(["Test Module", "Verification Scope"]):
        t_test.rows[0].cells[i].text = h
    format_table_header(t_test.rows[0], w_tst)

    test_data = [
        ("tests/test_data.py", "Parses question marks to NaN, removes duplicates, validates target binarization, rejects invalid schemas."),
        ("tests/test_features.py", "Ensures ColumnTransformer outputs non-null arrays, standardizes numeric columns, gracefully handles unseen categories."),
        ("tests/test_model.py", "Confirms candidate model architectures, validates metric bounds, enforces reproducibility, runs end-to-end training."),
        ("tests/test_api.py", "Tests /health, verifies /predict returns predictions and confidence, tolerates missing optional fields, rejects invalid values with 422.")
    ]
    for r_idx, (f, v) in enumerate(test_data, start=1):
        row = t_test.rows[r_idx]
        row.cells[0].text = f
        row.cells[1].text = v
    format_table_rows(t_test, w_tst)

    add_figure_if_exists(doc,
        "screenshots/05_pytest_pass.png",
        "Fig 11. Terminal output showing all 21 pytest unit tests passing with 100% success rate in 40.24 seconds.",
        width=Inches(6.4))

    doc.add_page_break()

    # =============================================================
    # PAGE 9: CI/CD PIPELINE & FAIL-FAST PROOF
    # =============================================================
    add_heading_with_spacing(doc, "GitHub Actions (.github/workflows/ci.yml)", level=2)
    add_p(doc,
        "Continuous integration triggers on push to main, pull requests, and manual triggers. It enforces four sequential jobs: "
        "Job 1 (lint): flake8 style conformance; Job 2 (test): installs dependencies, runs 21 pytest tests with coverage; "
        "Job 3 (train): runs download, EDA, nested CV model training, and uploads artifacts; Job 4 (docker): builds the serving image and runs smoke tests. "
        "Any failure in an upstream job halts the pipeline immediately (fail-fast).")

    add_figure_if_exists(doc,
        "screenshots/08_actions_failure.png",
        "Fig 12. Fail-fast demonstration: An intentional PEP 8 lint error halts the GitHub Actions pipeline at Job 1, preventing defective code from reaching deployment.",
        width=Inches(6.4))

    add_figure_if_exists(doc,
        "screenshots/08b_workflow_history.png",
        "Fig 13. GitHub Actions workflow history: Illustrating fail-fast termination on run #1 (red) followed by resolution on run #2 (green).",
        width=Inches(6.4))

    doc.add_page_break()

    # =============================================================
    # PAGE 10: GITHUB ACTIONS EXECUTION RUNS
    # =============================================================
    add_heading_with_spacing(doc, "GitHub Actions Workflow Execution", level=2)

    add_figure_if_exists(doc,
        "screenshots/06_actions_run.png",
        "Fig 14. Successful GitHub Actions workflow execution: All four jobs (lint, test, train, docker) completed green in 4m 24s.",
        width=Inches(6.4))

    add_figure_if_exists(doc,
        "screenshots/07_actions_artifacts.png",
        "Fig 15. Uploaded build artifacts from CI pipeline: test-reports (JUnit XML), model (model.joblib, metadata.json), mlruns (tracking database), and figures.",
        width=Inches(6.4))

    add_figure_if_exists(doc,
        "screenshots/06b_checks_passed.png",
        "Fig 16. GitHub repository commit verification: All automated branch checks passing on origin/main.",
        width=Inches(6.4))

    doc.add_page_break()

    # =============================================================
    # PAGE 11: CONTAINERIZATION AND REST API
    # =============================================================
    add_heading_with_spacing(doc, "8. Containerization and API", level=1)
    add_bullet_p(doc, "Image: ", "python:3.11-slim base, runtime dependencies only, non-root appuser execution, container HEALTHCHECK probing /health every 30s.")
    add_bullet_p(doc, "Endpoints: ", "POST /predict (JSON in, prediction and confidence out), GET /health, GET /model-info, GET /metrics, /docs (Swagger UI).")
    add_bullet_p(doc, "Validation: ", "Pydantic schema enforcing clinical ranges on all 13 features; invalid payloads trigger HTTP 422 with descriptive error details.")
    add_bullet_p(doc, "Tracing: ", "Each request is tagged with an X-Request-ID header for end-to-end operational traceability.")

    add_callout_box(doc, "Sample POST /predict Request and Response Payload", [
        'POST /predict',
        '{"age": 57, "sex": 1, "cp": 2, "trestbps": 130, "chol": 236, "fbs": 0, "restecg": 0,',
        ' "thalach": 174, "exang": 0, "oldpeak": 0.0, "slope": 1, "ca": 1, "thal": 3}',
        '',
        '# Response (HTTP 200 OK):',
        '{"prediction": 0, "label": "no_disease", "probability_disease": 0.4258,',
        ' "confidence": 0.5742, "model_version": "logistic_regression-20261020082404"}'
    ])

    add_figure_if_exists(doc,
        "screenshots/09_docker_build.png",
        "Fig 17. Docker build execution: Single-stage production container build producing lightweight 162 MB image with non-root security hardening.",
        width=Inches(6.4))

    add_figure_if_exists(doc,
        "screenshots/10_docker_predict.png",
        "Fig 18. Local container serving proof: Container running healthy on port 8000 and returning real-time inference prediction.",
        width=Inches(6.4))

    doc.add_page_break()

    # =============================================================
    # PAGE 12: CONTAINER LOGS & OBSERVABILITY TELEMETRY
    # =============================================================
    add_heading_with_spacing(doc, "Structured Logging and Privacy Enforcement", level=2)
    add_p(doc,
        "An asynchronous middleware intercepts all HTTP traffic. For every incoming request, it mints a UUID request ID, "
        "measures latency via time.perf_counter(), and emits a single-line JSON log. Crucially, raw clinical measurements are strictly "
        "omitted from logs to uphold patient data privacy; only the high-level prediction class and confidence are recorded.")

    add_figure_if_exists(doc,
        "screenshots/13_api_logs.png",
        "Fig 19. Container access logs displaying privacy-conscious structured JSON telemetry (request ID, method, path, HTTP status, and latency).",
        width=Inches(6.4))

    add_callout_box(doc, "Structured JSON Access Log Excerpt", [
        'INFO: 2026-10-20 11:56:38,490 Loaded model from /app/models/model.joblib',
        'INFO: {"event": "request", "request_id": "c6a2fcf8", "method": "GET", "path": "/health", "status": 200, "latency_ms": 2.21}',
        'INFO: {"event": "prediction", "label": "no_disease", "probability": 0.4258, "model_version": "logistic_regression-20261020082404"}',
        'INFO: {"event": "request", "request_id": "f7d7eb28", "method": "POST", "path": "/predict", "status": 200, "latency_ms": 47.95}'
    ])

    doc.add_page_break()

    # =============================================================
    # PAGE 13: PRODUCTION DEPLOYMENT (KUBERNETES)
    # =============================================================
    add_heading_with_spacing(doc, "9. Production deployment (Kubernetes)", level=1)
    add_p(doc,
        "Declarative Kubernetes manifests (k8s/) support scalable production deployment across local clusters (Docker Desktop Kubernetes, "
        "Minikube) and managed cloud platforms (GKE, EKS, AKS):",
        bold_prefix="9.1 Kubernetes Architecture and Manifests: ")

    # K8s Manifests Table
    t_k8s = doc.add_table(rows=5, cols=3)
    t_k8s.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_k8s)
    w_k = [Inches(1.8), Inches(1.8), Inches(3.2)]
    for i, h in enumerate(["Manifest File", "Resource Kind", "Configuration Details"]):
        t_k8s.rows[0].cells[i].text = h
    format_table_header(t_k8s.rows[0], w_k)

    k8s_data = [
        ("k8s/deployment.yaml", "Deployment", "2 replicas, resources: requests(100m, 256Mi), limits(500m, 512Mi), liveness/readiness probes on /health, Prometheus scrape annotations."),
        ("k8s/service.yaml", "Service", "LoadBalancer service exposing HTTP port 80 and forwarding traffic to container targetPort 8000."),
        ("k8s/ingress.yaml", "Ingress", "NGINX Ingress routing path-based traffic under domain heart.local."),
        ("k8s/hpa.yaml", "HorizontalPodAutoscaler", "Autoscales deployment between 2 and 5 replicas when average CPU exceeds 70%.")
    ]
    for r_idx, (f, knd, cf) in enumerate(k8s_data, start=1):
        row = t_k8s.rows[r_idx]
        row.cells[0].text = f
        row.cells[1].text = knd
        row.cells[2].text = cf
    format_table_rows(t_k8s, w_k)

    add_heading_with_spacing(doc, "9.2 Deployed API Access and Invocation", level=2)
    add_bullet_p(doc, "Cluster Host & Port: ", "http://localhost:80 (LoadBalancer Service) or http://localhost:8000 (direct).")
    add_bullet_p(doc, "Health Verification Endpoint: ", "GET http://localhost/health (returns HTTP 200: {\"status\": \"ok\", \"model_loaded\": true}).")
    add_bullet_p(doc, "Inference Endpoint: ", "POST http://localhost/predict (accepts JSON PatientFeatures, returns prediction payload).")

    add_figure_if_exists(doc,
        "screenshots/11_k8s_pods_svc.png",
        "Fig 20. Kubernetes cluster resources: 2 active pods (heart-disease-api-7b8df95c4d-6m8qk, x92pt), LoadBalancer Service (10.108.45.192:80), and HPA.",
        width=Inches(6.4))

    add_figure_if_exists(doc,
        "screenshots/12_k8s_predict.png",
        "Fig 21. Live inference request routed through the Kubernetes LoadBalancer Service on localhost:80 returning 200 OK.",
        width=Inches(6.4))

    doc.add_page_break()

    # =============================================================
    # PAGE 14: MONITORING AND OBSERVABILITY
    # =============================================================
    add_heading_with_spacing(doc, "10. Monitoring and logging", level=1)
    add_bullet_p(doc, "Logging: ", "Structured JSON access logs capturing request ID, HTTP method, path, status, and latency_ms without exposing raw patient PII.")
    add_bullet_p(doc, "Metrics: ", "Prometheus client natively instruments api_requests_total{method,path,status}, api_request_latency_seconds_bucket, and predictions_total{label}.")
    add_bullet_p(doc, "Grafana Dashboard: ", "docker-compose.yml runs the monitoring stack locally. Pre-provisioned dashboard (monitoring/grafana/dashboards/heart-api.json) visualizes real-time operational telemetry.")

    add_figure_if_exists(doc,
        "screenshots/14_grafana_dashboard.png",
        "Fig 22. Real-time Grafana monitoring dashboard: Request rate, p95 latency (<50ms), and prediction distribution (97 no disease vs 191 disease).",
        width=Inches(6.4))

    add_callout_box(doc, "Prometheus Telemetry Excerpt (http://localhost:8000/metrics after 300 requests)", [
        'api_requests_total{method="POST",path="/predict",status="200"} 288.0',
        'api_requests_total{method="POST",path="/predict",status="422"} 12.0',
        'predictions_total{label="no_disease"} 97.0',
        'predictions_total{label="disease"} 191.0',
        'api_request_latency_seconds_bucket{le="0.05",path="/predict"} 298.0'
    ])

    doc.add_page_break()

    # =============================================================
    # PAGE 15: ARCHITECTURE, DELIVERABLES & VIDEO DEMONSTRATION
    # =============================================================
    add_heading_with_spacing(doc, "11. Architecture, deliverables and repository", level=1)

    add_figure_if_exists(doc,
        "docs/architecture.png",
        "Fig 23. End-to-end MLOps pipeline architecture from data ingestion to Kubernetes serving and Grafana monitoring.",
        width=Inches(6.4))

    # Deliverables Checklist Table
    t_deliv = doc.add_table(rows=10, cols=2)
    t_deliv.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_deliv)
    w_dl = [Inches(2.6), Inches(4.2)]
    for i, h in enumerate(["Deliverable Component", "Repository Location"]):
        t_deliv.rows[0].cells[i].text = h
    format_table_header(t_deliv.rows[0], w_dl)

    deliv_data = [
        ("Code, Dockerfile, requirements", "src/heart/, Dockerfile, docker-compose.yml, requirements*.txt"),
        ("Cleaned dataset + download script", "data/processed/heart_clean.csv, scripts/download_data.py"),
        ("Notebooks (EDA, training, inference)", "notebooks/01_eda.ipynb, 02_training.ipynb, 03_inference.ipynb"),
        ("Unit tests suite (21 tests)", "tests/ (test_data.py, test_features.py, test_model.py, test_api.py)"),
        ("CI/CD pipeline workflow", ".github/workflows/ci.yml"),
        ("Kubernetes manifests", "k8s/deployment.yaml, k8s/service.yaml, k8s/hpa.yaml, k8s/ingress.yaml"),
        ("Screenshots suite (14 items)", "screenshots/"),
        ("Technical report", "MLOps_Report.docx, docs/MLOps_Report.docx"),
        ("Access instructions & Video outline", "README.md, Section 2 & Appendix B")
    ]
    for r_idx, (comp, loc) in enumerate(deliv_data, start=1):
        row = t_deliv.rows[r_idx]
        row.cells[0].text = comp
        row.cells[1].text = loc
    format_table_rows(t_deliv, w_dl)

    add_p(doc, "https://github.com/Mohana1507/heart-disease-mlops", bold_prefix="GitHub Repository: ")

    # Highlighted Video Submission Callout Box
    add_callout_box(doc, "PIPELINE DEMONSTRATION VIDEO ACCESS & SUBMISSION LINK", [
        "Video URL: [PASTE_YOUR_VIDEO_LINK_HERE: e.g., https://youtu.be/xxxx or Google Drive link]",
        "",
        "Access Permissions: Set to 'Unlisted' on YouTube or 'Anyone with the link can view' on Google Drive.",
        "Demonstration Duration: Approximately 4 minutes 30 seconds.",
        "Key Demonstrations Covered:",
        "  - 0:00 - 0:45 : Repository structure, modular src/ package, and environment setup.",
        "  - 0:45 - 1:30 : GitHub Actions CI/CD pipeline run with all 4 jobs green (lint, test, train, docker).",
        "  - 1:30 - 2:15 : MLflow Tracking UI demonstrating candidate models, hyperparameter grids, and artifacts.",
        "  - 2:15 - 3:00 : Docker container packaging, non-root user execution, and /predict inference verification.",
        "  - 3:00 - 3:45 : Kubernetes deployment (kubectl apply, 2 ready pods, LoadBalancer Service inference).",
        "  - 3:45 - 4:30 : Real-time Prometheus & Grafana dashboard under active synthetic load test."
    ], border_color="0066CC", bg_color="EBF3FB")

    add_p(doc,
        "Limitations and Next Steps: The Cleveland benchmark reflects a modest sample size (N=303). "
        "Production enhancements should include: (1) automated model registry with canary deployment gates; "
        "(2) Evidently AI data drift detection on streaming clinical distributions; (3) Helm chart packaging for multi-environment cluster promotion.",
        bold_prefix="Limitations and Future Work: ")

    # Save to target locations
    out_root = Path("MLOps_Report.docx")
    out_docs = Path("docs/MLOps_Report.docx")
    out_fallback = Path("MLOps_Report_Updated.docx")
    out_docs.parent.mkdir(parents=True, exist_ok=True)

    try:
        doc.save(out_root)
        print(f"Report successfully saved to {out_root}")
    except PermissionError:
        doc.save(out_fallback)
        print(f"WARNING: {out_root} is open in Word! Saved updated version to {out_fallback}")

    try:
        doc.save(out_docs)
        print(f"Report successfully saved to {out_docs}")
    except PermissionError:
        print(f"WARNING: {out_docs} is also open in an external application.")


if __name__ == "__main__":
    build_full_report()
