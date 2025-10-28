"""
Task data models for APOLLO.

Tasks are daily/weekly actions that optionally link to milestones.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Task(BaseModel):
    """Complete task model with all database fields."""
    id: Optional[str] = None  # UUID from database
    user_id: str  # UUID of the user who owns the task
    title: str  # Title of the task
    description: Optional[str] = None  # Detailed description
    status: str = "pending"  # Task status: pending, in_progress, completed
    milestone_id: Optional[str] = None  # Links to parent milestone (NEW)
    project: Optional[str] = None  # Project grouping (NEW)
    priority: str = "medium"  # Task priority: high, medium, low (NEW)
    created_at: Optional[datetime] = None  # Timestamp of creation
    updated_at: Optional[datetime] = None  # Timestamp of last update


class TaskUpdate(BaseModel):
    """Model for partial task updates (PATCH /tasks/{id})."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    milestone_id: Optional[str] = None  # NEW
    project: Optional[str] = None  # NEW
    priority: Optional[str] = None  # NEW
