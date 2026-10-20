"""Generate the comprehensive, publication-quality MLOps Assignment 1 Final Report.

Structured for optimal academic density (~10-11 pages) adhering strictly to BITS Pilani
AIMLCZG523 assignment guidelines.

Outputs:
  - MLOps_Report.docx (root)
  - docs/MLOps_Report.docx
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


def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
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
        set_cell_margins(cell, top=90, bottom=90, left=110, right=110)
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
            set_cell_margins(cell, top=60, bottom=60, left=110, right=110)
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
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=90, bottom=90, left=140, right=140)

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
    p0.paragraph_format.space_after = Pt(3)
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
        h.paragraph_format.space_before = Pt(11)
        h.paragraph_format.space_after = Pt(3)
        for r in h.runs:
            r.font.color.rgb = RGBColor(27, 54, 93)
            r.font.size = Pt(13)
            r.font.bold = True
    elif level == 2:
        h.paragraph_format.space_before = Pt(8)
        h.paragraph_format.space_after = Pt(2)
        for r in h.runs:
            r.font.color.rgb = RGBColor(41, 74, 110)
            r.font.size = Pt(11)
            r.font.bold = True
    elif level == 3:
        h.paragraph_format.space_before = Pt(5)
        h.paragraph_format.space_after = Pt(1)
        for r in h.runs:
            r.font.color.rgb = RGBColor(60, 60, 60)
            r.font.size = Pt(10)
            r.font.bold = True
    return h


def add_p(doc, text="", bold_prefix=None, space_after=3):
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
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.12
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(27, 54, 93)
    r_txt = p.add_run(text)
    r_txt.font.color.rgb = RGBColor(35, 35, 35)
    r_txt.font.size = Pt(9.5)
    return p


def add_figure_if_exists(doc, img_path_str, caption, width=Inches(5.6)):
    p = Path(img_path_str)
    if p.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(1)
        p_img.add_run().add_picture(str(p), width=width)
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(5)
        r_cap = p_cap.add_run(caption)
        r_cap.font.size = Pt(8)
        r_cap.font.italic = True
        r_cap.font.color.rgb = RGBColor(80, 80, 80)


def add_side_by_side_figures(doc, left_path, right_path, caption, left_w=Inches(3.1), right_w=Inches(3.1)):
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
        p_cap.paragraph_format.space_after = Pt(5)
        r_cap = p_cap.add_run(caption)
        r_cap.font.size = Pt(8)
        r_cap.font.italic = True
        r_cap.font.color.rgb = RGBColor(80, 80, 80)


def add_triplet_figures(doc, p1, p2, p3, caption, w1=Inches(2.05), w2=Inches(2.05), w3=Inches(2.05)):
    paths = [Path(p1), Path(p2), Path(p3)]
    if all(p.exists() for p in paths):
        t = doc.add_table(rows=1, cols=3)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        widths = [w1, w2, w3]
        for idx, c in enumerate(t.rows[0].cells):
            c.width = widths[idx]
            set_cell_background(c, "FFFFFF")
            set_cell_margins(c, 0, 0, 0, 0)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(str(paths[idx]), width=widths[idx])

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(1)
        p_cap.paragraph_format.space_after = Pt(5)
        r_cap = p_cap.add_run(caption)
        r_cap.font.size = Pt(8)
        r_cap.font.italic = True
        r_cap.font.color.rgb = RGBColor(80, 80, 80)


def add_2x2_figures(doc, r1c1, r1c2, r2c1, r2c2, caption, w1=Inches(3.1), w2=Inches(3.1)):
    p_all = [Path(r1c1), Path(r1c2), Path(r2c1), Path(r2c2)]
    if all(p.exists() for p in p_all):
        t = doc.add_table(rows=2, cols=2)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for r_idx in range(2):
            for c_idx in range(2):
                c = t.rows[r_idx].cells[c_idx]
                c.width = w1 if c_idx == 0 else w2
                set_cell_background(c, "FFFFFF")
                set_cell_margins(c, 0, 0, 0, 0)
                p = c.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.add_run().add_picture(str(p_all[r_idx * 2 + c_idx]), width=c.width)

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(1)
        p_cap.paragraph_format.space_after = Pt(5)
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
    sec.top_margin = Inches(0.7)
    sec.bottom_margin = Inches(0.7)
    sec.left_margin = Inches(0.75)
    sec.right_margin = Inches(0.75)

    # Base Font
    style_normal = doc.styles["Normal"]
    style_normal.font.name = "Calibri"
    style_normal.font.size = Pt(9.5)
    style_normal.font.color.rgb = RGBColor(35, 35, 35)

    # Title Banner
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(1)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("End-to-End MLOps Pipeline for Heart Disease Risk Prediction")
    r_title.font.size = Pt(17)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(27, 54, 93)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(6)
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("Machine Learning Operations (AIMLCZG523) — Assignment 01 Technical Report")
    r_sub.font.size = Pt(10.5)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(70, 70, 70)

    # Metadata Table
    meta_table = doc.add_table(rows=2, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(meta_table, color="B0C4DE", sz="6")
    meta_widths = [Inches(3.3), Inches(3.4)]

    row0 = meta_table.rows[0]
    row0.cells[0].text = "Student Name: Mohanapriya M"
    row0.cells[1].text = "Student ID: 2025AE05482"
    row1 = meta_table.rows[1]
    row1.cells[0].text = "Course: AIMLCZG523 (MLOps)"
    row1.cells[1].text = "Repository: https://github.com/Mohana1507/heart-disease-mlops"

    for row in meta_table.rows:
        for c_idx, cell in enumerate(row.cells):
            set_cell_background(cell, "F4F7FA")
            set_cell_margins(cell, top=45, bottom=45, left=90, right=90)
            cell.width = meta_widths[c_idx]
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                for r in p.runs:
                    r.font.size = Pt(8.5)
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(27, 54, 93)

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(2)
    p_spacer.paragraph_format.space_after = Pt(4)

    # -------------------------------------------------------------
    # 1. Introduction and Scope
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "1. Introduction and Scope", level=1)
    add_p(doc,
        "Cardiovascular diseases represent the leading cause of global mortality, responsible for an estimated "
        "17.9 million deaths annually (World Health Organization [WHO], 2021). Automated clinical risk stratification "
        "derived from non-invasive diagnostic indicators—such as resting blood pressure, serum cholesterol, resting "
        "electrocardiography, and exercise treadmill measurements—enables physicians to prioritize urgent interventions. "
        "However, transitioning predictive models from exploratory notebooks into clinical environments requires robust "
        "Machine Learning Operations (MLOps) engineering to guarantee reproducibility, auditability, low-latency serving, "
        "and runtime observability.")

    add_p(doc,
        "This project implements an end-to-end MLOps workflow for heart disease risk classification utilizing the canonical "
        "UCI Cleveland Heart Disease benchmark (Janosi et al., 1989; Dua & Graff, 2019). The engineering pipeline spans: "
        "(1) automated data ingestion and leakage-free sanitization; (2) exploratory data analysis with diagnostic visualizations; "
        "(3) hyperparameter-tuned candidate model training evaluated via nested cross-validation (Pedregosa et al., 2011); "
        "(4) experiment tracking and artifact lineage with MLflow (Zaharia et al., 2018); (5) production packaging into an encapsulated "
        "scikit-learn pipeline; (6) containerized REST microservice serving via FastAPI (Tiangolo, 2024); (7) declarative Kubernetes "
        "orchestration (Kubernetes Authors, 2024); (8) Prometheus and Grafana monitoring (Prometheus Authors, 2024); and (9) automated "
        "continuous integration and deployment through GitHub Actions.")

    add_p(doc, "Table 1 outlines the mapping between core assignment tasks and repository implementations.", bold_prefix="Implementation Mapping: ")

    # Table 1: Requirement to Artifact Mapping
    t1 = doc.add_table(rows=10, cols=3)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t1)
    col_w1 = [Inches(1.6), Inches(2.7), Inches(2.4)]

    headers1 = ["Assignment Task", "Implementation Summary", "Repository Artefacts"]
    for i, h in enumerate(headers1):
        t1.rows[0].cells[i].text = h
    format_table_header(t1.rows[0], col_w1)

    t1_data = [
        ("1. Data & EDA", "Automated ingestion, target binarization, NaN preservation, class balance, correlation heatmap & histograms.", "scripts/download_data.py, src/heart/data.py, src/heart/eda.py"),
        ("2. Modelling", "ColumnTransformer preprocessing, 3 tuned classifiers (LR, RF, GB), 5x3 nested CV protocol.", "src/heart/features.py, src/heart/modeling.py"),
        ("3. Tracking", "MLflow run logging of hyperparameters, CV metrics, test scores, ROC/PR curves, and model signatures.", "src/heart/train.py, mlruns/"),
        ("4. Packaging", "Self-contained scikit-learn Pipeline serialization (model.joblib) with companion metadata.json.", "models/model.joblib, models/metadata.json"),
        ("5. CI/CD & Tests", "21 offline pytest unit tests (synthetic fixture), 4-stage GitHub Actions workflow (lint, test, train, docker).", "tests/, .github/workflows/ci.yml"),
        ("6. Containerization", "FastAPI serving application, non-root user security hardening, container HEALTHCHECK probe.", "Dockerfile, src/heart/api.py"),
        ("7. Deployment", "Declarative Kubernetes Deployment (2 replicas), LoadBalancer Service, Ingress, and Autoscaling (HPA).", "k8s/deployment.yaml, k8s/service.yaml, k8s/hpa.yaml"),
        ("8. Monitoring", "Structured JSON request logging without raw PII, Prometheus telemetry (/metrics), pre-provisioned Grafana.", "src/heart/api.py, docker-compose.yml, monitoring/"),
        ("9. Documentation", "Technical report, video walkthrough outline, execution instructions, and reproducible manifests.", "MLOps_Report.docx, README.md, docs/"),
    ]
    for r_idx, (c0, c1, c2) in enumerate(t1_data, start=1):
        row = t1.rows[r_idx]
        row.cells[0].text = c0
        row.cells[1].text = c1
        row.cells[2].text = c2
    format_table_rows(t1, col_w1)

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(2)
    p_sp.paragraph_format.space_after = Pt(2)

    add_p(doc,
        "Figure 1 illustrates the modular system architecture, tracing the lifecycle from raw data acquisition to Kubernetes "
        "load balancing and Prometheus/Grafana operational monitoring.", bold_prefix="Architecture Walkthrough: ")

    add_figure_if_exists(doc, "docs/architecture.png",
        "Figure 1: End-to-end MLOps pipeline architecture — from raw data acquisition to Kubernetes serving and Grafana monitoring.",
        width=Inches(5.5))

    # -------------------------------------------------------------
    # 2. Setup and Environment Configuration
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "2. Setup and Environment Configuration", level=1)
    add_p(doc,
        "To ensure deterministic execution across operating systems (Linux, macOS, Windows) and eliminate dependency drift, "
        "project dependencies are pinned strictly and partitioned into two functional tiers:")

    add_bullet_p(doc, "Runtime Serving Dependencies (requirements-serve.txt): ",
        "Minimal set required for model deserialization and inference: numpy==1.26.4, pandas==2.2.3, scikit-learn==1.5.2, "
        "scipy==1.13.1, joblib==1.4.2, fastapi==0.115.4, uvicorn==0.32.0, pydantic==2.9.2, prometheus-client==0.21.0. Keeps the "
        "production container compressed image size to 162 MB.")
    add_bullet_p(doc, "Development & Training Dependencies (requirements.txt): ",
        "Extends runtime dependencies with training and quality tooling: matplotlib==3.9.2, seaborn==0.13.2, mlflow==2.17.2, "
        "pytest==8.3.3, pytest-cov==5.0.0, httpx==0.27.2, flake8==7.1.1, and an editable install of the package (-e .).")

    add_callout_box(doc, "Quickstart Setup Commands", [
        "git clone https://github.com/Mohana1507/heart-disease-mlops.git && cd heart-disease-mlops",
        "python -m venv .venv && source .venv/bin/activate  # Windows: .venv\\Scripts\\activate",
        "pip install -r requirements.txt && python scripts/download_data.py",
        "python -m heart.eda && python -m heart.train && pytest -v"
    ])

    # -------------------------------------------------------------
    # 3. Data Acquisition and Exploratory Data Analysis
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "3. Data Acquisition and Exploratory Data Analysis", level=1)

    add_heading_with_spacing(doc, "3.1 Dataset Overview", level=2)
    add_p(doc,
        "The UCI Cleveland Heart Disease dataset (Janosi et al., 1989) is the most widely utilized benchmark among the four UCI heart disease "
        "cohorts. The raw cohort contains 303 patient records and 14 clinical attributes (13 predictors and 1 target). "
        "Automated ingestion (scripts/download_data.py) verifies file integrity and downloads raw data directly from the UCI archive.")

    # Table 3: Schema Overview
    t3 = doc.add_table(rows=15, cols=4)
    t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t3)
    col_w3 = [Inches(1.1), Inches(1.1), Inches(1.6), Inches(2.9)]
    for i, h in enumerate(["Attribute", "Type", "Domain / Values", "Clinical Description"]):
        t3.rows[0].cells[i].text = h
    format_table_header(t3.rows[0], col_w3)

    t3_data = [
        ("age", "Continuous", "29 – 77 years", "Patient age in years"),
        ("sex", "Categorical", "0 = female, 1 = male", "Biological sex"),
        ("cp", "Categorical", "1: typ. angina, 2: atyp., 3: non-anginal, 4: asympt.", "Chest pain diagnostic type"),
        ("trestbps", "Continuous", "94 – 200 mm Hg", "Resting blood pressure on hospital admission"),
        ("chol", "Continuous", "126 – 564 mg/dL", "Serum cholesterol level"),
        ("fbs", "Categorical", "0 = <=120 mg/dL, 1 = >120 mg/dL", "Fasting blood sugar > 120 mg/dL"),
        ("restecg", "Categorical", "0: normal, 1: ST-T wave abn., 2: LV hypertrophy", "Resting electrocardiographic findings"),
        ("thalach", "Continuous", "71 – 202 bpm", "Maximum heart rate achieved during exercise"),
        ("exang", "Categorical", "0 = no, 1 = yes", "Exercise-induced angina symptom"),
        ("oldpeak", "Continuous", "0.0 – 6.2 mm", "ST depression induced by exercise relative to rest"),
        ("slope", "Categorical", "1: upsloping, 2: flat, 3: downsloping", "Peak exercise ST segment slope"),
        ("ca", "Continuous", "0 – 3 vessels (4 missing)", "Number of major vessels colored by fluoroscopy"),
        ("thal", "Categorical", "3: normal, 6: fixed defect, 7: revers. (2 miss.)", "Thallium-201 myocardial scintigraphy defect"),
        ("target (num)", "Binary", "0 = healthy (absent), 1 = disease (present)", "Angiographic coronary artery disease status")
    ]
    for r_idx, (c0, c1, c2, c3) in enumerate(t3_data, start=1):
        row = t3.rows[r_idx]
        row.cells[0].text = c0
        row.cells[1].text = c1
        row.cells[2].text = c2
        row.cells[3].text = c3
    format_table_rows(t3, col_w3)

    add_heading_with_spacing(doc, "3.2 Data Sanitization and Data Leakage Prevention", level=2)
    add_p(doc,
        "Raw UCI data marks missing entries with '?' characters. The ingestion script parses these to IEEE NaN floats. "
        "Six total entries contain missing values: four in 'ca' and two in 'thal'. One duplicate row is removed. "
        "The raw integer target (0 = no disease, 1–4 = varying degrees of coronary stenosis) is binarized to {0, 1}. "
        "Crucially, the cleaned CSV deliberately preserves NaN values rather than imputing them upfront. Imputation parameters "
        "are learned strictly inside the training folds of the scikit-learn pipeline, preventing cross-validation data leakage.")

    add_heading_with_spacing(doc, "3.3 Exploratory Data Analysis & Empirical Observations", level=2)
    add_p(doc,
        "Executing python -m heart.eda generates visual diagnostics exported to reports/figures/ and writes summary statistics "
        "to reports/eda_summary.txt. Figure 2 presents the target class balance, Pearson correlation matrix, continuous feature "
        "distributions, and boxplots by disease status.")

    add_2x2_figures(doc,
        "screenshots/01_eda_class_balance.png",
        "screenshots/02_eda_correlation.png",
        "screenshots/02b_eda_histograms.png",
        "screenshots/02c_eda_boxplots.png",
        "Figure 2: Comprehensive EDA suite — (Top-Left) Class balance (54.1% healthy, 45.9% disease); (Top-Right) Pearson correlation matrix; (Bottom-Left) Continuous feature histograms; (Bottom-Right) Clinical boxplots grouped by target diagnosis.",
        w1=Inches(3.2), w2=Inches(3.2))

    add_p(doc, "Key clinical observations from exploratory analysis:", bold_prefix="Empirical Insights: ")
    add_bullet_p(doc, "Class Distribution: ", "164 healthy subjects (54.1%) vs 138 disease subjects (45.9%). Well-balanced distribution avoids degenerate majority-class bias.")
    add_bullet_p(doc, "Maximum Heart Rate (thalach): ", "Exhibits strong negative correlation with disease (r = -0.42). Healthy patients achieve median thalach of 158 bpm compared to 142 bpm for diseased patients, reflecting chronotropic reserve.")
    add_bullet_p(doc, "Exercise ST Depression (oldpeak): ", "Positively correlated with coronary disease (r = +0.42). Healthy individuals exhibit median ST depression of 0.0 mm vs 1.4 mm in diseased patients.")
    add_bullet_p(doc, "Chest Pain Type (cp): ", "Asymptomatic presentation (cp = 4) exhibits the highest disease incidence (>72%), demonstrating that advanced coronary obstruction frequently manifests without typical angina.")

    # -------------------------------------------------------------
    # 4. Feature Engineering and Model Development
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "4. Feature Engineering and Model Development", level=1)

    add_heading_with_spacing(doc, "4.1 Preprocessing Pipeline Design", level=2)
    add_p(doc,
        "To ensure modularity and prevent train-serving skew, all feature transformations are encapsulated in a single scikit-learn "
        "ColumnTransformer (src/heart/features.py):")
    add_bullet_p(doc, "Numeric Pipeline (age, trestbps, chol, thalach, oldpeak, ca): ",
        "Median imputation (SimpleImputer) followed by z-score standardization (StandardScaler).")
    add_bullet_p(doc, "Categorical Pipeline (sex, cp, fbs, restecg, exang, slope, thal): ",
        "Most-frequent imputation followed by one-hot encoding (OneHotEncoder(handle_unknown='ignore')).")

    add_heading_with_spacing(doc, "4.2 Candidate Classifiers and Inductive Biases", level=2)
    add_p(doc,
        "Three distinct algorithmic families were selected to explore differing inductive biases:")
    add_bullet_p(doc, "Logistic Regression (L2-regularized): ", "Linear decision boundary with calibrated probabilistic outputs; robust against overfitting on small medical cohorts (N=242 train).")
    add_bullet_p(doc, "Random Forest: ", "Non-linear bagging ensemble of decision trees with feature sub-sampling, reducing estimation variance.")
    add_bullet_p(doc, "Gradient Boosting: ", "Sequential boosting ensemble minimizing binomial deviance, capable of capturing complex non-linear feature interactions.")

    add_heading_with_spacing(doc, "4.3 Evaluation Protocol & Experimental Results", level=2)
    add_p(doc,
        "Model evaluation utilizes a nested cross-validation protocol (5 outer folds, 3 inner folds) on the 80% development split (N=242), "
        "with a held-out test split (20%, N=61) reserved exclusively for final evaluation. Hyperparameters are optimized via GridSearchCV "
        "on the inner folds using ROC-AUC scoring.")

    # Table 4: Experimental Results
    t4 = doc.add_table(rows=4, cols=8)
    t4.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t4)
    col_w4 = [Inches(1.2), Inches(0.8), Inches(0.8), Inches(0.8), Inches(0.8), Inches(1.1), Inches(0.6), Inches(0.6)]
    headers4 = ["Candidate Model", "CV Acc.", "CV Prec.", "CV Rec.", "CV F1", "CV ROC-AUC", "Test Acc.", "Test AUC"]
    for i, h in enumerate(headers4):
        t4.rows[0].cells[i].text = h
    format_table_header(t4.rows[0], col_w4)

    t4_data = [
        ("Logistic Regression", "0.8305", "0.8594", "0.7652", "0.8054", "0.9018 ± 0.0156", "88.52%", "0.9665"),
        ("Random Forest", "0.8057", "0.8082", "0.7826", "0.7933", "0.8914 ± 0.0316", "86.89%", "0.9416"),
        ("Gradient Boosting", "0.7808", "0.7818", "0.7565", "0.7651", "0.8744 ± 0.0249", "86.89%", "0.9610")
    ]
    for r_idx, row_vals in enumerate(t4_data, start=1):
        row = t4.rows[r_idx]
        for c_idx, val in enumerate(row_vals):
            row.cells[c_idx].text = val
    format_table_rows(t4, col_w4)

    add_triplet_figures(doc,
        "screenshots/model_comparison.png",
        "screenshots/logistic_regression_confusion_matrix.png",
        "screenshots/logistic_regression_roc.png",
        "Figure 3: (Left) Nested CV ROC-AUC comparison across candidate models; (Center) Champion test Confusion Matrix on 61 patients (26 TP, 28 TN, 5 FP, 2 FN); (Right) Champion test ROC Curve (AUC = 0.9665).",
        w1=Inches(2.1), w2=Inches(2.1), w3=Inches(2.1))

    add_p(doc,
        "Performance Discussion: L2-regularized Logistic Regression achieved the highest outer-fold mean ROC-AUC (0.9018 ± 0.0156) "
        "and demonstrated lower observed variance across outer folds than Random Forest (0.8914 ± 0.0316) and Gradient Boosting (0.8744 ± 0.0249). "
        "On the independent 61-patient hold-out test set, Logistic Regression attained 88.52% Accuracy, 92.86% Recall (diagnosing 26 of 28 "
        "diseased patients with only 2 false negatives), and a test ROC-AUC of 0.9665. Consequently, Logistic Regression was promoted to production.")

    add_heading_with_spacing(doc, "4.4 Key Engineering Decisions and Practical Challenges", level=2)
    add_bullet_p(doc, "Preserving Missing Values During Ingestion: ",
        "The cleaned dataset deliberately preserves NaN markers rather than imputing them globally. Pre-imputation causes subtle data "
        "leakage because validation fold statistics influence training statistics. Imputing strictly within pipeline folds ensures clean separation.")
    add_bullet_p(doc, "Multiprocessing Resource Contention on Windows: ",
        "Setting n_jobs=-1 inside joblib GridSearchCV spawned excessive worker processes on Windows host environments, exhausting memory "
        "commit limits. This was resolved by parameterizing N_JOBS via environment variables with a safe single-worker default.")
    add_bullet_p(doc, "Fail-Fast Static Analysis: ",
        "Enforcing flake8 lint gates in CI initially caught formatting issues in helper scripts. Specific helper excludes were codified in "
        "setup.cfg to maintain strict standards across production src/ and tests/ modules while allowing specialized scripts.")

    # -------------------------------------------------------------
    # 5. Experiment Tracking with MLflow
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "5. Experiment Tracking with MLflow", level=1)
    add_p(doc,
        "All training runs, hyperparameters, cross-validation metrics, and serialized artifacts are tracked via MLflow (Zaharia et al., 2018) "
        "under experiment 'heart-disease-risk'. A final promotion run ('final_model_selection') tags the champion model and serializes "
        "production artifacts.")

    # Table 5: MLflow Taxonomy
    t5 = doc.add_table(rows=5, cols=2)
    t5.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t5)
    col_w5 = [Inches(1.8), Inches(4.9)]
    for i, h in enumerate(["Artifact Category", "Logged Metadata and Payloads"]):
        t5.rows[0].cells[i].text = h
    format_table_header(t5.rows[0], col_w5)

    t5_data = [
        ("Parameters", "Model family, random seed (42), test size (0.2), outer folds (5), inner folds (3), train rows (242), test rows (61), best_C, best_penalty."),
        ("CV Metrics", "Mean and std across 5 outer folds: cv_accuracy, cv_precision, cv_recall, cv_f1, cv_roc_auc, tuning_best_cv_roc_auc."),
        ("Hold-Out Test Metrics", "Unbiased validation scores on 61 test patients: test_accuracy, test_precision, test_recall, test_f1, test_roc_auc."),
        ("Logged Artifacts", "Confusion matrix and ROC plots, serialized Pipeline model, Conda environment descriptor, and MLmodel signature.")
    ]
    for r_idx, (cat, desc) in enumerate(t5_data, start=1):
        row = t5.rows[r_idx]
        row.cells[0].text = cat
        row.cells[1].text = desc
    format_table_rows(t5, col_w5)

    add_side_by_side_figures(doc,
        "screenshots/03_mlflow_runs.png",
        "screenshots/04_mlflow_run_detail.png",
        "Figure 4: MLflow Tracking Server — (Left) Candidate runs overview under experiment 'heart-disease-risk'; (Right) Champion Logistic Regression logged parameters (10) and cross-validation/test metrics (16).",
        left_w=Inches(3.2), right_w=Inches(3.2))

    # -------------------------------------------------------------
    # 6. Model Packaging and Reproducibility
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "6. Model Packaging and Reproducibility", level=1)
    add_p(doc,
        "To eliminate train-serving skew, the deployable unit produced by src/heart/train.py is the entire fitted scikit-learn Pipeline "
        "(imputation + scaling + encoding + classifier) serialized to models/model.joblib. The companion metadata file (models/metadata.json) "
        "records the training timestamp, Git commit SHA, feature ordering, and evaluation metrics.")

    add_bullet_p(doc, "Fixed Pseudorandom Seeds: ", "Random seed (RANDOM_STATE = 42) is enforced across splits, folds, and estimators, validated by unit test test_training_is_reproducible.")
    add_bullet_p(doc, "Strict Dependency Pinning: ", "All library versions are pinned in requirements-serve.txt and requirements.txt.")
    add_bullet_p(doc, "Artifact Immutability: ", "Production containers copy the serialized model directly during build; serving requires no retraining.")

    # -------------------------------------------------------------
    # 7. Automated Testing and CI/CD Pipeline
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "7. Automated Testing and CI/CD Pipeline", level=1)

    add_heading_with_spacing(doc, "7.1 Unit Testing Framework (pytest)", level=2)
    add_p(doc,
        "The test suite comprises 21 automated pytest unit tests across four modules: (1) test_data.py verifies question mark parsing, "
        "duplicate removal, target binarization, and schema validation; (2) test_features.py asserts null-free output, z-score scaling, and unseen "
        "category handling; (3) test_model.py confirms candidate architectures, metric bounds, reproducibility, and end-to-end execution; "
        "(4) test_api.py tests FastAPI endpoints, Pydantic input validation, missing field tolerance, and HTTP 422 error handling. "
        "An offline synthetic fixture (tests/synthetic.py) ensures tests execute deterministically without external network calls.")

    add_heading_with_spacing(doc, "7.2 Multi-Stage GitHub Actions CI/CD Pipeline", level=2)
    add_p(doc,
        "Continuous Integration and Continuous Deployment is automated via GitHub Actions (.github/workflows/ci.yml). "
        "The pipeline enforces four sequential dependency-gated jobs:")
    add_bullet_p(doc, "Job 1 (lint): ", "Enforces PEP 8 compliance via flake8 src tests scripts. Any violation halts the pipeline.")
    add_bullet_p(doc, "Job 2 (test): ", "Installs dependencies, runs 21 pytest tests with coverage, and uploads test reports.")
    add_bullet_p(doc, "Job 3 (train): ", "Executes data ingestion, EDA, nested CV model training, MLflow tracking, and model packaging.")
    add_bullet_p(doc, "Job 4 (docker): ", "Builds the serving container, boots it locally, and executes HTTP smoke tests against /health and /predict.")

    add_2x2_figures(doc,
        "screenshots/05_pytest_pass.png",
        "screenshots/06_actions_run.png",
        "screenshots/07_actions_artifacts.png",
        "screenshots/08_actions_failure.png",
        "Figure 5: Verification & CI/CD — (Top-Left) Terminal output showing all 21 pytest unit tests passing in 40.24s; (Top-Right) GitHub Actions 4-stage workflow (lint, test, train, docker) all green; (Bottom-Left) Uploaded pipeline build artifacts; (Bottom-Right) Fail-fast demonstration showing pipeline termination on lint error.",
        w1=Inches(3.2), w2=Inches(3.2))

    # -------------------------------------------------------------
    # 8. Model Containerization
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "8. Model Containerization", level=1)
    add_p(doc,
        "The serving application is packaged into a production Docker container (Dockerfile) utilizing python:3.11-slim. "
        "Security hardening features include non-root execution (useradd appuser), pinned runtime dependencies, minimal image size (162 MB), "
        "and a container HEALTHCHECK probing /health every 30 seconds.")

    # Table 6: API Surface
    t6 = doc.add_table(rows=5, cols=3)
    t6.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t6)
    col_w6 = [Inches(1.5), Inches(1.1), Inches(4.1)]
    for i, h in enumerate(["Endpoint", "HTTP Method", "Behavior & Response Schema"]):
        t6.rows[0].cells[i].text = h
    format_table_header(t6.rows[0], col_w6)

    t6_data = [
        ("POST /predict", "POST", "Validates PatientFeatures, evaluates model, returns prediction (0/1), label, probability_disease, confidence, model_version."),
        ("GET /health", "GET", "Probes model readiness. Returns status ('ok') and model_loaded boolean. Used by container and Kubernetes health probes."),
        ("GET /model-info", "GET", "Exposes metadata.json (training timestamp, Git commit SHA, hold-out evaluation metrics)."),
        ("GET /metrics", "GET", "Exposes Prometheus telemetry (request counts, latency histograms, prediction class distribution).")
    ]
    for r_idx, (ep, m, beh) in enumerate(t6_data, start=1):
        row = t6.rows[r_idx]
        row.cells[0].text = ep
        row.cells[1].text = m
        row.cells[2].text = beh
    format_table_rows(t6, col_w6)

    add_side_by_side_figures(doc,
        "screenshots/09_docker_build.png",
        "screenshots/10_docker_predict.png",
        "Figure 6: Containerization — (Left) Docker single-stage production build completing with 162 MB compressed image; (Right) Container running healthy on port 8000 and returning JSON prediction payload.",
        left_w=Inches(3.2), right_w=Inches(3.2))

    # -------------------------------------------------------------
    # 9. Production Deployment and Kubernetes Orchestration
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "9. Production Deployment and Kubernetes Orchestration", level=1)
    add_p(doc,
        "Declarative Kubernetes manifests (k8s/) support scalable production deployment across local clusters (Docker Desktop Kubernetes, "
        "Minikube) and managed cloud platforms (GKE, EKS, AKS):")
    add_bullet_p(doc, "Deployment (k8s/deployment.yaml): ", "2 pod replicas for high availability, resource requests (100m CPU, 256Mi RAM), limits (500m CPU, 512Mi RAM), liveness and readiness probes on /health, Prometheus scrape annotations.")
    add_bullet_p(doc, "Service (k8s/service.yaml): ", "LoadBalancer service exposing HTTP port 80 and routing to container targetPort 8000.")
    add_bullet_p(doc, "Autoscaling (k8s/hpa.yaml): ", "Horizontal Pod Autoscaler scaling from 2 to 5 replicas when average CPU exceeds 70%.")

    add_heading_with_spacing(doc, "9.2 Deployed API Access and Invocation", level=2)
    add_p(doc,
        "The microservice can be queried via standard HTTP clients. Below is the active deployment access specification:")
    add_bullet_p(doc, "Deployment Host & Port: ", "Local cluster: http://localhost:80 (LoadBalancer) or http://localhost:8000 (direct/port-forward).")
    add_bullet_p(doc, "Health Verification Endpoint: ", "GET http://localhost/health (returns HTTP 200: {\"status\": \"ok\", \"model_loaded\": true}).")
    add_bullet_p(doc, "Interactive API Documentation: ", "Swagger UI accessible at http://localhost:8000/docs.")

    add_callout_box(doc, "Sample curl Inference Request", [
        'curl -X POST http://localhost/predict \\',
        '  -H "Content-Type: application/json" \\',
        '  -d \'{"age": 57, "sex": 1, "cp": 2, "trestbps": 130, "chol": 236, \\',
        '       "fbs": 0, "restecg": 0, "thalach": 174, "exang": 0, "oldpeak": 0.0, \\',
        '       "slope": 1, "ca": 1, "thal": 3}\'',
        '',
        '# Response (HTTP 200 OK):',
        '{"prediction": 0, "label": "no_disease", "probability_disease": 0.4258,',
        ' "confidence": 0.5742, "model_version": "logistic_regression-20261020082404"}'
    ])

    add_side_by_side_figures(doc,
        "screenshots/11_k8s_pods_svc.png",
        "screenshots/12_k8s_predict.png",
        "Figure 7: Kubernetes Deployment — (Left) Active Pods (pod/heart-disease-api-7b8df95c4d-6m8qk, x92pt) and LoadBalancer Service (10.108.45.192:80); (Right) Successful HTTP inference request routed through the LoadBalancer Service on localhost:80.",
        left_w=Inches(3.2), right_w=Inches(3.2))

    # -------------------------------------------------------------
    # 10. Monitoring and Logging
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "10. Monitoring and Logging", level=1)
    add_p(doc,
        "The observability framework pairs structured JSON request logging with Prometheus metrics collection and a Grafana dashboard:")
    add_bullet_p(doc, "Privacy-Conscious Structured Request Logging: ",
        "FastAPI middleware intercepts every HTTP transaction, assigns an X-Request-ID header, tracks latency via time.perf_counter(), "
        "and logs structured JSON (method, path, status, latency_ms). To comply with healthcare data privacy principles, raw clinical measurements "
        "are strictly omitted from logs; only the prediction class and confidence are recorded.")
    add_bullet_p(doc, "Prometheus Metrics Instrumentation: ",
        "Exposes api_requests_total (partitioned by method, path, status), api_request_latency_seconds (histogram buckets), and predictions_total "
        "(disease vs no_disease). Bounded route templates prevent metric cardinality explosion.")
    add_bullet_p(doc, "Grafana Observability Dashboard: ",
        "docker-compose.yml runs Prometheus (:9090) and Grafana (:3000) alongside the API. Grafana is pre-provisioned with panels for "
        "Request Throughput, p95 Latency, 5xx Error Rate, and Prediction Class Distribution. In cluster deployments, the identical /metrics endpoint "
        "is scraped by the cluster Prometheus operator using the pod annotations declared in k8s/deployment.yaml.")

    add_callout_box(doc, "Observability Verification (Prometheus Scrape Excerpt)", [
        '# Prometheus Scrape Excerpt (http://localhost:8000/metrics after 300 load test requests):',
        'api_requests_total{method="POST",path="/predict",status="200"} 288.0',
        'api_requests_total{method="POST",path="/predict",status="422"} 12.0',
        'predictions_total{label="no_disease"} 97.0',
        'predictions_total{label="disease"} 191.0',
        'api_request_latency_seconds_bucket{le="0.05",path="/predict"} 298.0'
    ])

    add_side_by_side_figures(doc,
        "screenshots/13_api_logs.png",
        "screenshots/14_grafana_dashboard.png",
        "Figure 8: Observability — (Left) Privacy-conscious structured JSON container logs with request IDs and latency; (Right) Real-time Grafana dashboard displaying request rate, p95 latency, and prediction distribution (97 no_disease vs 191 disease).",
        left_w=Inches(3.1), right_w=Inches(3.3))

    # -------------------------------------------------------------
    # 11. Limitations, Governance, and Future Work
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "11. Limitations, Governance, and Future Work", level=1)
    add_p(doc,
        "Key engineering constraints and governance considerations:")
    add_bullet_p(doc, "Sample Size & Population Drift: ",
        "The Cleveland benchmark is small (N=303) and reflects historical patient demographics (1989). In production, a data-drift detector "
        "(e.g., Evidently AI) should monitor Kolmogorov-Smirnov statistics on continuous inputs and Population Stability Index (PSI) on categorical features.")
    add_bullet_p(doc, "Automated Model Governance & Promotion: ",
        "Future iterations should integrate a formal model registry with automated canary deployment gates, comparing newly trained models "
        "against production champions on shadow traffic before routing clinical requests.")

    # -------------------------------------------------------------
    # 12. Conclusion
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "12. Conclusion", level=1)
    add_p(doc,
        "This project establishes a reproducible, production-grade MLOps pipeline for heart disease risk classification. "
        "Through leakage-free data processing, nested cross-validation, MLflow tracking, containerization with security hardening, "
        "declarative Kubernetes orchestration, and continuous monitoring via Prometheus and Grafana, the implementation satisfies "
        "the operational requirements of dependable clinical machine learning engineering.")

    # -------------------------------------------------------------
    # Appendix A: Repository Structure
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "Appendix A: Repository Structure", level=1)
    add_p(doc, "The repository is structured into standard production components:")
    add_callout_box(doc, "Directory Hierarchy (https://github.com/Mohana1507/heart-disease-mlops)", [
        "heart-disease-mlops/",
        "├── .github/workflows/ci.yml     # 4-stage GitHub Actions CI/CD workflow",
        "├── src/heart/                   # Production library (data, features, modeling, api)",
        "├── tests/                       # 21 automated unit tests and synthetic data fixture",
        "├── notebooks/                   # Jupyter notebooks (01_eda, 02_training, 03_inference)",
        "├── k8s/                         # Kubernetes manifests (deployment, service, hpa)",
        "├── monitoring/                  # Prometheus and Grafana provisioning configurations",
        "├── screenshots/                 # Visual evidence suite for submission verification",
        "├── Dockerfile & docker-compose  # Containerization & local observability stack",
        "└── requirements.txt             # Pinned dependencies for reproducible execution"
    ])

    # -------------------------------------------------------------
    # Appendix B: Pipeline Demonstration Video
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "Appendix B: Pipeline Demonstration Video", level=1)
    add_p(doc,
        "A recorded video walkthrough demonstrates the complete MLOps workflow from repository structure to live monitoring.",
        bold_prefix="Video Demonstration Link: ")

    # Highlighted Callout Box for Video Link
    add_callout_box(doc, "VIDEO WALKTHROUGH ACCESS & SUBMISSION LINK", [
        "Video URL: [PASTE_YOUR_VIDEO_LINK_HERE: e.g., https://youtu.be/xxxx or Google Drive link]",
        "",
        "Access Permissions: Set to 'Unlisted' on YouTube or 'Anyone with the link can view' on Drive.",
        "Demonstration Duration: Approximately 4 minutes.",
        "Key Demonstrations Covered:",
        "  - 0:00 - 0:45 : Repository structure, modular code design, and environment setup.",
        "  - 0:45 - 1:30 : GitHub Actions CI/CD pipeline run with all 4 jobs green (lint, test, train, docker).",
        "  - 1:30 - 2:15 : MLflow Tracking UI demonstrating candidate model runs and champion selection.",
        "  - 2:15 - 3:00 : Docker container execution and /predict inference verification.",
        "  - 3:00 - 4:00 : Real-time Grafana monitoring dashboard under active synthetic load."
    ], border_color="0066CC", bg_color="EBF3FB")

    # -------------------------------------------------------------
    # References
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "References", level=1)
    refs = [
        "Detrano, R., Janosi, A., Steinbrunn, W., Pfisterer, M., Schmid, J., Sandhu, S., Guppy, K., Lee, S., & Froelicher, V. (1989). International application of a new probability algorithm for the diagnosis of coronary artery disease. The American Journal of Cardiology, 64(5), 304–310.",
        "Dua, D., & Graff, C. (2019). UCI Machine Learning Repository: Heart Disease Data Set. University of California, Irvine, School of Information and Computer Sciences. https://archive.ics.uci.edu/ml/datasets/Heart+Disease",
        "Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1989). Heart Disease Database (Cleveland Clinic Foundation). UCI Machine Learning Repository.",
        "Kubernetes Authors. (2024). Kubernetes: Production-Grade Container Orchestration (Version 1.30). Cloud Native Computing Foundation. https://kubernetes.io/docs/",
        "Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, E. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, 2825–2830.",
        "Prometheus Authors. (2024). Prometheus: An Open-Source Systems Monitoring and Alerting Toolkit (Version 2.54). Cloud Native Computing Foundation. https://prometheus.io/docs/",
        "Tiangolo, S. (2024). FastAPI: Modern, Fast (High-Performance), Web Framework for Building APIs with Python 3.8+ (Version 0.115). https://fastapi.tiangolo.com/",
        "World Health Organization. (2021). Cardiovascular diseases (CVDs) Fact Sheet. World Health Organization. https://www.who.int/news-room/fact-sheets/detail/cardiovascular-diseases-(cvds)",
        "Zaharia, M., Chen, A., Davidson, A., Ghodsi, A., Hong, S. A., Konwinski, A., Murching, S., Nykodym, T., Ogilvie, P., Parkhe, M., Xie, F., & Zumar, C. (2018). Accelerating the machine learning lifecycle with MLflow. IEEE Data Engineering Bulletin, 41(4), 39–45."
    ]
    for r in refs:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.left_indent = Inches(0.4)
        p_ref.paragraph_format.first_line_indent = Inches(-0.4)
        p_ref.paragraph_format.space_before = Pt(1)
        p_ref.paragraph_format.space_after = Pt(2)
        p_ref.paragraph_format.line_spacing = 1.12
        r_ref = p_ref.add_run(r)
        r_ref.font.size = Pt(8.5)
        r_ref.font.color.rgb = RGBColor(40, 40, 40)

    # Save to target locations
    out_root = Path("MLOps_Report.docx")
    out_docs = Path("docs/MLOps_Report.docx")
    out_docs.parent.mkdir(parents=True, exist_ok=True)
    try:
        doc.save(out_root)
        print(f"Report successfully saved to {out_root}")
    except PermissionError:
        out_fallback = Path("MLOps_Report_Updated.docx")
        doc.save(out_fallback)
        print(f"WARNING: {out_root} is open in Word/LibreOffice! Saved updated version to {out_fallback}")

    try:
        doc.save(out_docs)
        print(f"Report successfully saved to {out_docs}")
    except PermissionError:
        print(f"WARNING: {out_docs} is also open in an external application.")


if __name__ == "__main__":
    build_full_report()
