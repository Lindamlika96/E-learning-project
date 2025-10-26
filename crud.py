from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from schemas import UserCreate, UserOut
from auth import get_password_hash
from typing import List
from IA.predict_signup import predict_signup  # 👈 ton modèle IA

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def permissions_to_string(permissions: List[str]) -> str:
    return ",".join(permissions)

@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # 🔍 Vérification IA avant création
    risk = predict_signup(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        time_to_submit_ms=6000  # tu peux calculer côté front si tu veux
    )

    if risk["decision"] == "block":
        raise HTTPException(status_code=400, detail="❌ Faux compte détecté par l'IA")

    if risk["decision"] == "review":
        raise HTTPException(status_code=400, detail="⚠️ Compte suspect, en révision IA")

    # 🔒 Vérifie si username déjà utilisé
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")

    # ✅ Création du compte si IA dit "allow"
    db_user = User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        role=user.role,
        permissions=permissions_to_string(user.permissions)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
