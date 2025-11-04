from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

class TimeEntryCreate(BaseModel):
    task_id: UUID
    description: Optional[str] = None

class TimeEntry(BaseModel):
    id: int
    task_id: UUID
    user_id: UUID
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None  # seconds
    description: Optional[str] = None
    project_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

class TimeEntryResponse(BaseModel):
    id: int
    task_id: UUID
    start_time: datetime
    status: str  # "running" or "stopped"
