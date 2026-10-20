"""Central configuration: paths, column names and constants."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATA_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/"
    "heart-disease/processed.cleveland.data"
)
RAW_PATH = ROOT / "data" / "raw" / "processed.cleveland.data"
CLEAN_PATH = ROOT / "data" / "processed" / "heart_clean.csv"

MODEL_DIR = ROOT / "models"
MODEL_PATH = MODEL_DIR / "model.joblib"
METADATA_PATH = MODEL_DIR / "metadata.json"
FIGURES_DIR = ROOT / "reports" / "figures"

RANDOM_STATE = 42
TARGET = "target"

# Column order of processed.cleveland.data (no header row in the file).
FEATURES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal",
]
COLUMNS = FEATURES + [TARGET]

NUMERIC_FEATURES = ["age", "trestbps", "chol", "thalach", "oldpeak"]
CATEGORICAL_FEATURES = ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"]

FEATURE_DESCRIPTIONS = {
    "age": "Age in years",
    "sex": "Sex (1 = male, 0 = female)",
    "cp": "Chest pain type (1-4)",
    "trestbps": "Resting blood pressure (mm Hg)",
    "chol": "Serum cholesterol (mg/dl)",
    "fbs": "Fasting blood sugar > 120 mg/dl (1 = true)",
    "restecg": "Resting ECG result (0-2)",
    "thalach": "Maximum heart rate achieved",
    "exang": "Exercise-induced angina (1 = yes)",
    "oldpeak": "ST depression induced by exercise",
    "slope": "Slope of peak exercise ST segment (1-3)",
    "ca": "Major vessels coloured by fluoroscopy (0-3)",
    "thal": "Thalassemia (3 = normal, 6 = fixed defect, 7 = reversible defect)",
}
