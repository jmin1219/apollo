"""
Conversation models for APOLLO chat persistence.

Models:
    - Conversation: Full conversation with metadata
    - ConversationCreate: For creating new conversations
    - ConversationUpdate: For updating conversation title
    - ConversationWithMessages: Conversation with message list
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ConversationBase(BaseModel):
    """Base conversation fields."""
    title: Optional[str] = Field(None, max_length=100)


class ConversationCreate(ConversationBase):
    """
    Create new conversation.

    Title is optional - will auto-generate from first message if not provided.
    """
    title: Optional[str] = Field(None, max_length=100)


class ConversationUpdate(BaseModel):
    """
    Update conversation (only title is modifiable).
    """
    title: str = Field(..., min_length=1, max_length=100)


class Conversation(ConversationBase):
    """
    Full conversation model.

    Fields:
        id: UUID primary key
        user_id: Owner of conversation
        title: Auto-generated or user-set title
        created_at: When conversation started
        updated_at: Last message timestamp (for sorting)
    """
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationListItem(BaseModel):
    """
    Lightweight conversation for list view.

    Includes message count for preview.
    """
    id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int = 0  # Computed from messages table

    class Config:
        from_attributes = True
