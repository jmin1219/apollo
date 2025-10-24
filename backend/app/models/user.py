from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class User(BaseModel):
    """Internal user model (includes password hash)"""
    id: Optional[str] = None  # UUID from database
    email: EmailStr  # Validated email address
    hashed_password: Optional[str] = None  # Hashed password string; NEVER return in API
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserPublic(BaseModel):
    """API response model (no password)"""
    id: str
    email: EmailStr
    created_at: datetime

class UserCreate(BaseModel):
    """Registration request model"""
    email: EmailStr
    password: str  # Plaintext password; will be hashed before storage

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
