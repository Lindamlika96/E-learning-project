"""Routes pour les utilisateurs (users)."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from database.session import get_connection
import json
import os

router = APIRouter()


class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None


@router.get("/users", response_model=List[User])
def list_users() -> List[User]:
    """Retourne tous les utilisateurs depuis la table users (si existante)."""
    with get_connection() as conn:
        cur = conn.execute("SELECT id, username, email, full_name FROM users ORDER BY id")
        rows = cur.fetchall()
        if rows:
            return [User(**dict(r)) for r in rows]

    # fallback JSON
    jpath = os.path.join("data", "users.json")
    if os.path.exists(jpath):
        with open(jpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [User(**u) for u in data]
    return []


@router.get("/users/{user_id}", response_model=User)
def get_user(user_id: int) -> User:
    """Retourne un utilisateur par id (404 si absent)."""
    with get_connection() as conn:
        cur = conn.execute("SELECT id, username, email, full_name FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        return User(**dict(row))


if __name__ == "__main__":
    print("OK - users_api chargé")
