"""
Milestone data models for APOLLO.

Milestones represent quarterly checkpoints under goals.
Example: "APOLLO portfolio deployment" → SWE job goal
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class MilestoneBase(BaseModel):
    """Base milestone fields shared across operations."""
    title: str = Field(..., max_length=200, description="Milestone title")
    description: Optional[str] = Field(None, description="Detailed description")
    goal_id: Optional[str] = Field(None, description="Parent goal UUID (optional)")
    target_date: Optional[date] = Field(None, description="Target completion date")
    status: str = Field(default="not_started", description="Status: not_started, in_progress, completed, blocked")
    progress: int = Field(default=0, ge=0, le=100, description="Completion percentage 0-100")


class MilestoneCreate(MilestoneBase):
    """Model for creating a new milestone (POST /milestones)."""
    pass


class MilestoneUpdate(BaseModel):
    """Model for updating an existing milestone (PATCH /milestones/{id})."""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    goal_id: Optional[str] = None
    target_date: Optional[date] = None
    status: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0, le=100)


class Milestone(MilestoneBase):
    """Complete milestone model with database fields."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
