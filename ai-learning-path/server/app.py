from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
from pathlib import Path
import pandas as pd

app = Flask(__name__)
CORS(app)

# Paths
ROOT = Path(__file__).resolve().parent.parent
ML_DIR = ROOT / "ml"

# Load models
difficulty_bundle = joblib.load(ML_DIR / "difficulty_model.pkl")
difficulty_model = difficulty_bundle["pipeline"]
diff_label_encoder = difficulty_bundle["label_encoder"]

time_model = joblib.load(ML_DIR / "time_model.pkl")


@app.get("/")
def home():
    return {"message": "API is running!"}


@app.route("/predict", methods=["POST"])
def predict():
    body = request.get_json(force=True)

    subject = body.get("subject", "")
    topic_length = float(body.get("topic_length", 1))
    self_rating = float(body.get("self_rating", 3))
    past_score = float(body.get("past_score", 50))

    # Use DataFrame so ColumnTransformer can select by column names
    X = pd.DataFrame(
        [[subject, topic_length, self_rating, past_score]],
        columns=["subject", "topic_length", "self_rating", "past_score"],
    )

    try:
        diff_enc = difficulty_model.predict(X)[0]
        diff = diff_label_encoder.inverse_transform([diff_enc])[0]
    except Exception as e:
        print("DIFFICULTY ERROR:", repr(e))
        return jsonify({"error": "difficulty prediction failed", "detail": str(e)}), 500

    try:
        time_needed = time_model.predict(X)[0]
    except Exception as e:
        print("TIME ERROR:", repr(e))
        return jsonify({"error": "time prediction failed", "detail": str(e)}), 500

    return jsonify({
        "difficulty": str(diff),
        "time_needed_hours": round(float(time_needed), 2)
    })


@app.get("/test_predict")
def test_predict():
    X = pd.DataFrame(
        [["Maths", 5, 3, 80]],
        columns=["subject", "topic_length", "self_rating", "past_score"],
    )
    diff_enc = difficulty_model.predict(X)[0]
    diff = diff_label_encoder.inverse_transform([diff_enc])[0]
    time_needed = time_model.predict(X)[0]
    return {
        "difficulty": str(diff),
        "time_needed_hours": round(float(time_needed), 2)
    }


if __name__ == "__main__":
    app.run(debug=True)
