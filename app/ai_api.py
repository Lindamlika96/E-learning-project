"""Endpoints AI : prédiction 'what-if' et suivi des étudiants à risque."""

from fastapi import APIRouter, HTTPException
from fastapi.routing import APIRouter
from pydantic import BaseModel
from typing import Optional
import os
import joblib
import numpy as np
from .at_risk_api import router as at_risk_router

router = APIRouter()
router.include_router(at_risk_router, tags=["at-risk"])
MODEL_PATH = os.path.join("data", "model_dropout.joblib")


class FeaturesRow(BaseModel):
    user_id: int
    course_id: int
    percent_complete: float
    time_spent_hours: float
    pages_viewed: int
    num_sessions_last7: int
    annotations_count: int
    days_since_last_activity: int


@router.post("/ai/predict_dropout")
def predict_dropout(row: FeaturesRow):
    """
    Prédit un score de risque d'abandon pour une ligne de features.
    Si le modèle sklearn n'existe pas, renvoie une heuristique simple.
    """
    x = np.array(
        [
            [
                row.percent_complete,
                row.time_spent_hours,
                row.pages_viewed,
                row.num_sessions_last7,
                row.annotations_count,
                row.days_since_last_activity,
            ]
        ]
    )

    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            proba = model.predict_proba(x)[:, 1].tolist()[0]
            return {"user_id": row.user_id, "course_id": row.course_id, "dropout_score": float(proba)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur modèle: {e}")

    # Heuristique si pas de modèle : faible completion → score élevé
    score = max(0.0, min(1.0, 1.0 - (row.percent_complete / 100.0)))
    return {"user_id": row.user_id, "course_id": row.course_id, "dropout_score": float(score)}
