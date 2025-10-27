# routes/ml.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from enum import Enum
import numpy as np
import json
import os
import joblib

# -------- Enums identiques au backend --------
class VilleTunisie(str, Enum):
    Tunis = "Tunis"
    Sfax = "Sfax"
    Sousse = "Sousse"
    Kairouan = "Kairouan"
    Bizerte = "Bizerte"
    Gabès = "Gabès"
    Ariana = "Ariana"

class Importance(str, Enum):
    Tres_peu = "Très peu"
    Peu = "Peu"
    Moyen = "Moyen"
    Important = "Important"
    Tres_important = "Très important"
    Extra_event = "Événement extraordinaire"

class Exigeance(str, Enum):
    E_Tres_peu = "Très peu"
    E_Peu = "Peu"
    E_Moyen = "Moyen"
    E_Important = "Important"
    E_Tres_important = "Très important"
    E_Extraordinaire = "Extraordinaire"

class Formateur(str, Enum):
    Eleve_Univ = "Élève Université"
    Etudiant_benevole = "Étudiant bénévole"
    Prof_Univ = "Professeur Université"
    Expert = "Expert"
    PDG = "PDG"

# -------- Schéma d'entrée brute (côté formulaire React) --------
class PredictPayload(BaseModel):
    titre: str = Field(min_length=1)               # ignoré par le modèle (mais utile UI)
    description: str | None = None                 # ignoré par le modèle
    localisation: VilleTunisie
    date: str = Field(min_length=10)               # ignoré par le modèle
    duree_jours: int = Field(ge=1)
    nombre_places: int = Field(ge=1)
    niveau_importance: Importance
    niveau_exigeance: Exigeance
    formateur: Formateur

# -------- Mappings utilisés à l'entraînement --------
map_localisation = {
    "Tunis": 1, "Sfax": 2, "Sousse": 3, "Kairouan": 4, "Bizerte": 5, "Gabès": 6, "Ariana": 7
}
map_importance = {
    "Très peu": 1, "Peu": 2, "Moyen": 3, "Important": 4, "Très important": 5, "Événement extraordinaire": 6
}
map_exigeance = {
    "Très peu": 1, "Peu": 2, "Moyen": 3, "Important": 4, "Très important": 5, "Extraordinaire": 6
}
map_formateur = {
    "Élève Université": 1, "Étudiant bénévole": 2, "Professeur Université": 3, "Expert": 4, "PDG": 5
}

# -------- Chargement modèle / scaler / feature order --------
ARTIF_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")
MODEL_PATH = os.path.abspath(os.path.join(ARTIF_DIR, "best_model_succes.pkl"))
METRICS_PATH = os.path.abspath(os.path.join(ARTIF_DIR, "metrics_best_model.json"))
SCALER_PATH = os.path.abspath(os.path.join(ARTIF_DIR, "scaler.pkl"))  # optionnel si RF/XGB

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Impossible de charger le modèle: {e}")

feature_order = None
try:
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)
        feature_order = meta.get("features")  # liste ordonnée des features à l'entraînement
except Exception as e:
    raise RuntimeError(f"Impossible de lire metrics_best_model.json: {e}")

scaler = None
if os.path.exists(SCALER_PATH):
    try:
        scaler = joblib.load(SCALER_PATH)
    except Exception as e:
        raise RuntimeError(f"Impossible de charger le scaler.pkl: {e}")

router = APIRouter(prefix="/ml", tags=["ml"])

def preprocess(payload: PredictPayload) -> np.ndarray:
    """
    Encode les catégories puis ordonne les features selon feature_order.
    Applique le scaler si disponible.
    """
    raw = {
        "duree_jours": payload.duree_jours,
        "nombre_places": payload.nombre_places,
        "localisation": map_localisation[payload.localisation.value],
        "niveau_importance": map_importance[payload.niveau_importance.value],
        "niveau_exigeance": map_exigeance[payload.niveau_exigeance.value],
        "formateur": map_formateur[payload.formateur.value],
    }

    if feature_order is None:
        raise HTTPException(status_code=500, detail="Ordre des features introuvable.")

    x = np.array([raw[col] for col in feature_order], dtype=float).reshape(1, -1)

    # si scaler disponible, on transforme (utile pour LogisticRegression)
    if scaler is not None:
        x = scaler.transform(x)

    return x

@router.post("/predict")
def predict(payload: PredictPayload):
    """
    Renvoie la probabilité de succès et la classe prédite.
    """
    x = preprocess(payload)
    if hasattr(model, "predict_proba"):
        proba = float(model.predict_proba(x)[:, 1][0])
    else:
        # fallback pour modèles sans proba
        score = float(model.decision_function(x).ravel()[0])
        # transformation sigmoïde de secours
        proba = 1.0 / (1.0 + np.exp(-score))

    label = bool(proba >= 0.5)
    return {
        "success_probability": proba,
        "predicted_label": label,
        "features_order": feature_order
    }
