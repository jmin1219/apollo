"""
Agent context management for APOLLO.

This module handles context creation for AI agents - gathering user data,
formatting it for LLM consumption, and managing token budgets.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class AgentContext:
    """
    Context provided to AI agents for generating responses.
    
    TODO: Think about what data an agent needs to respond intelligently
    - User identification?
    - Conversation history?
    - User's current tasks?
    - User preferences or settings?
    - Available tools?
    
    Design consideration: Keep this focused. Only include data the agent
    actually needs, not everything you have available.
    """
    user_id: str
    # TODO: Add more fields as you understand what agents need


async def create_agent_context(
    user_id: str,
    message: str,
    conversation_id: Optional[str] = None
) -> AgentContext:
    """
    Build context for agent to process user message.
    
    TODO: Implement context building
    
    Steps to think through:
    1. What user data should we fetch from database?
       - Current tasks? All of them or just pending?
       - User preferences or settings?
       - Conversation history?
    
    2. How do we manage token budget?
       - GPT-4 has 8k token limit
       - System prompt uses ~200 tokens
       - How much budget left for user context?
       - What if user has 100 tasks? (can't fit all)
    
    3. How do we format data for the agent?
       - JSON? Natural language? Structured list?
       - Trade-off: Token efficiency vs clarity
    
    Concepts to research:
    - Token counting (how to estimate context size)
    - Context window management (what to include/exclude)
    - Data prioritization (recent vs relevant)
    
    Interview question you should be able to answer:
    "How do you handle context that exceeds the model's token limit?"
    
    Args:
        user_id: ID of user making the request
        message: Current user message
        conversation_id: Optional conversation to load history from
    
    Returns:
        AgentContext with all data agent needs
    """
    # TODO: Implement this function
    # Hint: Start by just returning a basic context with user_id
    # Then gradually add more data (tasks, history, etc.)
    pass
