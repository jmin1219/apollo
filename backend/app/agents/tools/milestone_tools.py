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
        # TODO: Implement validation and creation
        # 1. Validate title (3-200 characters)
        # 2. Validate status (must be: "not_started", "in_progress", "completed")
        # 3. Validate progress (0-100 integer)
        # 4. VERIFY goal_id exists and belongs to user (IMPORTANT!)
        # 5. Insert into "milestones" table
        
        pass

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
        # TODO: Implement progress update
        # 1. Verify milestone exists and belongs to user
        # 2. Validate progress (0-100 integer)
        # 3. Auto-update status based on progress:
        #    - progress == 0: status = "not_started"
        #    - 0 < progress < 100: status = "in_progress"  
        #    - progress == 100: status = "completed"
        # 4. Update milestone
        
        pass

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
        # TODO: Implement list query
        # 1. Query milestones table for user_id
        # 2. If goal_id provided, filter by goal_id
        # 3. Order by target_date (closest first)
        # 4. Return list
        
        pass
