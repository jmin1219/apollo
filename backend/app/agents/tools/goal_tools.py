"""
Tool functions for AI agents to manipulate goals.

Security principles:
- ALWAYS validate user_id from authenticated context
- ALWAYS verify ownership before update/delete
- ALWAYS validate input (even from agent)
- Return meaningful errors (agent can explain to user)
"""

from typing import Any, Optional
from supabase import Client


class GoalTools:
    """
    Goal manipulation tools for AI agents.

    Goals = Yearly vision-level objectives with measurable targets

    Design principles:
    - Agent provides: title, description, target_date (goal content)
    - System provides: user_id (from authentication)
    - Security: Ownership verified for update/delete
    """

    def __init__(self, supabase: Client):
        """Initialize GoalTools with database client."""
        self.supabase = supabase

    async def create_goal(
        self,
        user_id: str,  # From authentication, NOT from agent!
        title: str,
        target_date: str,  # ISO format: "2027-04-01"
        description: Optional[str] = None,
        status: str = "active"
    ) -> dict[str, Any]:
        """
        Create new goal for authenticated user.

        Args:
            user_id: Authenticated user ID (system-provided)
            title: Goal title (agent-provided, validate!)
            target_date: Target completion date in ISO format (agent-provided)
            description: Optional description (agent-provided)
            status: Initial status - default "active"

        Returns:
            Created goal dict with id, title, status, etc.

        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        # Validate title
        if not title or not (3 <= len(title.strip()) <= 200):
            raise ValueError("Title must be between 3 and 200 characters.")
        
        # Validate status
        if status not in ["active", "completed", "archived"]:
            raise ValueError('Status must be one of: "active", "completed", "archived".')
        
        # Validate target_date
        if not target_date or not target_date.strip():
            raise ValueError("Target date must be provided.")

        # Prepare data for insertion
        goal_data = {
            "user_id": user_id,
            "title": title.strip(),
            "description": description.strip() if description else None,
            "target_date": target_date.strip(),
            "status": status
        }

        try:
            response = self.supabase.table("goals")\
                .insert(goal_data)\
                .execute()  # type: ignore
            
            if not response.data:  # type: ignore
                raise Exception("Failed to create goal - no data returned")
            
            return response.data[0]  # type: ignore

        except Exception as e:
            raise Exception(f"Database error creating goal: {str(e)}") from e

    async def update_goal(
        self,
        user_id: str,
        goal_id: str,
        updates: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Update existing goal.

        Args:
            user_id: Authenticated user ID
            goal_id: Goal to update (agent-provided)
            updates: Fields to update (agent-provided, validate!)

        Returns:
            Updated goal dict

        Raises:
            ValueError: If goal not found or access denied
        """
        # Verify goal exists and belongs to user
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

        # Validate and sanitize updates
        allowed_fields = ["title", "description", "target_date", "status"]
        validated_updates = {}

        for key, value in updates.items():
            if key not in allowed_fields:
                continue  # Skip disallowed fields silently

            # Validate specific fields
            if key == "title" and value:
                if not (3 <= len(value.strip()) <= 200):
                    raise ValueError("Title must be between 3 and 200 characters")
                validated_updates[key] = value.strip()
            
            elif key == "status":
                if value not in ["active", "completed", "archived"]:
                    raise ValueError('Status must be one of: "active", "completed", "archived"')
                validated_updates[key] = value
            
            elif key == "description":
                validated_updates[key] = value.strip() if value else None
            
            elif key == "target_date":
                if not value or not value.strip():
                    raise ValueError("Target date cannot be empty")
                validated_updates[key] = value.strip()

        # Perform update
        try:
            response = self.supabase.table("goals")\
                .update(validated_updates)\
                .eq("id", goal_id)\
                .execute()  # type: ignore
            
            if not response.data:  # type: ignore
                raise Exception("Failed to update goal - no data returned")
            
            return response.data[0]  # type: ignore
        
        except Exception as e:
            raise Exception(f"Database error updating goal: {str(e)}") from e

    async def list_goals(
        self,
        user_id: str,
        status: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        List user's goals, optionally filtered by status.

        Args:
            user_id: Authenticated user ID
            status: Optional status filter ("active", "completed", "archived")

        Returns:
            List of goal dicts
        """
        try:
            # Build query
            query = self.supabase.table("goals")\
                .select("*")\
                .eq("user_id", user_id)
            
            # Add status filter if provided
            if status:
                query = query.eq("status", status)
            
            # Order by target_date (closest deadlines first)
            response = query.order("target_date", desc=False)\
                .execute()  # type: ignore

            return response.data or []  # type: ignore

        except Exception as e:
            raise Exception(f"Database error listing goals: {str(e)}") from e
