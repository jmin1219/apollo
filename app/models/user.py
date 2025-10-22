from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class User(BaseModel):
    id: Optional[str] = None  # UUID from database
    email: EmailStr  # Validated email address
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None