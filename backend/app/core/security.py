"""
JWT & password security utilities.

Design decisions (documented as per SPEC §11):
- Passwords: bcrypt via passlib — industry standard, auto-salts.
- Tokens: HS256 JWT.  Access tokens are short-lived (30 min default).
  Refresh tokens are long-lived (7 days) and stored hashed in the DB so
  token rotation can invalidate old ones on reuse.
- Confidence formula (used in agent layer, documented here for clarity):
    confidence = 0.6 * retrieval_confidence + 0.4 * generation_confidence
  where each sub-score is in [0, 1].  Display as a percentage or badge.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ── Password hashing ──────────────────────────────────────────────────────────
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


# ── JWT token helpers ─────────────────────────────────────────────────────────
def _create_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    payload.update({"exp": expire})
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_access_token(user_id: int) -> str:
    return _create_token(
        {"sub": str(user_id), "type": "access"},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: int) -> str:
    return _create_token(
        {"sub": str(user_id), "type": "refresh"},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_access_token(token: str) -> Optional[int]:
    """Returns user_id if valid, None if expired/invalid."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "access":
            return None
        sub = payload.get("sub")
        return int(sub) if sub else None
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[int]:
    """Returns user_id if valid refresh token, None otherwise."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "refresh":
            return None
        sub = payload.get("sub")
        return int(sub) if sub else None
    except JWTError:
        return None
