import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"

FEATURE_NAMES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal",
]

FIELD_META = {
    "age": {
        "label": "Age",
        "unit": "years",
        "help": "Patient age at the time of assessment.",
        "type": "number", "min": 1, "max": 120, "step": 1,
    },
    "sex": {
        "label": "Sex",
        "unit": "",
        "help": "Select the value used by the training dataset.",
        "type": "select",
        "options": [(1, "Male"), (0, "Female")],
    },
    "cp": {
        "label": "Chest Pain Type",
        "unit": "",
        "help": "Choose the chest-pain category that best matches the record.",
        "type": "select",
        "options": [
            (0, "Typical angina"),
            (1, "Atypical angina"),
            (2, "Non-anginal pain"),
            (3, "Asymptomatic"),
        ],
    },
    "trestbps": {
        "label": "Resting Blood Pressure",
        "unit": "mm Hg",
        "help": "Resting systolic blood pressure.",
        "type": "number", "min": 60, "max": 260, "step": 1,
    },
    "chol": {
        "label": "Serum Cholesterol",
        "unit": "mg/dl",
        "help": "Serum cholesterol level.",
        "type": "number", "min": 100, "max": 700, "step": 1,
    },
    "fbs": {
        "label": "Fasting Blood Sugar",
        "unit": "> 120 mg/dl",
        "help": "Whether fasting blood sugar is above 120 mg/dl.",
        "type": "select",
        "options": [(0, "No"), (1, "Yes")],
    },
    "restecg": {
        "label": "Resting ECG",
        "unit": "",
        "help": "Resting electrocardiographic result.",
        "type": "select",
        "options": [
            (0, "Normal"),
            (1, "ST-T wave abnormality"),
            (2, "Left ventricular hypertrophy"),
        ],
    },
    "thalach": {
        "label": "Maximum Heart Rate",
        "unit": "bpm",
        "help": "Maximum heart rate achieved during exercise.",
        "type": "number", "min": 60, "max": 250, "step": 1,
    },
    "exang": {
        "label": "Exercise-Induced Angina",
        "unit": "",
        "help": "Whether exercise produces angina.",
        "type": "select",
        "options": [(0, "No"), (1, "Yes")],
    },
    "oldpeak": {
        "label": "ST Depression",
        "unit": "oldpeak",
        "help": "ST depression induced by exercise relative to rest.",
        "type": "number", "min": 0, "max": 10, "step": 0.1,
    },
    "slope": {
        "label": "Peak Exercise ST Slope",
        "unit": "",
        "help": "Slope of the peak exercise ST segment.",
        "type": "select",
        "options": [
            (0, "Upsloping"),
            (1, "Flat"),
            (2, "Downsloping"),
        ],
    },
    "ca": {
        "label": "Major Vessels",
        "unit": "0–4",
        "help": "Number of major vessels colored by fluoroscopy.",
        "type": "select",
        "options": [(0, "0"), (1, "1"), (2, "2"), (3, "3"), (4, "4")],
    },
    "thal": {
        "label": "Thalassemia",
        "unit": "",
        "help": "Thalassemia status encoded in the supplied dataset.",
        "type": "select",
        "options": [
            (0, "Unknown / dataset code 0"),
            (1, "Normal"),
            (2, "Fixed defect"),
            (3, "Reversible defect"),
        ],
    },
}

FIELD_LIST = [{"name": name, **FIELD_META[name]} for name in FEATURE_NAMES]

MODEL = joblib.load(MODEL_DIR / "heartrf.joblib")


def _predict(values):
    row = pd.DataFrame(
        [{f: float(values[f]) for f in FEATURE_NAMES}],
        columns=FEATURE_NAMES,
    )
    prediction = int(MODEL.predict(row)[0])
    confidence = None
    if hasattr(MODEL, "predict_proba"):
        confidence = float(np.max(MODEL.predict_proba(row)[0]))
    return prediction, confidence


def _form_context(**extra):
    context = {"fields": FIELD_LIST, "feature_order": FEATURE_NAMES}
    context.update(extra)
    return context


def index(request):
    return render(
        request,
        "index.html",
        {"model_name": type(MODEL).__name__, "feature_count": len(FEATURE_NAMES)},
    )


def predict(request):
    if request.method == "GET":
        return render(request, "predict.html", _form_context())

    values = {}
    for field in FIELD_LIST:
        name = field["name"]
        raw = request.POST.get(name, "")
        try:
            values[name] = float(raw)
        except (TypeError, ValueError):
            return render(
                request,
                "predict.html",
                _form_context(
                    error=f"Please enter a valid value for {field['label']}.",
                    submitted=request.POST,
                ),
            )

    prediction, confidence = _predict(values)

    return render(
        request,
        "result.html",
        {
            "result_label": (
                "Heart disease indicated"
                if prediction == 1
                else "No heart disease indicated"
            ),
            "risk_level": "high" if prediction == 1 else "low",
            "confidence": round((confidence or 0) * 100, 1),
            "values": values,
            "fields": FIELD_LIST,
            "feature_order": FEATURE_NAMES,
        },
    )


def about(request):
    metrics_path = MODEL_DIR / "metrics.txt"
    metrics_text = (
        metrics_path.read_text(encoding="utf-8")
        if metrics_path.exists()
        else "Metrics file not found."
    )
    return render(
        request,
        "about.html",
        {"metrics_text": metrics_text, "fields": FIELD_LIST},
    )


def api_predict(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        values = {f: float(data[f]) for f in FEATURE_NAMES}
        prediction, confidence = _predict(values)
        return JsonResponse(
            {
                "prediction": prediction,
                "label": (
                    "Heart disease indicated"
                    if prediction == 1
                    else "No heart disease indicated"
                ),
                "confidence": confidence,
            }
        )
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)
