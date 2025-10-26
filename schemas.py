from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, validator

# 🆕 Création d'utilisateur
class UserCreate(BaseModel):
    username: str
    email: Optional[str]
    full_name: str
    password: str
    role: str = "student"
    permissions: List[str] = ["view_courses"]

    @validator("username")
    def no_spaces_in_username(cls, v):
        if " " in v:
            raise ValueError("Le nom d'utilisateur ne doit pas contenir d'espaces")
        return v

    @validator("password")
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError("Le mot de passe doit contenir au moins 6 caractères")
        return v

    @validator("role")
    def role_must_be_valid(cls, v):
        valid_roles = ["admin", "teacher", "student"]
        if v not in valid_roles:
            raise ValueError(f"Le rôle doit être parmi : {', '.join(valid_roles)}")
        return v

# 👤 Schéma de sortie utilisateur
class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[str]
    full_name: Optional[str]
    role: str
    permissions: List[str] = Field(..., alias="permissions_list")
    is_verified: bool

    class Config:
        from_attributes = True  # ✅ Pydantic v2

# 📩 Vérification du compte
class VerificationRequest(BaseModel):
    username: str
    code: str

# 🔁 Renvoi du code
class UsernameRequest(BaseModel):
    username: str

# 🔐 Mot de passe oublié avec CAPTCHA
class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    captcha_token: str

# 🔐 Réinitialisation du mot de passe
class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str

# 🔍 IA – Scoring d'inscription
class SignupInput(BaseModel):
    username: str = Field(..., example="xxkiller")
    email: str = Field(..., example="user@yopmail.com")
    full_name: str = Field(..., example="xXx_killer_xXx")
    time_to_submit_ms: float = Field(60000.0, example=2500.0)

    class Config:
        from_attributes = True
