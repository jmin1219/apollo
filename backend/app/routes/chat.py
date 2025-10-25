"""
Chat API routes for APOLLO Life Coordinator agent.

Provides streaming conversation endpoints using Server-Sent Events (SSE).
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator
import json
import os

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.agents.life_coordinator import LifeCoordinator
from app.agents.context import create_agent_context, agent_context_to_dict
from app.agents.tools.task_tools import TaskTools
from app.db.supabase_client import supabase


router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """
    User message to Life Coordinator.
    
    Fields:
        message: User's text message
        conversation_history: Optional previous messages for context
    """
    message: str
    conversation_history: list[dict[str, str]] = []


@router.post("/stream")
async def stream_message(
    request: ChatMessage,
    current_user: User = Depends(get_current_user)
):
    """
    Send message to Life Coordinator and receive streaming response.
    
    Uses Server-Sent Events (SSE) for real-time word-by-word responses.
    
    Args:
        request: ChatMessage with user's message and optional history
        current_user: Authenticated user from JWT
    
    Returns:
        StreamingResponse with text/event-stream content type
    
    SSE Format:
        data: {"type": "chunk", "content": "I"}\n\n
        data: {"type": "chunk", "content": " recommend"}\n\n
        ...
        data: {"type": "done"}\n\n
    
    Example:
        POST /chat/stream
        {
            "message": "What should I focus on today?",
            "conversation_history": []
        }
        
        Response (streaming):
        data: {"type": "chunk", "content": "I"}
        data: {"type": "chunk", "content": " recommend"}
        ...
        data: {"type": "done"}
    """
    
    async def generate_stream() -> AsyncGenerator[str, None]:
        """
        Generate SSE stream for agent response.
        
        This is an async generator that:
        1. Gets OpenAI API key
        2. Initializes agent
        3. Fetches user context from database
        4. Streams agent response chunk-by-chunk
        5. Sends completion event
        
        Yields:
            SSE-formatted events as strings
        """
        try:
            # Get API key
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                yield f"data: {json.dumps({'type': 'error', 'content': 'OpenAI API key not configured'})}\n\n"
                return
            
            # Validate user ID exists
            if not current_user.id:
                yield f"data: {json.dumps({'type': 'error', 'content': 'User ID missing'})}\n\n"
                return
            
            # Type-safe user_id (we've validated it's not None)
            user_id: str = current_user.id
            
            # Initialize agent
            agent = LifeCoordinator(api_key=api_key)
            
            # Fetch user context from database
            agent_context = await create_agent_context(
                user_id=user_id,
                message=request.message
            )
            user_context = agent_context_to_dict(agent_context)
            
            # Build message history (conversation_history + new message)
            messages = request.conversation_history.copy()
            messages.append({
                "role": "user",
                "content": request.message
            })
            
            # Stream response chunks from agent
            async for chunk in agent.generate_response_stream(
                user_id=user_id,
                messages=messages,
                user_context=user_context
            ):
                # Format chunk as SSE event
                event_data = {
                    "type": "chunk",
                    "content": chunk
                }
                # SSE format: "data: {json}\n\n"
                yield f"data: {json.dumps(event_data)}\n\n"
            
            # Send completion event
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
        except Exception as e:
            # Stream error to client (don't crash, let client handle)
            error_data = {
                "type": "error",
                "content": f"Error: {str(e)}"
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",  # Don't cache streaming responses
            "Connection": "keep-alive",    # Keep connection open
        }
    )
