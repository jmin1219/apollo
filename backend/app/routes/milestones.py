"""
Milestones API routes for APOLLO.

Handles CRUD operations for milestones (quarterly checkpoints).
"""

from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.db.supabase_client import supabase
from app.models.milestone import Milestone, MilestoneCreate, MilestoneUpdate
from app.models.user import User


router = APIRouter(prefix="/milestones", tags=["milestones"])


@router.post("", response_model=Milestone, status_code=201)
async def create_milestone(
    milestone: MilestoneCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Create a new milestone for the authenticated user.

    Args:
        milestone: Milestone data
        current_user: Authenticated user from JWT

    Returns:
        Created milestone

    Raises:
        400: Invalid goal_id (foreign key violation)
        500: Database error
    """
    try:
        response: Any = (
            supabase.table("milestones")
            .insert({
                "user_id": current_user.id,
                "title": milestone.title,
                "description": milestone.description,
                "goal_id": milestone.goal_id,
                "target_date": str(milestone.target_date) if milestone.target_date else None,
                "status": milestone.status,
                "progress": milestone.progress,
            })
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create milestone")

        created_milestone: dict = cast(dict, response.data[0])
        return Milestone(**created_milestone)

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "foreign key constraint" in error_msg.lower():
            raise HTTPException(
                status_code=400, detail="Invalid goal_id: goal does not exist"
            ) from e
        detail = f"Error creating milestone: {error_msg}"
        raise HTTPException(status_code=500, detail=detail) from e


@router.get("", response_model=list[Milestone])
async def list_milestones(
    current_user: User = Depends(get_current_user),
    goal_id: str | None = None,
    status: str | None = None,
):
    """
    List milestones for the authenticated user.

    Args:
        current_user: Authenticated user from JWT
        goal_id: Optional filter by parent goal
        status: Optional filter by status

    Returns:
        List of milestones ordered by target_date
    """
    try:
        query = supabase.table("milestones").select("*").eq("user_id", current_user.id)

        if goal_id:
            query = query.eq("goal_id", goal_id)
        if status:
            query = query.eq("status", status)

        query = query.order("target_date", desc=False)

        response: Any = query.execute()
        milestones_data = cast(list[dict], response.data)

        return [Milestone(**m) for m in milestones_data]

    except Exception as e:
        detail = f"Error retrieving milestones: {str(e)}"
        raise HTTPException(status_code=500, detail=detail) from e


@router.get("/{milestone_id}", response_model=Milestone)
async def get_milestone(
    milestone_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get a single milestone by ID (must belong to current user).

    Args:
        milestone_id: UUID of the milestone
        current_user: Authenticated user from JWT

    Returns:
        Milestone data

    Raises:
        404: Milestone not found
        400: Invalid UUID
    """
    try:
        response: Any = (
            supabase.table("milestones")
            .select("*")
            .eq("id", milestone_id)
            .eq("user_id", current_user.id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Milestone not found")

        return Milestone(**cast(dict, response.data[0]))

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "invalid input syntax for type uuid" in error_msg.lower():
            raise HTTPException(
                status_code=400, detail="Invalid milestone_id: must be a valid UUID"
            ) from e
        detail = f"Error retrieving milestone: {error_msg}"
        raise HTTPException(status_code=500, detail=detail) from e


@router.patch("/{milestone_id}", response_model=Milestone)
async def update_milestone(
    milestone_id: str,
    milestone: MilestoneUpdate,
    current_user: User = Depends(get_current_user),
):
    """
    Update a milestone (partial update).

    Args:
        milestone_id: UUID of the milestone
        milestone: Fields to update
        current_user: Authenticated user from JWT

    Returns:
        Updated milestone
    """
    try:
        update_data = {}
        if milestone.title is not None:
            update_data["title"] = milestone.title
        if milestone.description is not None:
            update_data["description"] = milestone.description
        if milestone.goal_id is not None:
            update_data["goal_id"] = milestone.goal_id
        if milestone.target_date is not None:
            update_data["target_date"] = str(milestone.target_date)
        if milestone.status is not None:
            update_data["status"] = milestone.status
        if milestone.progress is not None:
            update_data["progress"] = milestone.progress

        update_data["updated_at"] = "now()"

        response: Any = (
            supabase.table("milestones")
            .update(update_data)
            .eq("id", milestone_id)
            .eq("user_id", current_user.id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Milestone not found")

        updated_milestone: dict = cast(dict, response.data[0])
        return Milestone(**updated_milestone)

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "invalid input syntax for type uuid" in error_msg.lower():
            raise HTTPException(
                status_code=400, detail="Invalid milestone_id: must be a valid UUID"
            ) from e
        detail = f"Error updating milestone: {error_msg}"
        raise HTTPException(status_code=500, detail=detail) from e


@router.delete("/{milestone_id}", status_code=204)
async def delete_milestone(
    milestone_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Delete a milestone (tasks with this milestone_id will have it set to NULL).

    Args:
        milestone_id: UUID of the milestone
        current_user: Authenticated user from JWT

    Returns:
        204 No Content on success

    Raises:
        404: Milestone not found
    """
    try:
        response: Any = (
            supabase.table("milestones")
            .delete()
            .eq("id", milestone_id)
            .eq("user_id", current_user.id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Milestone not found")

        return

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "invalid input syntax for type uuid" in error_msg.lower():
            raise HTTPException(
                status_code=400, detail="Invalid milestone_id: must be a valid UUID"
            ) from e
        detail = f"Error deleting milestone: {error_msg}"
        raise HTTPException(status_code=500, detail=detail) from e
