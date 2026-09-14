from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.db import get_db
from app.models.user import User
from app.rate_limit import limiter
from app.schemas import LoginRequest, SignupRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse)
@limiter.limit("5/minute")
def signup(request: Request, body: SignupRequest, db: Session = Depends(get_db)) -> TokenResponse:
    email = body.email.strip().lower()
    user = User(email=email, password_hash=hash_password(body.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id), user=UserOut(id=user.id, email=user.email))


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    email = body.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(user.id), user=UserOut(id=user.id, email=user.email))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut(id=current_user.id, email=current_user.email)
