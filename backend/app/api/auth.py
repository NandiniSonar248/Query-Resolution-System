from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.auth import (
    UserRegister, UserLogin, TokenOut, UserOut,
    RefreshRequest, AccessTokenOut,
)
from app.services.user_service import (
    register_user, authenticate_user, issue_tokens,
    rotate_refresh_token, logout_user, get_current_user,
)
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """Register a new user and return access + refresh tokens."""
    user = register_user(payload, db)
    tokens = issue_tokens(user, db)
    return TokenOut(user=UserOut.model_validate(user), **tokens)


@router.post("/login", response_model=TokenOut)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """Login with email + password, receive access + refresh tokens."""
    user = authenticate_user(payload.email, payload.password, db)
    tokens = issue_tokens(user, db)
    return TokenOut(user=UserOut.model_validate(user), **tokens)


@router.post("/refresh", response_model=AccessTokenOut)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    """Rotate refresh token and return a new access token."""
    tokens = rotate_refresh_token(payload.refresh_token, db)
    return AccessTokenOut(access_token=tokens["access_token"])


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Revoke current user's refresh token."""
    logout_user(current_user.id, db)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user
