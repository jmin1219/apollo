"""
Tool functions for AI agents to manipulate tasks.

Security principles:
- ALWAYS validate user_id from authenticated context (never trust agent)
- ALWAYS verify ownership before update/delete
- ALWAYS validate input (even from agent)
- Return meaningful errors (agent can explain to user)
"""

from typing import Any, Optional
from supabase import Client


class TaskTools:
    """
    Task manipulation tools for AI agents.

    Design principles:
    - Agent provides: title, description, status (task content)
    - System provides: user_id (from authentication)
    - Security: Ownership verified for update/delete

    Why separate class?
    - Testable (can mock Supabase)
    - Reusable across multiple agents
    - Clear responsibility boundary
    - Audit logging possible
    """

    def __init__(self, supabase: Client):
        """
        Initialize TaskTools with database client.

        Args:
            supabase: Authenticated Supabase client
        """
        self.supabase = supabase

    async def create_task(
        self,
        user_id: str,  # From authentication, NOT from agent!
        title: str,
        description: Optional[str] = None,
        status: str = "pending",
        milestone_id: Optional[str] = None,
        project: Optional[str] = None,
        priority: str = "medium"
    ) -> dict[str, Any]:
        """
        Create new task for authenticated user.

        Security: user_id comes from authentication, not agent input

        Args:
            user_id: Authenticated user ID (system-provided, trusted)
            title: Task title (agent-provided, validate!)
            description: Optional description (agent-provided)
            status: Initial status (agent-provided, validate!)

        Returns:
            Created task dict with id, title, status, etc.

        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        # Validate title
        if not title or len(title.strip()) < 3:
            raise ValueError("Task title must be at least 3 characters")
        if len(title) > 200:
            raise ValueError("Task title must be less than 200 characters")

        # Validate status
        valid_statuses = ["pending", "in_progress", "completed"]
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")

        # Validate priority
        valid_priorities = ["high", "medium", "low"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")

        # Create Task in database
        try:
            response = self.supabase.table("tasks").insert({
                "user_id": user_id,
                "title": title.strip(),
                "description": description.strip() if description else None,
                "status": status,
                "milestone_id": milestone_id,
                "project": project,
                "priority": priority
            }).execute()  # type: ignore

            if not response.data:  # type: ignore
                raise Exception("Failed to create task - no data returned")

            return response.data[0]  # type: ignore

        except Exception as e:
            # Re-raise with context for debugging
            raise Exception(f"Database error creating task: {str(e)}") from e

    async def update_task(
        self,
        user_id: str,  # From authentication
        task_id: str,  # From agent
        updates: dict[str, Any]  # From agent
    ) -> dict[str, Any]:
        """
        Update existing task.

        CRITICAL SECURITY: Verify task belongs to user before updating!

        Args:
            user_id: Authenticated user ID (system-provided)
            task_id: Task to update (agent-provided)
            updates: Fields to update (agent-provided, validate!)

        Returns:
            Updated task dict

        Raises:
            ValueError: If task not found or access denied
            Exception: If database operation fails
        """

        try:
            # Check if task exists and belongs to user
            task_check = self.supabase.table("tasks")\
                .select("*")\
                .eq("id", task_id)\
                .eq("user_id", user_id)\
                .execute()  # type: ignore

            if not task_check.data:  # type: ignore
                raise ValueError("Task not found or access denied")

        except Exception as e:
            raise ValueError("Task not found or access denied") from e

        # Validate updates
        allowed_fields = ["title", "description", "status", "milestone_id", "project", "priority"]
        validated_updates = {}

        for key, value in updates.items():
            if key not in allowed_fields:
                # Silently skip disallowed fields (don't error)
                # Why? Agent might try to update user_id accidentally
                continue

            # Validate specific fields
            if key == "title" and value:
                if len(value.strip()) < 3:
                    raise ValueError("Title must be at least 3 characters")
                if len(value) > 200:
                    raise ValueError("Title must be less than 200 characters")
                validated_updates[key] = value.strip()

            elif key == "status":
                valid_statuses = ["pending", "in_progress", "completed"]
                if value not in valid_statuses:
                    raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
                validated_updates[key] = value

            elif key == "description":
                validated_updates[key] = value.strip() if value else None

            elif key == "milestone_id":
                validated_updates[key] = value  # UUID, no stripping needed

            elif key == "project":
                validated_updates[key] = value.strip() if value else None

            elif key == "priority":
                valid_priorities = ["high", "medium", "low"]
                if value not in valid_priorities:
                    raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")
                validated_updates[key] = value

        # Perform update
        try:
            response = self.supabase.table("tasks")\
                .update(validated_updates)\
                .eq("id", task_id)\
                .execute()  # type: ignore

            if not response.data:  # type: ignore
                raise Exception("Failed to update task - no data returned")

            return response.data[0]  # type: ignore

        except Exception as e:
            raise Exception(f"Database error updating task: {str(e)}") from e

    async def delete_task(
        self,
        user_id: str,
        task_id: str
    ) -> bool:
        """
        Delete task.

        CRITICAL: Verify ownership before deletion!

        Args:
            user_id: Authenticated user ID
            task_id: Task to delete

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If task not found or access denied
        """
        try:
            # Step 1: Verify ownership
            task_check = self.supabase.table("tasks")\
                .select("*")\
                .eq("id", task_id)\
                .eq("user_id", user_id)\
                .execute()  # type: ignore

            if not task_check.data:  # type: ignore
                raise ValueError("Task not found or access denied")

            # Step 2: Delete
            response = self.supabase.table("tasks")\
                .delete()\
                .eq("id", task_id)\
                .execute()  # type: ignore

            # Step 3: Return success
            return True

        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            raise Exception(f"Database error deleting task: {str(e)}") from e
