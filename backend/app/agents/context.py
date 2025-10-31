"""
Agent context management for APOLLO.

This module handles context creation for AI agents - gathering user data,
formatting it for LLM consumption, and managing token budgets.
"""

from dataclasses import dataclass
from typing import Any, Optional, TypeAlias, cast
from app.services.obsidian_vault import ObsidianClient
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
        today_context: Today's date, day of week, capacity (Module 3)
        weekly_progress: Tasks completed this week, total minutes (Module 3)
        urgent_deadlines: Tasks due within 3 days (Module 3)
        upcoming_deadlines: Tasks due within 4-10 days (Module 3)
    """
    user_id: str
    current_tasks: list[TaskDict] | None = None
    goals: list[TaskDict] | None = None
    milestones: list[TaskDict] | None = None
    user_preferences: PreferencesDict | None = None
    recent_messages: list[MessageDict] | None = None
    history_summary: str | None = None

    today_context: dict[str, Any] | None = None
    weekly_progress: dict[str, Any] | None = None
    urgent_deadlines: list[TaskDict] | None = None  # Within 3 days
    upcoming_deadlines: list[TaskDict] | None = None  # Within 10 days


async def create_agent_context(
    user_id: str,
    message: str,
    conversation_id: Optional[str] = None
) -> AgentContext:
    """
    Build context for agent to process user message.

    Module 3 implementation:
    - Fetches user's active tasks, goals, milestones
    - Calculates weekly progress (tasks completed this week)
    - Identifies urgent deadlines (0-3 days) and upcoming (4-10 days)
    - Provides today's context (date, day of week)

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
        - Goals (10): ~400 tokens
        - Milestones (20): ~600 tokens
        - Progress/deadlines: ~200 tokens
        - Messages (future): ~1,500 tokens
        - History summary (future): ~500 tokens
        - Current message: ~100 tokens
        - Total context: ~4,400 tokens
        - Available for response: ~3,800 tokens
    """
    # Fetch Obsidian profile
    obsidian = ObsidianClient()
    profile = await obsidian.get_profile()

    # ========= Fetch Goals =========
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

    # ======== Fetch Milestones =========
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

    # ======== Fetch Current Tasks =========
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


    # ========= Weekly Progress Calculation =========
    from datetime import datetime, timedelta

    # Calculate week boundaries (Monday to Sunday)
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_start_str = week_start.strftime("%Y-%m-%d")

    try:
        # Count tasks completed this week
        completed_tasks_response: Any = (
            supabase.table("tasks")
            .select("*", count="exact")
            .eq("user_id", user_id)
            .eq("status", "completed")
            .gte("updated_at", week_start_str)
            .execute()
        )

        tasks_completed_count = completed_tasks_response.count or 0
        completed_tasks_data= completed_tasks_response.data or []

    except Exception as e:
        print(f"Error fetching weekly completed tasks for user {user_id}: {e}")
        tasks_completed_count = 0
        completed_tasks_data = []

    # ======== Deadline Boundaries Calculation ========
    three_days_from_now = today + timedelta(days=3)
    three_days_from_now_str = three_days_from_now.strftime("%Y-%m-%d")
    ten_days_from_now = today + timedelta(days=10)
    ten_days_from_now_str = ten_days_from_now.strftime("%Y-%m-%d")

    try:
        # Urgent deadlines within 3 days
        urgent_deadlines_response: Any = (
            supabase.table("tasks")
            .select("*")
            .eq("user_id", user_id)
            .in_("status", ["pending", "in_progress"])
            .not_.is_("due_date", 'null')
            .lte("due_date", three_days_from_now_str)
            .order("due_date", desc=False)
            .limit(10)
            .execute()
        )

        urgent_deadlines_data: list[TaskDict] = cast(list[TaskDict], urgent_deadlines_response.data) or []

    except Exception as e:
        print(f"Error fetching urgent deadlines for user {user_id}: {e}")
        urgent_deadlines_data = []

    try:
        # Upcoming deadlines within 10 days (excluding urgent 0-3 day range)
        upcoming_deadlines_response: Any = (
            supabase.table("tasks")
            .select("*")
            .eq("user_id", user_id)
            .in_("status", ["pending", "in_progress"])
            .not_.is_("due_date", 'null')
            .gt("due_date", three_days_from_now_str)  # After urgent window
            .lte("due_date", ten_days_from_now_str)   # Within 10 days
            .order("due_date", desc=False)
            .limit(15)
            .execute()
        )

        upcoming_deadlines_data: list[TaskDict] = cast(list[TaskDict], upcoming_deadlines_response.data) or []

    except Exception as e:
        print(f"Error fetching upcoming deadlines for user {user_id}: {e}")
        upcoming_deadlines_data = []

    # ========= Assemble Context =========
    today_context = {
        "date": today.strftime("%Y-%m-%d"),
        "day_of_week": today.strftime("%A"),
    }

    weekly_progress = {
        "week_start": week_start_str,
        "tasks_completed": tasks_completed_count,
        "total_minutes": sum(task.get("time_spent_minutes", 0) for task in completed_tasks_data) if completed_tasks_data else 0,
    }

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
        recent_messages=None,
        history_summary=None,
        today_context=today_context,
        weekly_progress=weekly_progress,
        urgent_deadlines=urgent_deadlines_data,
        upcoming_deadlines=upcoming_deadlines_data,
        user_preferences=profile
    )

def agent_context_to_dict(context: AgentContext) -> dict[str, Any]:
    """
    Convert AgentContext dataclass to dictionary for easier serialization.

    Args:
        context: AgentContext instance from create_agent_context

    Returns:
        Dictionary with tasks, goals, milestones, progress, and stats:
        {
            "tasks": [...],
            "goals": [...],
            "milestones": [...],
            "today_context": {...},
            "weekly_progress": {...},
            "urgent_deadlines": [...],
            "upcoming_deadlines": [...],
            "stats": {...}
        }
    """
    tasks = context.current_tasks if context.current_tasks else []
    goals = context.goals if context.goals else []
    milestones = context.milestones if context.milestones else []
    urgent = context.urgent_deadlines if context.urgent_deadlines else []
    upcoming = context.upcoming_deadlines if context.upcoming_deadlines else []

    return {
        "tasks": tasks,
        "goals": goals,
        "milestones": milestones,
        "today_context": context.today_context,
        "weekly_progress": context.weekly_progress,
        "urgent_deadlines": urgent,
        "upcoming_deadlines": upcoming,
        "user_profile": context.user_preferences,
        "stats": {
            "total_tasks": len(tasks),
            "pending_tasks": sum(1 for task in tasks if task.get("status") == "pending"),
            "total_goals": len(goals),
            "active_milestones": len(milestones),
            "urgent_count": len(urgent),
            "upcoming_count": len(upcoming),
        }
    }
