"""
Goals API routes for APOLLO.

Handles CRUD operations for user goals (yearly objectives).
"""

from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.db.supabase_client import supabase
from app.models.goal import Goal, GoalCreate, GoalUpdate
from app.models.user import User


router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("", response_model=Goal, status_code=201)
async def create_goal(
    goal: GoalCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Create a new goal for the authenticated user.

    Args:
        goal: Goal data (title, description, target_date, status)
        current_user: Authenticated user from JWT

    Returns:
        Created goal with id and timestamps

    Raises:
        400: Invalid input (validation error)
        500: Database error
    """
    try:
        response: Any = (
            supabase.table("goals")
            .insert({
                "user_id": current_user.id,
                "title": goal.title,
                "description": goal.description,
                "target_date": str(goal.target_date) if goal.target_date else None,
                "status": goal.status,
            })
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create goal")

        created_goal: dict = cast(dict, response.data[0])
        return Goal(**created_goal)

    except HTTPException:
        raise
    except Exception as e:
        detail = f"Error creating goal: {str(e)}"
        raise HTTPException(status_code=500, detail=detail) from e


@router.get("", response_model=list[Goal])
async def list_goals(
    current_user: User = Depends(get_current_user),
    status: str | None = None,
):
    """
    List all goals for the authenticated user.

    Args:
        current_user: Authenticated user from JWT
        status: Optional filter by status (active, achieved, abandoned)

    Returns:
        List of goals ordered by target_date (soonest first)
    """
    try:
        query = supabase.table("goals").select("*").eq("user_id", current_user.id)

        if status:
            query = query.eq("status", status)

        query = query.order("target_date", desc=False)

        response: Any = query.execute()
        goals_data = cast(list[dict], response.data)

        return [Goal(**goal) for goal in goals_data]

    except Exception as e:
        detail = f"Error retrieving goals: {str(e)}"
        raise HTTPException(status_code=500, detail=detail) from e


@router.get("/{goal_id}", response_model=Goal)
async def get_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get a single goal by ID (must belong to current user).

    Args:
        goal_id: UUID of the goal
        current_user: Authenticated user from JWT

    Returns:
        Goal data

    Raises:
        404: Goal not found or doesn't belong to user
        400: Invalid UUID format
    """
    try:
        response: Any = (
            supabase.table("goals")
            .select("*")
            .eq("id", goal_id)
            .eq("user_id", current_user.id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Goal not found")

        return Goal(**cast(dict, response.data[0]))

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "invalid input syntax for type uuid" in error_msg.lower():
            raise HTTPException(
                status_code=400, detail="Invalid goal_id: must be a valid UUID"
            ) from e
        detail = f"Error retrieving goal: {error_msg}"
        raise HTTPException(status_code=500, detail=detail) from e


@router.patch("/{goal_id}", response_model=Goal)
async def update_goal(
    goal_id: str,
    goal: GoalUpdate,
    current_user: User = Depends(get_current_user),
):
    """
    Update a goal (partial update).

    Args:
        goal_id: UUID of the goal
        goal: Fields to update (all optional)
        current_user: Authenticated user from JWT

    Returns:
        Updated goal

    Raises:
        404: Goal not found
        400: Invalid input
    """
    try:
        # Build update dict from non-None fields
        update_data = {}
        if goal.title is not None:
            update_data["title"] = goal.title
        if goal.description is not None:
            update_data["description"] = goal.description
        if goal.target_date is not None:
            update_data["target_date"] = str(goal.target_date)
        if goal.status is not None:
            update_data["status"] = goal.status

        update_data["updated_at"] = "now()"

        response: Any = (
            supabase.table("goals")
            .update(update_data)
            .eq("id", goal_id)
            .eq("user_id", current_user.id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Goal not found")

        updated_goal: dict = cast(dict, response.data[0])
        return Goal(**updated_goal)

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "invalid input syntax for type uuid" in error_msg.lower():
            raise HTTPException(
                status_code=400, detail="Invalid goal_id: must be a valid UUID"
            ) from e
        detail = f"Error updating goal: {error_msg}"
        raise HTTPException(status_code=500, detail=detail) from e


@router.delete("/{goal_id}", status_code=204)
async def delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Delete a goal (CASCADE deletes associated milestones).

    Args:
        goal_id: UUID of the goal
        current_user: Authenticated user from JWT

    Returns:
        204 No Content on success

    Raises:
        404: Goal not found
    """
    try:
        response: Any = (
            supabase.table("goals")
            .delete()
            .eq("id", goal_id)
            .eq("user_id", current_user.id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Goal not found")

        return

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "invalid input syntax for type uuid" in error_msg.lower():
            raise HTTPException(
                status_code=400, detail="Invalid goal_id: must be a valid UUID"
            ) from e
        detail = f"Error deleting goal: {error_msg}"
        raise HTTPException(status_code=500, detail=detail) from e
