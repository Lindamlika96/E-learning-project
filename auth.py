from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import List
from IA.ml_model import predict_risk

from models import User, AdminLog
from database import SessionLocal
from schemas import (
    UserCreate,
    UsernameRequest,
    VerificationRequest,
    UserOut,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    SignupInput
)
from utils.email_welcome import send_welcome_email
from utils.email_verification import generate_code, send_code
from utils.email_reset import generate_reset_code, send_reset_code

router = APIRouter()

# ------------------ Auth config ------------------
SECRET_KEY = "secretkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
CODE_EXPIRATION_MINUTES = 10
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# ------------------ DB dependency ------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------ Utils ------------------
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password[:72])

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain[:72], hashed)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ------------------ Auth routes ------------------

@router.post("/users/", tags=["Auth"], status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    hashed_password = get_password_hash(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=user.role,
        permissions=",".join(user.permissions),
        is_verified=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Envoi d’email de bienvenue
    try:
        send_welcome_email(new_user.email, new_user.username)
    except Exception as e:
        print("❌ Erreur email bienvenue :", e)

    return {"message": "✅ Compte créé. Bienvenue !"}

@router.post("/login", tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut, tags=["Auth"])
def get_current_user_info(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token invalide")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_verified": user.is_verified,
        "permissions_list": user.permissions.split(",") if user.permissions else []
    }

# ------------------ Admin routes ------------------

@router.get("/users/all", response_model=List[UserOut], tags=["Admin"])
def get_all_users(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        if role != "admin":
            raise HTTPException(status_code=403, detail="⛔ Accès refusé")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_verified": u.is_verified,
            "permissions_list": u.permissions.split(",") if u.permissions else []
        }
        for u in users
    ]

@router.delete("/users/{user_id}", tags=["Admin"])
def delete_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="⛔ Accès refusé")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    db.delete(user)
    db.commit()
    return {"message": "✅ Utilisateur supprimé"}

@router.put("/users/{user_id}", tags=["Admin"])
def update_user(user_id: int, updated: dict, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="⛔ Accès refusé")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    # Merge simple des champs autorisés
    for key in ["email", "full_name", "role", "permissions"]:
        if key in updated:
            setattr(user, key, updated[key] if key != "permissions" else ",".join(updated[key]))
    db.commit()
    db.refresh(user)

    return {"message": "✅ Utilisateur mis à jour"}

@router.put("/users/{user_id}/verify", tags=["Admin"])
def verify_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="⛔ Accès refusé")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    user.is_verified = True
    db.commit()
    return {"message": "✅ Compte vérifié"}

@router.get("/users/stats", tags=["Admin"])
def user_stats(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="⛔ Accès refusé")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

    total = db.query(User).count()
    verified = db.query(User).filter(User.is_verified == True).count()
    unverified = total - verified

    by_role = {
        "admin": db.query(User).filter(User.role == "admin").count(),
        "teacher": db.query(User).filter(User.role == "teacher").count(),
        "student": db.query(User).filter(User.role == "student").count()
    }

    return {
        "total": total,
        "verified": verified,
        "unverified": unverified,
        "roles": by_role,
        "verification_rate": round((verified / total) * 100, 2) if total > 0 else 0
    }

@router.get("/admin/logs", tags=["Admin"])
def get_admin_logs(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="⛔ Accès refusé")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

    logs = db.query(AdminLog).order_by(AdminLog.timestamp.desc()).limit(100).all()
    return [
        {
            "id": log.id,
            "admin_id": log.admin_id,
            "action": log.action,
            "target_user_id": log.target_user_id,
            "timestamp": log.timestamp,
            "details": log.details
        }
        for log in logs
    ]

# ------------------- IA: scoring d'inscription -------------------

@router.post("/users/risk-ml", tags=["ML"])
def check_signup_risk(payload: SignupInput):
    return predict_risk(payload.dict())
