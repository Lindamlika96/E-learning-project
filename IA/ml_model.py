import os
import joblib
import json
import pandas as pd
from IA.feature_builder import build_features

# 📁 Déterminer le chemin absolu du dossier IA
IA_DIR = os.path.dirname(__file__)

# 📦 Charger le modèle
model_path = os.path.join(IA_DIR, "signup_risk_model.joblib")
model = joblib.load(model_path)

# 📄 Charger les noms de features
with open(os.path.join(IA_DIR, "feature_names.json")) as f:
    feature_names = json.load(f)

# 📄 Charger les seuils de décision
with open(os.path.join(IA_DIR, "signup_risk_thresholds.json")) as f:
    thresholds = json.load(f)

def predict_risk(user: dict) -> dict:
    """Prédit le risque d'un utilisateur à partir de ses données"""
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

    return {
        "score": round(float(proba), 3),
        "status": status,
        "decision": decision
    }
