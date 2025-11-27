import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import joblib
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "topics_dataset.csv"

# Load dataset
df = pd.read_csv(DATA_PATH)

X = df[["subject", "topic_length", "self_rating", "past_score"]]
y_difficulty = df["difficulty"]
y_time = df["time_needed_hours"]

# Encode difficulty labels (Easy, Medium, Hard)
le_diff = LabelEncoder()
y_diff_enc = le_diff.fit_transform(y_difficulty)

# Preprocessing: one-hot encode subject, passthrough numeric
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["subject"]),
        ("num", "passthrough", ["topic_length", "self_rating", "past_score"]),
    ]
)

# Pipelines
difficulty_pipeline = Pipeline(
    steps=[
        ("preprocess", preprocessor),
        ("model", RandomForestClassifier(random_state=42)),
    ]
)

time_pipeline = Pipeline(
    steps=[
        ("preprocess", preprocessor),
        ("model", RandomForestRegressor(random_state=42)),
    ]
)

# Train
difficulty_pipeline.fit(X, y_diff_enc)
time_pipeline.fit(X, y_time)

# Save models in ml/
joblib.dump(
    {"pipeline": difficulty_pipeline, "label_encoder": le_diff},
    ROOT / "ml" / "difficulty_model.pkl"
)
joblib.dump(time_pipeline, ROOT / "ml" / "time_model.pkl")

print("Models trained and saved.")
