from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from auth import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalide")
    return payload

def require_role(role: str):
    def role_checker(user=Depends(get_current_user)):
        if user["role"] != role:
            raise HTTPException(status_code=403, detail="Accès interdit")
        return user
    return role_checker

def require_permission(permission: str):
    def permission_checker(user=Depends(get_current_user)):
        perms = user.get("permissions", "")
        if permission not in perms.split(","):
            raise HTTPException(status_code=403, detail="Permission refusée")
        return user
    return permission_checker
