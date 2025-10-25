# app/api_ai.py
from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

router = APIRouter(prefix="/api/ai", tags=["ai"])

@router.post("/predict_dropout")
def predict_dropout_stub(user_id: int, course_id: int):
    """Stub - On branchera le modèle après entraînement (scripts/)."""
    model_path = Path("data/model_dropout.joblib")
    if not model_path.exists():
        raise HTTPException(status_code=400, detail="Modèle non entraîné. Lance d'abord les scripts ML.")
    return {"status": "ok", "user_id": user_id, "course_id": course_id, "risk": 0.42}
