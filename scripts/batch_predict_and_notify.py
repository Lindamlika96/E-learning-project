# scripts/batch_predict_and_notify.py
import os
import json
import logging
from datetime import datetime, timezone
import pandas as pd
import joblib
from sqlmodel import Session, SQLModel, create_engine, select
from models.at_risk import StudentAtRisk

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("predict")

# Chemins
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FEATURES_PATH = os.path.join(DATA_DIR, "features.csv")
MODEL_PATH = os.path.join(DATA_DIR, "model_dropout.joblib")
MANIFEST_PATH = os.path.join(DATA_DIR, "model_manifest.json")
COURSES_JSON = os.path.join(DATA_DIR, "courses.json")

# Configuration SQLite
DATABASE_URL = "sqlite:///data/app.db"
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

# Seuils
THRESHOLD_WATCH = 0.65
THRESHOLD_CRITICAL = 0.80

def get_risk_status(score: float) -> str:
    """Détermine le statut de risque basé sur le score."""
    if score > THRESHOLD_CRITICAL:
        return "Critique"
    elif score >= THRESHOLD_WATCH:
        return "À surveiller"
    return "Normal"

def load_courses():
    """Charge les informations des cours."""
    try:
        with open(COURSES_JSON, "r", encoding="utf-8") as f:
            return {str(c["course_id"]): c for c in json.load(f)}
    except Exception as e:
        logger.error(f"Erreur chargement cours: {e}")
        return {}

def main():
    # Charger et vérifier les features
    if not os.path.exists(FEATURES_PATH):
        raise SystemExit("Features manquantes.")
        
    df = pd.read_csv(FEATURES_PATH)
    if df.empty:
        raise SystemExit("Features vides.")

    # Charger le modèle
    model = joblib.load(MODEL_PATH)
    with open(MANIFEST_PATH, "r") as f:
        manifest = json.load(f)
    feat_cols = manifest["feature_columns"]
    
    # Charger les informations des cours
    courses = load_courses()

    # Prédictions
    if hasattr(model[-1], "predict_proba"):
        proba = model.predict_proba(df[feat_cols])[:, 1]
    else:
        import numpy as np
        raw = model.decision_function(df[feat_cols])
        proba = 1 / (1 + np.exp(-raw))

    # Session BD
    with Session(engine) as session:
        updated = 0
        for i, row in df.iterrows():
            score = float(proba[i])
            
            # Vérifier seuil
            if score < THRESHOLD_WATCH:
                continue

            # Récupérer infos cours
            course_id = str(row.get("course_id", "0"))
            course = courses.get(course_id, {
                "title": f"Cours {course_id}",
                "tutor": "Non assigné"
            })

            # Créer/mettre à jour l'enregistrement
            student_at_risk = StudentAtRisk(
                student_id=int(row.get("user_id", 1)),
                student_name=f"Étudiant {row.get('user_id', 1)}",  # À remplacer par le vrai nom
                course_id=hash(course_id) % (2**31),  # Génère un ID numérique stable à partir du course_id
                course_name=course["title"],
                abandon_score=score,
                predicted_at=datetime.now(timezone.utc),
                status=get_risk_status(score)
            )

            # Upsert (mise à jour si existe, sinon création)
            stmt = select(StudentAtRisk).where(
                StudentAtRisk.student_id == student_at_risk.student_id,
                StudentAtRisk.course_id == student_at_risk.course_id
            )
            existing = session.exec(stmt).first()
            
            if existing:
                for key, value in student_at_risk.dict(exclude={"id"}).items():
                    setattr(existing, key, value)
            else:
                session.add(student_at_risk)
            
            updated += 1

        session.commit()
        logger.info(f"Prédictions mises à jour : {updated}")

if __name__ == "__main__":
    main()