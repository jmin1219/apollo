"""
Progress analysis tools for AI agents.

These tools help agents analyze user progress, calculate metrics,
and identify blockers - going beyond simple CRUD operations.
"""

from typing import Any
from datetime import datetime, timedelta
from supabase import Client


class ProgressTools:
    """
    Progress analysis tools for AI agents.

    Purpose:
    - Aggregate completion metrics
    - Calculate goal progress from milestones
    - Identify blockers and stuck tasks

    Design principles:
    - Read-only operations (no data modification)
    - Analytical insights for strategic decision-making
    - Token-efficient summaries
    """

    def __init__(self, supabase: Client):
        """Initialize ProgressTools with database client."""
        self.supabase = supabase

    async def get_weekly_progress(
        self,
        user_id: str
    ) -> dict[str, Any]:
        """
        Get user's progress for current week (Monday-Sunday).

        Args:
            user_id: Authenticated user ID

        Returns:
            Dict with weekly metrics:
            {
                "week_start": "2025-10-27",
                "week_end": "2025-11-02",
                "tasks_completed": 5,
                "total_minutes": 320,
                "tasks_by_project": {"APOLLO": 3, "NeetCode": 2},
                "milestones_updated": 2
            }
        """
        try:
            # Calculate week boundaries (Monday to Sunday)
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            week_start_str = week_start.strftime("%Y-%m-%d")
            week_end_str = week_end.strftime("%Y-%m-%d")

            # Query tasks completed this week
            completed_tasks = self.supabase.table("tasks")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("status", "completed")\
                .gte("updated_at", week_start_str)\
                .execute()  # type: ignore

            tasks_completed_count = len(completed_tasks.data) if completed_tasks.data else 0

            # Group by project
            tasks_by_project = {}
            for task in completed_tasks.data or []:
                project_name = task.get("project", "Uncategorized")
                tasks_by_project[project_name] = tasks_by_project.get(project_name, 0) + 1

            # Calculate total time spent
            total_minutes = sum(
                task.get("time_spent_minutes", 0) 
                for task in (completed_tasks.data or [])
            )

            # Count milestones updated this week
            updated_milestones = self.supabase.table("milestones")\
                .select("*")\
                .eq("user_id", user_id)\
                .gte("updated_at", week_start_str)\
                .execute()  # type: ignore

            milestones_updated_count = len(updated_milestones.data) if updated_milestones.data else 0

            return {
                "week_start": week_start_str,
                "week_end": week_end_str,
                "tasks_completed": tasks_completed_count,
                "total_minutes": total_minutes,
                "tasks_by_project": tasks_by_project,
                "milestones_updated": milestones_updated_count
            }
        
        except Exception as e:
            raise Exception(f"Database error calculating weekly progress: {str(e)}") from e

    async def get_goal_progress(
        self,
        user_id: str,
        goal_id: str
    ) -> dict[str, Any]:
        """
        Calculate overall goal progress from its milestones.

        Logic:
        - Get all milestones for this goal
        - Average their progress percentages
        - Count completed vs total milestones

        Args:
            user_id: Authenticated user ID
            goal_id: Goal to analyze

        Returns:
            Dict with goal progress:
            {
                "goal_id": "...",
                "overall_progress": 65,  # Average of milestone progress
                "milestones_total": 4,
                "milestones_completed": 2,
                "milestones_in_progress": 1,
                "milestones_not_started": 1
            }
        """
        try:
            # Verify goal exists and belongs to user
            goal_check = self.supabase.table("goals")\
                .select("*")\
                .eq("id", goal_id)\
                .eq("user_id", user_id)\
                .execute()  # type: ignore

            if not goal_check.data:  # type: ignore
                raise ValueError("Goal not found or access denied")

            # Get all milestones for this goal
            milestone_data = self.supabase.table("milestones")\
                .select("*")\
                .eq("goal_id", goal_id)\
                .eq("user_id", user_id)\
                .execute()  # type: ignore

            milestones = milestone_data.data or []

            # Handle empty milestones
            if len(milestones) == 0:
                return {
                    "goal_id": goal_id,
                    "overall_progress": 0,
                    "milestones_total": 0,
                    "milestones_completed": 0,
                    "milestones_in_progress": 0,
                    "milestones_not_started": 0
                }

            # Calculate average progress
            total_progress = sum(m.get("progress", 0) for m in milestones)
            overall_progress = round(total_progress / len(milestones))

            # Count milestones by status
            milestones_completed = sum(1 for m in milestones if m.get("status") == "completed")
            milestones_in_progress = sum(1 for m in milestones if m.get("status") == "in_progress")
            milestones_not_started = sum(1 for m in milestones if m.get("status") == "not_started")

            return {
                "goal_id": goal_id,
                "overall_progress": overall_progress,
                "milestones_total": len(milestones),
                "milestones_completed": milestones_completed,
                "milestones_in_progress": milestones_in_progress,
                "milestones_not_started": milestones_not_started
            }
        
        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"Database error calculating goal progress: {str(e)}") from e

    async def identify_blockers(
        self,
        user_id: str
    ) -> dict[str, Any]:
        """
        Identify tasks that are stuck or blocking progress.

        A task is a blocker if:
        - Status is "in_progress" for > 7 days (stuck)
        - Has high priority but status is "pending" (not started)
        - Due date passed but not completed (overdue)

        Args:
            user_id: Authenticated user ID

        Returns:
            Dict with blocker analysis:
            {
                "stuck_tasks": [...],      # In progress > 7 days
                "high_priority_pending": [...],  # High priority not started
                "overdue_tasks": [...],    # Past due date
                "blocker_count": 5
            }
        """
        try:
            # Find stuck tasks (in_progress > 7 days)
            seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            stuck_tasks = self.supabase.table("tasks")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("status", "in_progress")\
                .lt("updated_at", seven_days_ago)\
                .execute()  # type: ignore
            stuck_tasks_list = stuck_tasks.data or []

            # Find high priority pending tasks
            high_priority_pending = self.supabase.table("tasks")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("status", "pending")\
                .eq("priority", "high")\
                .execute()  # type: ignore
            high_priority_pending_list = high_priority_pending.data or []

            # Find overdue tasks (due_date < today, not completed)
            today = datetime.now().strftime("%Y-%m-%d")
            overdue_tasks = self.supabase.table("tasks")\
                .select("*")\
                .eq("user_id", user_id)\
                .not_.is_("due_date", 'null')\
                .lt("due_date", today)\
                .in_("status", ["pending", "in_progress"])\
                .execute()  # type: ignore
            overdue_tasks_list = overdue_tasks.data or []

            return {
                "stuck_tasks": stuck_tasks_list,
                "high_priority_pending": high_priority_pending_list,
                "overdue_tasks": overdue_tasks_list,
                "blocker_count": len(stuck_tasks_list) + len(high_priority_pending_list) + len(overdue_tasks_list)
            }
        
        except Exception as e:
            raise Exception(f"Database error identifying blockers: {str(e)}") from e
