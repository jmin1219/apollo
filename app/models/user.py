from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: Optional[str] = None  # UUID from database
    email: EmailStr  # Validated email address
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
