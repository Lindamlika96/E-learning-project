import joblib, json, pandas as pd
from IA.feature_builder import build_features

# Charger modèle et fichiers associés
model = joblib.load("IA/signup_risk_model.joblib")

with open("IA/feature_names.json") as f:
    feature_names = json.load(f)

with open("IA/signup_risk_thresholds.json") as f:
    thresholds = json.load(f)

def predict_risk(user: dict) -> dict:
    feats = build_features(
        username=user["username"],
        email=user["email"],
        full_name=user.get("full_name", ""),
        time_to_submit_ms=user.get("time_to_submit_ms", 60000)
    )
    X = pd.DataFrame([feats])[feature_names]
    proba = model.predict_proba(X)[0][1]

    if proba >= thresholds["T_BLOCK"]:
        status, decision = "Frauduleux", "block"
    elif proba >= thresholds["T_REVIEW"]:
        status, decision = "Suspect", "review"
    else:
        status, decision = "Normal", "allow"

    return {"score": round(float(proba), 3), "status": status, "decision": decision}
