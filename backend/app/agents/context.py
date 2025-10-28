"""
Agent context management for APOLLO.

This module handles context creation for AI agents - gathering user data,
formatting it for LLM consumption, and managing token budgets.
"""

from dataclasses import dataclass
from typing import Any, Optional, TypeAlias, cast

from app.db.supabase_client import supabase

# Type aliases for clarity (using modern lowercase dict)
TaskDict: TypeAlias = dict[str, Any]
MessageDict: TypeAlias = dict[str, Any]
PreferencesDict: TypeAlias = dict[str, Any]


@dataclass
class AgentContext:
    """
    Context provided to AI agents for generating responses.

    Fields:
        user_id: Unique identifier for user
        current_tasks: Active tasks (pending/in_progress), limited to 20
        goals: User's active goals (yearly objectives)
        milestones: Active milestones (quarterly checkpoints)
        user_preferences: User settings (future implementation)
        recent_messages: Last 10 conversation messages (future implementation)
        history_summary: Compressed older messages (future implementation)
    """
    user_id: str
    current_tasks: list[TaskDict] | None = None
    goals: list[TaskDict] | None = None
    milestones: list[TaskDict] | None = None
    user_preferences: PreferencesDict | None = None
    recent_messages: list[MessageDict] | None = None
    history_summary: str | None = None


async def create_agent_context(
    user_id: str,
    message: str,
    conversation_id: Optional[str] = None
) -> AgentContext:
    """
    Build context for agent to process user message.

    Phase 1 implementation:
    - Fetches user's active tasks (pending + in_progress)
    - Limits to 20 tasks (~800 tokens)
    - Skips messages/preferences (tables don't exist yet)

    Phase 3 will add:
    - Conversation messages table
    - User preferences table
    - History summarization

    Args:
        user_id: ID of user making the request
        message: Current user message
        conversation_id: Optional conversation to load history from

    Returns:
        AgentContext with all data agent needs

    Token budget allocation (GPT-4: 8,192 tokens total):
        - System prompt: ~300 tokens
        - Tasks (20): ~800 tokens
        - Messages (future): ~1,500 tokens
        - History summary (future): ~500 tokens
        - Current message: ~100 tokens
        - Total context: ~3,300 tokens
        - Available for response: ~4,892 tokens
    """

    # Fetch active goals
    try:
        goals_response: Any = (
            supabase.table("goals")
            .select("*")
            .eq("user_id", user_id)
            .eq("status", "active")
            .order("target_date", desc=False)
            .limit(10)  # Token budget
            .execute()
        )
        goals_data: list[TaskDict] = cast(list[TaskDict], goals_response.data)
    except Exception as e:
        print(f"Error fetching goals for user {user_id}: {e}")
        goals_data = []

    # Fetch active milestones
    try:
        milestones_response: Any = (
            supabase.table("milestones")
            .select("*")
            .eq("user_id", user_id)
            .in_("status", ["not_started", "in_progress"])  # Active milestones
            .order("target_date", desc=False)
            .limit(20)  # Token budget
            .execute()
        )
        milestones_data: list[TaskDict] = cast(list[TaskDict], milestones_response.data)
    except Exception as e:
        print(f"Error fetching milestones for user {user_id}: {e}")
        milestones_data = []

    # Fetch active tasks (pending + in_progress)
    try:
        response: Any = (
            supabase.table("tasks")
            .select("*")
            .eq("user_id", user_id)
            .in_("status", ["pending", "in_progress"])  # Match either status
            .order("created_at", desc=True)  # Most recent first
            .limit(20)  # Token budget constraint
            .execute()
        )

        tasks_data: list[TaskDict] = cast(list[TaskDict], response.data)

    except Exception as e:
        # Graceful degradation: agent works without task context
        # Logs error for debugging but doesn't crash
        print(f"Error fetching tasks for user {user_id}: {e}")
        tasks_data = []

    # Phase 3 TODO: Fetch recent messages
    # Will require creating conversations and messages tables

    # Phase 3 TODO: Fetch user preferences
    # Will require creating user_preferences table

    # Phase 3 TODO: Generate history summary
    # Will require implementing summarization logic

    return AgentContext(
        user_id=user_id,
        current_tasks=tasks_data,
        goals=goals_data,
        milestones=milestones_data,
        user_preferences=None,
        recent_messages=None,
        history_summary=None
    )

def agent_context_to_dict(context: AgentContext) -> dict[str, Any]:
    """
    Convert AgentContext dataclass to dictionary for easier serialization.

    Args:
        context: AgentContext instance from create_agent_context

    Returns:
        Dictionary with tasks, goals, milestones, and stats:
        {
            "tasks": [...],
            "goals": [...],
            "milestones": [...],
            "stats": {...}
        }
    """
    tasks = context.current_tasks if context.current_tasks else []
    goals = context.goals if context.goals else []
    milestones = context.milestones if context.milestones else []

    return {
        "tasks": tasks,
        "goals": goals,
        "milestones": milestones,
        "stats": {
            "total_tasks": len(tasks),
            "pending_tasks": sum(1 for task in tasks if task.get("status") == "pending"),
            "total_goals": len(goals),
            "active_milestones": len(milestones),
        }
    }
