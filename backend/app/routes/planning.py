"""
Planning timeline routes for APOLLO.

Provides temporal timeline views with detail gradient:
- Today: All pending tasks
- Week: Active projects + upcoming tasks
- Month: Active milestones + key deadlines
- Year: Active goals + major milestones
"""

from fastapi import APIRouter, Depends, Query
from typing import Literal
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.db.supabase_client import supabase
from datetime import datetime, timedelta

router = APIRouter(prefix="/planning", tags=["planning"])


@router.get("/timeline")
async def get_timeline(
    horizon: Literal["today", "week", "month", "year"] = Query(default="week"),
    current_user: User = Depends(get_current_user)
):
    """
    Get temporal timeline with detail gradient.

    Args:
        horizon: Time window to view (today/week/month/year)
        current_user: Authenticated user (from JWT)

    Returns:
        {
            "horizon": "week",
            "items": [
                {type: "goal|milestone|task", ...data},
                ...
            ]
        }
    """
    user_id = current_user.id
    items = []

    # Calculate date boundaries based on horizon
    today = datetime.now()

    if horizon == "today":
        # Today: All pending/in_progress tasks (5-10 items)
        try:
            tasks_response = supabase.table("tasks")\
                .select("*")\
                .eq("user_id", user_id)\
                .in_("status", ["pending", "in_progress"])\
                .order("priority", desc=True)\
                .order("created_at", desc=True)\
                .limit(10)\
                .execute()  # type: ignore

            tasks = tasks_response.data or []  # type: ignore

            for task in tasks:
                items.append({
                    "type": "task",
                    **task
                })

        except Exception as e:
            # Gracefully handle DB errors
            items = []

    elif horizon == "week":
        # This week: Active milestones + upcoming tasks + goals
        try:
            # Fetch active milestones
            milestones_response = supabase.table("milestones")\
                .select("*")\
                .eq("user_id", user_id)\
                .in_("status", ["not_started", "in_progress"])\
                .order("target_date", desc=False)\
                .limit(5)\
                .execute()  # type: ignore
            milestones = milestones_response.data or []  # type: ignore

            for milestone in milestones:
                items.append({
                    "type": "milestone",
                    **milestone
                })
        except Exception as e:
            pass

        # Fetch upcoming tasks
        try:
            tasks_response = supabase.table("tasks")\
                .select("*")\
                .eq("user_id", user_id)\
                .in_("status", ["pending", "in_progress"])\
                .order("priority", desc=True)\
                .order("created_at", desc=True)\
                .limit(10)\
                .execute()  # type: ignore

            tasks = tasks_response.data or []  # type: ignore

            for task in tasks:
                items.append({
                    "type": "task",
                    **task
                })
        except Exception as e:
            pass

        # Fetch active goals
        try:
            goals_response = supabase.table("goals")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("status", "active")\
                .order("target_date", desc=False)\
                .limit(5)\
                .execute()  # type: ignore

            goals = goals_response.data or []  # type: ignore

            for goal in goals:
                items.append({
                    "type": "goal",
                    **goal
                })
        except Exception as e:
            pass

    elif horizon == "month":
        # This month: Active milestones + key deadlines
        try:
            milestones_response = supabase.table("milestones")\
                .select("*")\
                .eq("user_id", user_id)\
                .in_("status", ["not_started", "in_progress"])\
                .order("target_date", desc=False)\
                .limit(5)\
                .execute()  # type: ignore

            milestones = milestones_response.data or []  # type: ignore

            for milestone in milestones:
                items.append({
                    "type": "milestone",
                    **milestone
                })
        except Exception as e:
            pass

        # Fetch key deadlines (tasks due this month)
        try:
            tasks_response = supabase.table("tasks")\
                .select("*")\
                .eq("user_id", user_id)\
                .in_("status", ["pending", "in_progress"])\
                .order("priority", desc=True)\
                .order("created_at", desc=True)\
                .limit(10)\
                .execute()  # type: ignore

            tasks = tasks_response.data or []  # type: ignore

            for task in tasks:
                items.append({
                    "type": "task",
                    **task
                })
        except Exception as e:
            pass

    elif horizon == "year":
        # Next 18 months: Active goals + major milestones
        # Extended to capture goals 15+ months out (like Jan 2027 co-op)
        today_str = today.strftime("%Y-%m-%d")
        eighteen_months = (today + timedelta(days=545)).strftime("%Y-%m-%d")  # ~18 months
        
        try:
            goals_response = supabase.table("goals")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("status", "active")\
                .gte("target_date", today_str)\
                .lte("target_date", eighteen_months)\
                .order("target_date", desc=False)\
                .limit(10)\
                .execute()  # type: ignore

            goals = goals_response.data or []  # type: ignore

            for goal in goals:
                items.append({
                    "type": "goal",
                    **goal
                })
        except Exception as e:
            pass

        try:
            milestones_response = supabase.table("milestones")\
                .select("*")\
                .eq("user_id", user_id)\
                .in_("status", ["not_started", "in_progress"])\
                .gte("target_date", today_str)\
                .lte("target_date", eighteen_months)\
                .order("target_date", desc=False)\
                .limit(20)\
                .execute()  # type: ignore

            milestones = milestones_response.data or []  # type: ignore

            for milestone in milestones:
                items.append({
                    "type": "milestone",
                    **milestone
                })
        except Exception as e:
            pass

    return {
        "horizon": horizon,
        "items": items
    }
