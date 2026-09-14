from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.user import User

JWT_ALGORITHM = "HS256"
JWT_EXPIRES_DAYS = 30


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRES_DAYS),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def _decode_user_id(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        return None


def _bearer_token(request: Request) -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.removeprefix("Bearer ").strip()


# Strict dependency: requires a valid, currently-logged-in user. Used by routes where being
# logged in is inherently the point (viewing your own account, your own persisted history).
def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = _bearer_token(request)
    if token is None:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    user_id = _decode_user_id(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# Lenient counterpart: never raises, just resolves to None on a missing/invalid/expired token or
# unknown user. Used by routes that work fine logged-out but add something (persisted history)
# when a valid session is present.
def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> User | None:
    token = _bearer_token(request)
    if token is None:
        return None
    user_id = _decode_user_id(token)
    if user_id is None:
        return None
    return db.get(User, user_id)
