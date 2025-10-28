"""
Goal data models for APOLLO.

Goals represent yearly vision-level objectives with deadlines.
Example: "SWE visa-sponsored job by Spring 2027"
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class GoalBase(BaseModel):
    """Base goal fields shared across operations."""
    title: str = Field(..., max_length=200, description="Goal title")
    description: Optional[str] = Field(None, description="Detailed description")
    target_date: Optional[date] = Field(None, description="Target completion date")
    status: str = Field(default="active", description="Goal status: active, achieved, abandoned")


class GoalCreate(GoalBase):
    """Model for creating a new goal (POST /goals)."""
    pass


class GoalUpdate(BaseModel):
    """Model for updating an existing goal (PATCH /goals/{id})."""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    target_date: Optional[date] = None
    status: Optional[str] = None


class Goal(GoalBase):
    """Complete goal model with database fields."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
