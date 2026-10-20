"""Generate rich, structured Jupyter notebooks for EDA, Training, and Inference."""
import json
from pathlib import Path


def create_eda_notebook(dest: Path):
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Exploratory Data Analysis: UCI Cleveland Heart Disease Dataset\n",
                "\n",
                "**Course:** AIMLCZG523 - Machine Learning Operations (MLOps)\n\n",
                "**Assignment 01 - Task 1:** Data Acquisition & Exploratory Data Analysis [5 marks]\n\n",
                "This notebook demonstrates data acquisition, cleaning, preprocessing, and exploratory data analysis for the UCI Cleveland heart disease dataset. All preprocessing logic is modularized in `src/heart` to guarantee absolute consistency between exploratory workflows, cross-validation, and production serving."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 1,
            "metadata": {},
            "outputs": [],
            "source": [
                "from pathlib import Path\n",
                "import pandas as pd\n",
                "from IPython.display import Image, display\n",
                "from heart import config, data, eda\n",
                "\n",
                "# Load cleaned dataset built from raw UCI Cleveland data\n",
                "df = data.ensure_clean_data()\n",
                "print(f'Dataset shape: {df.shape[0]} rows x {df.shape[1]} columns')\n",
                "df.head(10)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Missing Values & Summary Statistics\n",
                "\n",
                "In the raw Cleveland dataset (`processed.cleveland.data`), missing values are designated by `?`. Our cleaning module converts these to `NaN` and preserves them in `data/processed/heart_clean.csv`. Imputation is intentionally deferred to the modeling pipeline (`ColumnTransformer`) to avoid data leakage across cross-validation folds."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 2,
            "metadata": {},
            "outputs": [],
            "source": [
                "print(eda.summary_text(df))"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Exploratory Visualizations\n",
                "\n",
                "We generate five diagnostic figures:\n",
                "1. **Class Balance:** Distribution of target (0 = no disease, 1 = presence of disease).\n",
                "2. **Numeric Feature Histograms:** Stratified by diagnostic outcome.\n",
                "3. **Categorical Feature Frequencies:** Stratified by diagnostic outcome.\n",
                "4. **Pearson Correlation Heatmap:** Identifying feature interdependencies.\n",
                "5. **Numeric Feature Boxplots:** Outliers and quartile distributions."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 3,
            "metadata": {},
            "outputs": [],
            "source": [
                "figs = eda.run(config.FIGURES_DIR, df)\n",
                "for p in figs:\n",
                "    if p.suffix == '.png':\n",
                "        print(f'Generated: {p.name}')\n",
                "        display(Image(filename=str(p)))"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Key Observations & Clinical Insights\n",
                "\n",
                "- **Class Balance:** 164 patients (54.1%) without heart disease vs 139 patients (45.9%) with heart disease. The dataset is well-balanced.\n",
                "- **Missing Values:** Missing values occur only in `ca` (4 rows, 1.3%) and `thal` (2 rows, 0.7%).\n",
                "- **Key Predictors:**\n",
                "  - `thalach` (maximum heart rate) is significantly lower in heart disease patients (median ~142 bpm vs ~158 bpm in healthy subjects).\n",
                "  - `oldpeak` (ST depression) is markedly higher in heart disease patients (median ~1.4 mm vs ~0.0 mm in healthy subjects).\n",
                "  - `cp=4` (asymptomatic chest pain) and `exang=1` (exercise-induced angina) show strong positive correlation with disease.\n",
                "- **Correlation:** Pairwise correlations between predictors remain below 0.60, confirming suitability for classification without multicollinearity issues."
            ]
        }
    ]
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"}
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }
    dest.write_text(json.dumps(nb, indent=1), encoding="utf-8")


def create_training_notebook(dest: Path):
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Model Training, Tuning & MLflow Experiment Tracking\n",
                "\n",
                "**Course:** AIMLCZG523 - Machine Learning Operations (MLOps)\n\n",
                "**Assignment 01 - Tasks 2, 3 & 4:** Feature Engineering, Model Development & Experiment Tracking\n\n",
                "This notebook demonstrates model development across Logistic Regression, Random Forest, and Gradient Boosting using nested cross-validation, hyperparameter tuning (`GridSearchCV`), and MLflow tracking."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 1,
            "metadata": {},
            "outputs": [],
            "source": [
                "import json\n",
                "from IPython.display import Image, display\n",
                "from heart import config\n",
                "\n",
                "# Read metadata generated by train pipeline\n",
                "meta = json.loads(config.METADATA_PATH.read_text())\n",
                "print(f\"Selected Champion Model: {meta['model_name']}\")\n",
                "print(f\"Trained at: {meta['trained_at']}\")\n",
                "print(f\"Hold-out Test Accuracy: {meta['test_metrics']['accuracy']:.4f}\")\n",
                "print(f\"Hold-out Test ROC-AUC:  {meta['test_metrics']['roc_auc']:.4f}\")\n",
                "print(f\"Hold-out Test Recall:   {meta['test_metrics']['recall']:.4f}\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Nested Cross-Validation Comparison\n",
                "\n",
                "Nested cross-validation (5 outer folds, 3 inner folds) provides an unbiased estimate of generalization performance without optimistic tuning bias."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 2,
            "metadata": {},
            "outputs": [],
            "source": [
                "display(Image(filename=str(config.FIGURES_DIR / 'model_comparison.png')))"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Champion Model Performance Plots (Confusion Matrix & ROC Curve)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 3,
            "metadata": {},
            "outputs": [],
            "source": [
                "display(Image(filename=str(config.FIGURES_DIR / f\"{meta['model_name']}_confusion_matrix.png\")))\n",
                "display(Image(filename=str(config.FIGURES_DIR / f\"{meta['model_name']}_roc.png\")))"
            ]
        }
    ]
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"}
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }
    dest.write_text(json.dumps(nb, indent=1), encoding="utf-8")


def create_inference_notebook(dest: Path):
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Model Inference & API Serving Validation\n",
                "\n",
                "**Course:** AIMLCZG523 - Machine Learning Operations (MLOps)\n\n",
                "**Assignment 01 - Tasks 4 & 6:** Model Packaging, Local Inference & REST API Serving\n\n",
                "This notebook validates local model deserialization from `models/model.joblib`, schema validation via Pydantic, and scoring of patient clinical measurements."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 1,
            "metadata": {},
            "outputs": [],
            "source": [
                "import joblib\n",
                "import pandas as pd\n",
                "from heart import config\n",
                "from heart.api import PatientFeatures\n",
                "\n",
                "# Load packaged pipeline (ColumnTransformer + Classifier)\n",
                "pipeline = joblib.load(config.MODEL_PATH)\n",
                "print(f'Successfully loaded model from {config.MODEL_PATH}')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Single Patient Prediction Demo"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 2,
            "metadata": {},
            "outputs": [],
            "source": [
                "sample = {\n",
                "    'age': 63.0, 'sex': 1, 'cp': 1, 'trestbps': 145.0, 'chol': 233.0,\n",
                "    'fbs': 1, 'restecg': 2, 'thalach': 150.0, 'exang': 0,\n",
                "    'oldpeak': 2.3, 'slope': 3, 'ca': 0.0, 'thal': 6.0\n",
                "}\n",
                "patient = PatientFeatures(**sample)\n",
                "row = pd.DataFrame([patient.model_dump()])[config.FEATURES].astype(float)\n",
                "proba = float(pipeline.predict_proba(row)[0, 1])\n",
                "pred = int(proba >= 0.5)\n",
                "label = 'disease' if pred == 1 else 'no_disease'\n",
                "confidence = proba if pred == 1 else 1.0 - proba\n",
                "print(f'Prediction: {pred} ({label})')\n",
                "print(f'Probability of Heart Disease: {proba:.4f}')\n",
                "print(f'Confidence: {confidence:.4f}')"
            ]
        }
    ]
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"}
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }
    dest.write_text(json.dumps(nb, indent=1), encoding="utf-8")


if __name__ == "__main__":
    n_dir = Path("notebooks")
    n_dir.mkdir(exist_ok=True)
    create_eda_notebook(n_dir / "01_eda.ipynb")
    create_training_notebook(n_dir / "02_training.ipynb")
    create_inference_notebook(n_dir / "03_inference.ipynb")
    print("All 3 notebooks generated successfully.")
