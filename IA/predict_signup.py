import os
import joblib
import json
import pandas as pd

from IA.feature_builder import build_features

# Toujours calculer le chemin absolu du dossier IA
BASE_DIR = os.path.dirname(__file__)

# Charger le modèle et les seuils depuis IA/
model = joblib.load(os.path.join(BASE_DIR, "signup_risk_model.joblib"))
with open(os.path.join(BASE_DIR, "signup_risk_thresholds.json"), "r") as f:
    thresholds = json.load(f)

def predict_signup(username: str, email: str, full_name: str, time_to_submit_ms: int):
    """
    Transforme les infos utilisateur en features via build_features,
    applique le modèle ML et retourne allow / review / block.
    """
    # Construire les features avec ta fonction
    features = build_features(username, email, full_name, time_to_submit_ms)

    # Convertir en DataFrame pour sklearn
    X = pd.DataFrame([features])
    p = float(model.predict_proba(X)[0, 1])

    if p >= thresholds["T_BLOCK"]:
        decision = "block"
    elif p >= thresholds["T_REVIEW"]:
        decision = "review"
    else:
        decision = "allow"

    return {"decision": decision, "score": round(p, 4)}
