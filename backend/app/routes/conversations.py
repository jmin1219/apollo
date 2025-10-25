"""
Conversation management API routes.

Endpoints:
    - GET /conversations - List user's conversations
    - POST /conversations - Create new conversation
    - GET /conversations/{id} - Get conversation with messages
    - PATCH /conversations/{id} - Update conversation title
    - DELETE /conversations/{id} - Delete conversation
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from datetime import datetime

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.conversation import (
    Conversation,
    ConversationCreate,
    ConversationUpdate,
    ConversationListItem
)
from app.models.message import Message, MessageCreate
from app.db.supabase_client import supabase


router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=List[ConversationListItem])
async def list_conversations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
):
    """List user's conversations ordered by most recent."""
    
    # Query conversations
    response = supabase.table('conversations')\
        .select('*')\
        .eq('user_id', current_user.id)\
        .order('updated_at', desc=True)\
        .range(offset, offset + limit - 1)\
        .execute()
    
    if not response.data:
        return []
    
    # Count messages for each conversation
    conversations_with_counts = []
    for conv in response.data:
        msg_response = supabase.table('messages')\
            .select('*', count='exact')\
            .eq('conversation_id', conv['id'])\
            .execute()
        
        conversations_with_counts.append(
            ConversationListItem(
                **conv,  # Unpack dict as kwargs
                message_count=msg_response.count or 0
            )
        )
    
    return conversations_with_counts


@router.post("", response_model=Conversation)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: User = Depends(get_current_user)
):
    """Create new conversation."""
    
    response = supabase.table("conversations")\
        .insert({
            "user_id": current_user.id,
            "title": conversation.title
        })\
        .execute()
    
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create conversation")
    
    return Conversation(**response.data[0])


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
):
    """Get conversation with messages."""
    
    # Fetch conversation
    conv_response = supabase.table("conversations")\
        .select("*")\
        .eq("id", conversation_id)\
        .execute()
    
    if not conv_response.data:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = conv_response.data[0]
    
    # Verify ownership
    if conversation["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Fetch messages
    msg_response = supabase.table("messages")\
        .select("*")\
        .eq("conversation_id", conversation_id)\
        .order("created_at")\
        .range(offset, offset + limit - 1)\
        .execute()
    
    # Count total messages
    count_response = supabase.table("messages")\
        .select("*", count="exact")\
        .eq("conversation_id", conversation_id)\
        .execute()
    
    return {
        "conversation": conversation,
        "messages": msg_response.data or [],
        "total_messages": count_response.count or 0
    }


@router.patch("/{conversation_id}", response_model=Conversation)
async def update_conversation(
    conversation_id: str,
    update: ConversationUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update conversation title."""
    
    # Verify conversation exists and ownership
    conv_response = supabase.table("conversations")\
        .select("*")\
        .eq("id", conversation_id)\
        .execute()
    
    if not conv_response.data:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conv_response.data[0]["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update title and timestamp
    update_response = supabase.table("conversations")\
        .update({
            "title": update.title,
            "updated_at": datetime.utcnow().isoformat()
        })\
        .eq("id", conversation_id)\
        .execute()
    
    if not update_response.data:
        raise HTTPException(status_code=500, detail="Failed to update conversation")
    
    return Conversation(**update_response.data[0])


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete conversation and all messages (CASCADE)."""
    
    # Verify conversation exists and ownership
    conv_response = supabase.table("conversations")\
        .select("*")\
        .eq("id", conversation_id)\
        .execute()
    
    if not conv_response.data:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conv_response.data[0]["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Delete conversation (CASCADE deletes messages)
    supabase.table("conversations")\
        .delete()\
        .eq("id", conversation_id)\
        .execute()
    
    return {
        "deleted": True,
        "conversation_id": conversation_id
    }


@router.post("/{conversation_id}/messages", response_model=Message)
async def create_message(
    conversation_id: str,
    message: MessageCreate,
    current_user: User = Depends(get_current_user)
):
    """Add message to conversation and update timestamp."""
    
    # Verify conversation exists and ownership
    conv_response = supabase.table("conversations")\
        .select("*")\
        .eq("id", conversation_id)\
        .execute()
    
    if not conv_response.data:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = conv_response.data[0]
    
    if conversation["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Insert message
    msg_response = supabase.table("messages")\
        .insert({
            "conversation_id": conversation_id,
            "role": message.role,
            "content": message.content,
            "tool_calls": message.tool_calls
        })\
        .execute()
    
    if not msg_response.data:
        raise HTTPException(status_code=500, detail="Failed to create message")
    
    # Update conversation timestamp
    supabase.table("conversations")\
        .update({"updated_at": datetime.utcnow().isoformat()})\
        .eq("id", conversation_id)\
        .execute()
    
    # Auto-generate title from first user message if needed
    if message.role == "user" and not conversation.get("title"):
        title = message.content[:50] + ("..." if len(message.content) > 50 else "")
        supabase.table("conversations")\
            .update({"title": title})\
            .eq("id", conversation_id)\
            .execute()
    
    return Message(**msg_response.data[0])
