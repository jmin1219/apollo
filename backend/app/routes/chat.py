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
    Send message to Life Coordinator and receive response.

    Hybrid approach:
    - If message likely needs tool calling (task manipulation) → non-streaming response
    - If conversational only → streaming response (SSE)

    This provides best UX: streaming for conversation, instant execution for actions.

    Args:
        request: ChatMessage with user's message and optional history
        current_user: Authenticated user from JWT

    Returns:
        StreamingResponse with text/event-stream content type

    Example:
        POST /chat/stream
        {
            "message": "What should I focus on today?",
            "conversation_history": []
        }
    """

    # Detect if message likely needs tool calling
    tool_keywords = ['add', 'create', 'delete', 'remove', 'update', 'mark', 'complete', 'finish', 'done']
    needs_tools = any(keyword in request.message.lower() for keyword in tool_keywords)

    # Route to appropriate response mode
    if needs_tools:
        # Use non-streaming with tool calling support
        return await _handle_with_tools(request, current_user)
    else:
        # Use streaming for conversational responses
        return await _handle_streaming(request, current_user)


async def _handle_streaming(
    request: ChatMessage,
    current_user: User
) -> StreamingResponse:
    """Handle conversational messages with streaming (no tools)."""

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
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


async def _handle_with_tools(
    request: ChatMessage,
    current_user: User
) -> StreamingResponse:
    """Handle messages that need tool calling (non-streaming)."""

    async def generate_with_tools() -> AsyncGenerator[str, None]:
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                yield f"data: {json.dumps({'type': 'error', 'content': 'OpenAI API key not configured'})}\n\n"
                return

            if not current_user.id:
                yield f"data: {json.dumps({'type': 'error', 'content': 'User ID missing'})}\n\n"
                return

            user_id: str = current_user.id

            # Initialize agent and tools
            agent = LifeCoordinator(api_key=api_key)
            task_tools = TaskTools(supabase=supabase)

            # Fetch context
            agent_context = await create_agent_context(
                user_id=user_id,
                message=request.message
            )
            user_context = agent_context_to_dict(agent_context)

            # Build message history
            messages = request.conversation_history.copy()
            messages.append({
                "role": "user",
                "content": request.message
            })

            # Get response with tool calling (non-streaming)
            result = await agent.generate_response(
                user_id=user_id,
                messages=messages,
                user_context=user_context,
                task_tools=task_tools
            )

            # Stream the final response as one chunk
            yield f"data: {json.dumps({'type': 'chunk', 'content': result['response']})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            error_data = {
                "type": "error",
                "content": f"Error: {str(e)}"
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        generate_with_tools(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
