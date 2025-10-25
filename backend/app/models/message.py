"""
Message models for APOLLO chat persistence.

Models:
    - Message: Individual message in a conversation
    - MessageCreate: For saving new messages
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any, Literal


class MessageBase(BaseModel):
    """Base message fields."""
    role: Literal['user', 'assistant', 'system']
    content: str = Field(..., min_length=1)


class MessageCreate(MessageBase):
    """
    Create new message in conversation.
    
    Fields:
        conversation_id: Which conversation this belongs to
        role: user, assistant, or system
        content: Message text
        tool_calls: Optional metadata for assistant function calls
    """
    conversation_id: str
    tool_calls: Optional[dict[str, Any]] = None


class Message(MessageBase):
    """
    Full message model.
    
    Fields:
        id: UUID primary key
        conversation_id: Parent conversation
        role: user | assistant | system
        content: Message text
        created_at: When message was sent
        tool_calls: Optional function call metadata (JSONB)
    """
    id: str
    conversation_id: str
    created_at: datetime
    tool_calls: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True
