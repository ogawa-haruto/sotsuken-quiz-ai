from fastapi import Depends, HTTPException, status, Header
from jose import jwt, JWTError
from pydantic import BaseModel
import os

JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALG = "HS256"

class CurrentUser(BaseModel):
    id: int
    email: str | None = None

def get_current_user(authorization: str | None = Header(None)) -> CurrentUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        uid = payload.get("sub") or payload.get("user_id")
        email = payload.get("email")
        if uid is None:
            raise ValueError("no sub")
        return CurrentUser(id=int(uid), email=email)
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
