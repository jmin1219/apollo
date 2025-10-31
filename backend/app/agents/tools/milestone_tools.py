"""
Tool functions for AI agents to manipulate milestones.

Security principles:
- ALWAYS validate user_id from authenticated context
- ALWAYS verify ownership before update/delete
- ALWAYS validate input (even from agent)
- Return meaningful errors (agent can explain to user)
"""

from typing import Any, Optional
from supabase import Client


class MilestoneTools:
    """
    Milestone manipulation tools for AI agents.

    Milestones = Quarterly checkpoints that advance toward goals

    Design principles:
    - Agent provides: title, description, target_date, progress (milestone content)
    - System provides: user_id (from authentication)
    - Security: Ownership verified for update/delete
    """

    def __init__(self, supabase: Client):
        """Initialize MilestoneTools with database client."""
        self.supabase = supabase

    async def create_milestone(
        self,
        user_id: str,
        goal_id: str,  # Which goal does this milestone belong to?
        title: str,
        target_date: str,
        description: Optional[str] = None,
        progress: int = 0,
        status: str = "not_started"
    ) -> dict[str, Any]:
        """
        Create new milestone for authenticated user.

        Args:
            user_id: Authenticated user ID (system-provided)
            goal_id: Parent goal UUID (agent-provided, must verify!)
            title: Milestone title (agent-provided, validate!)
            target_date: Target completion date (agent-provided)
            description: Optional description
            progress: Progress percentage 0-100 (default: 0)
            status: Initial status ("not_started", "in_progress", "completed")

        Returns:
            Created milestone dict

        Raises:
            ValueError: If validation fails
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[MILESTONE TOOL] create_milestone called: user_id={user_id}, goal_id={goal_id}, title={title}, target_date={target_date}")
        
        # Validate title
        if not title or not (3 <= len(title.strip()) <= 200):
            logger.error(f"[MILESTONE TOOL] Title validation failed: {title}")
            raise ValueError("Title must be between 3 and 200 characters.")
        
        # Validate status
        if status not in ["not_started", "in_progress", "completed"]:
            raise ValueError('Status must be one of: "not_started", "in_progress", "completed".')
        
        # Validate progress
        if not isinstance(progress, int) or not (0 <= progress <= 100):
            raise ValueError("Progress must be an integer between 0 and 100.")
        
        # Validate target_date
        if not target_date or not target_date.strip():
            raise ValueError("Target date must be provided.")
        
        # CRITICAL: Verify goal exists and belongs to user
        try:
            goal_check = self.supabase.table("goals")\
                .select("*")\
                .eq("id", goal_id)\
                .eq("user_id", user_id)\
                .execute()  # type: ignore
            
            if not goal_check.data:  # type: ignore
                raise ValueError("Goal not found or access denied")
        
        except Exception as e:
            raise ValueError("Goal not found or access denied") from e
        
        # Prepare data
        milestone_data = {
            "user_id": user_id,
            "goal_id": goal_id,
            "title": title.strip(),
            "description": description.strip() if description else None,
            "target_date": target_date.strip(),
            "progress": progress,
            "status": status
        }
        
        # Insert
        try:
            logger.info(f"[MILESTONE TOOL] Inserting milestone into database: {milestone_data}")
            response = self.supabase.table("milestones")\
                .insert(milestone_data)\
                .execute()  # type: ignore
            
            logger.info(f"[MILESTONE TOOL] Database response: {response.data}")
            
            if not response.data:  # type: ignore
                logger.error("[MILESTONE TOOL] No data returned from insert")
                raise Exception("Failed to create milestone - no data returned")
            
            logger.info(f"[MILESTONE TOOL] Successfully created milestone: {response.data[0]}")
            return response.data[0]  # type: ignore
        
        except Exception as e:
            logger.error(f"[MILESTONE TOOL] Database error: {str(e)}", exc_info=True)
            raise Exception(f"Database error creating milestone: {str(e)}") from e

    async def update_milestone_progress(
        self,
        user_id: str,
        milestone_id: str,
        progress: int
    ) -> dict[str, Any]:
        """
        Update milestone progress percentage.

        Args:
            user_id: Authenticated user ID
            milestone_id: Milestone to update
            progress: New progress percentage (0-100)

        Returns:
            Updated milestone dict

        Raises:
            ValueError: If validation fails or access denied
        """
        # Verify milestone exists and belongs to user
        try:
            milestone_check = self.supabase.table("milestones")\
                .select("*")\
                .eq("id", milestone_id)\
                .eq("user_id", user_id)\
                .execute()  # type: ignore

            if not milestone_check.data:  # type: ignore
                raise ValueError("Milestone not found or access denied")
        
        except Exception as e:
            raise ValueError("Milestone not found or access denied") from e
        
        # Validate progress
        if not isinstance(progress, int) or not (0 <= progress <= 100):
            raise ValueError("Progress must be an integer between 0 and 100.")
        
        # Auto-update status based on progress (BUSINESS LOGIC!)
        if progress == 0:
            status = "not_started"
        elif progress == 100:
            status = "completed"
        else:
            status = "in_progress"
        
        # Update milestone
        try:
            response = self.supabase.table("milestones")\
                .update({"progress": progress, "status": status})\
                .eq("id", milestone_id)\
                .execute()  # type: ignore

            if not response.data:  # type: ignore
                raise Exception("Failed to update milestone - no data returned")

            return response.data[0]  # type: ignore

        except Exception as e:
            raise Exception(f"Database error updating milestone: {str(e)}") from e

    async def list_milestones(
        self,
        user_id: str,
        goal_id: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        List user's milestones, optionally filtered by goal.

        Args:
            user_id: Authenticated user ID
            goal_id: Optional filter - only show milestones for this goal

        Returns:
            List of milestone dicts
        """
        try:
            # Build query
            query = self.supabase.table("milestones")\
                .select("*")\
                .eq("user_id", user_id)
            
            # Add goal_id filter if provided
            if goal_id:
                query = query.eq("goal_id", goal_id)
            
            # Order by target_date (closest first)
            response = query.order("target_date", desc=False)\
                .execute()  # type: ignore
            
            return response.data or []  # type: ignore
        
        except Exception as e:
            raise Exception(f"Database error listing milestones: {str(e)}") from e
