from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ── Register ──────────────────────────────────────────────────────────────────
class UserRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


# ── Login ─────────────────────────────────────────────────────────────────────
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ── Responses ─────────────────────────────────────────────────────────────────
class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessTokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
