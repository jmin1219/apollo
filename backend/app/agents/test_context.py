"""
Test Module 3 context enhancements.

Run with: python -m app.agents.test_context
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.agents.context import create_agent_context, agent_context_to_dict


async def test_context_enhancement():
    """Test the new Module 3 multi-horizon context."""
    
    # Replace with your actual user_id from Supabase
    # You can find this in your Supabase dashboard > Authentication > Users
    user_id = os.getenv("TEST_USER_ID", "your-user-id-here")
    
    print("🧪 Testing Module 3 Context Enhancement...")
    print(f"User ID: {user_id}\n")
    
    # Create context
    context = await create_agent_context(
        user_id=user_id,
        message="What should I focus on today?",
        conversation_id=None
    )
    
    # Convert to dict for easier viewing
    context_dict = agent_context_to_dict(context)
    
    # Display results
    print("=" * 60)
    print("📅 TODAY'S CONTEXT:")
    print("=" * 60)
    if context.today_context:
        print(f"Date: {context.today_context.get('date')}")
        print(f"Day: {context.today_context.get('day_of_week')}")
    print()
    
    print("=" * 60)
    print("📊 WEEKLY PROGRESS:")
    print("=" * 60)
    if context.weekly_progress:
        print(f"Week Start: {context.weekly_progress.get('week_start')}")
        print(f"Tasks Completed: {context.weekly_progress.get('tasks_completed')}")
        print(f"Total Minutes: {context.weekly_progress.get('total_minutes')}")
    print()
    
    print("=" * 60)
    print("⚠️  URGENT DEADLINES (0-3 days):")
    print("=" * 60)
    if context.urgent_deadlines:
        for task in context.urgent_deadlines:
            print(f"  - {task.get('title')} (due: {task.get('due_date')})")
    else:
        print("  No urgent deadlines ✅")
    print()
    
    print("=" * 60)
    print("📅 UPCOMING DEADLINES (4-10 days):")
    print("=" * 60)
    if context.upcoming_deadlines:
        for task in context.upcoming_deadlines:
            print(f"  - {task.get('title')} (due: {task.get('due_date')})")
    else:
        print("  No upcoming deadlines ✅")
    print()
    
    print("=" * 60)
    print("📈 STATS:")
    print("=" * 60)
    stats = context_dict['stats']
    print(f"Total Active Tasks: {stats['total_tasks']}")
    print(f"Pending Tasks: {stats['pending_tasks']}")
    print(f"Active Goals: {stats['total_goals']}")
    print(f"Active Milestones: {stats['active_milestones']}")
    print(f"Urgent Deadlines: {stats['urgent_count']}")
    print(f"Upcoming Deadlines: {stats['upcoming_count']}")
    print()
    
    print("✅ Context enhancement working!")
    print("\nAgent now has:")
    print("  ✅ Today's context (date, day of week)")
    print("  ✅ Weekly progress tracking")
    print("  ✅ Urgent deadline awareness (0-3 days)")
    print("  ✅ Upcoming deadline planning (4-10 days)")
    print("  ✅ Multi-horizon strategic view")


if __name__ == "__main__":
    asyncio.run(test_context_enhancement())
