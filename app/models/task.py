from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Task(BaseModel):
    id: Optional[str] = None  # UUID from database
    user_id: str  # UUID of the user who owns the task
    title: str  # Title of the task
    description: Optional[str] = None  # Detailed description
    status: str = "pending"  # Task status: pending, in-progress, completed
    created_at: Optional[datetime] = None  # Timestamp of creation
    updated_at: Optional[datetime] = None  # Timestamp of last update


# New model for updates - all fields optional!
class TaskUpdate(BaseModel):
    user_id: Optional[str] = None  # Optional for update
    title: Optional[str] = None  # Optional for update
    description: Optional[str] = None
    status: Optional[str] = None
