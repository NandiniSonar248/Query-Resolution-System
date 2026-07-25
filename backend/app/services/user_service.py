"""
FastAPI dependency for protecting routes with JWT auth.

Usage:
    from app.services.user_service import get_current_user
    @router.get("/me")
    def me(user = Depends(get_current_user)):
        ...
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    decode_access_token, decode_refresh_token,
)
from app.models.user import User
from app.schemas.auth import UserRegister

_bearer = HTTPBearer()


# ── Auth helpers ──────────────────────────────────────────────────────────────
def register_user(payload: UserRegister, db: Session) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )
    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(email: str, password: str, db: Session) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled.",
        )
    return user


def issue_tokens(user: User, db: Session) -> dict:
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    # Store hashed refresh token for rotation validation
    user.refresh_token_hash = hash_password(refresh)
    db.commit()
    return {"access_token": access, "refresh_token": refresh}


def rotate_refresh_token(refresh_token: str, db: Session) -> dict:
    user_id = decode_refresh_token(refresh_token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.refresh_token_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked.")
    if not verify_password(refresh_token, user.refresh_token_hash):
        # Possible token reuse — revoke all
        user.refresh_token_hash = None
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token reuse detected.")
    return issue_tokens(user, db)


def logout_user(user_id: int, db: Session) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.refresh_token_hash = None
        db.commit()


# ── FastAPI dependency ────────────────────────────────────────────────────────
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    return user
