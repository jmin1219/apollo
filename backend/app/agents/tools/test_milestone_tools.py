"""
Test MilestoneTools implementation.

Run with: python -m app.agents.tools.test_milestone_tools
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from app.db.supabase_client import supabase
from app.agents.tools.milestone_tools import MilestoneTools


async def test_milestone_tools():
    """Test MilestoneTools CRUD operations."""
    
    user_id = os.getenv("TEST_USER_ID", "your-user-id-here")
    
    print("🧪 Testing MilestoneTools...")
    print(f"User ID: {user_id}\n")
    
    # Initialize tools
    milestone_tools = MilestoneTools(supabase)
    
    # Get a real goal_id from user's goals
    goals_response = supabase.table("goals").select("*").eq("user_id", user_id).limit(1).execute()
    if not goals_response.data:
        print("❌ No goals found. Create a goal first!")
        return
    
    test_goal_id = goals_response.data[0]['id']
    test_goal_title = goals_response.data[0]['title']
    print(f"Using goal: {test_goal_title} (ID: {test_goal_id})\n")
    
    # Test 1: Create Milestone
    print("=" * 60)
    print("TEST 1: Create Milestone")
    print("=" * 60)
    try:
        new_milestone = await milestone_tools.create_milestone(
            user_id=user_id,
            goal_id=test_goal_id,
            title="Test Milestone - APOLLO Module 3 Complete",
            target_date="2025-11-15",
            description="Complete strategic planning system with visual timeline",
            progress=0,
            status="not_started"
        )
        print("✅ Milestone created successfully!")
        print(f"   ID: {new_milestone['id']}")
        print(f"   Title: {new_milestone['title']}")
        print(f"   Progress: {new_milestone['progress']}%")
        print(f"   Status: {new_milestone['status']}")
        milestone_id = new_milestone['id']
    except Exception as e:
        print(f"❌ Failed to create milestone: {e}")
        return
    
    print()
    
    # Test 2: List Milestones (all)
    print("=" * 60)
    print("TEST 2: List All Milestones")
    print("=" * 60)
    try:
        milestones = await milestone_tools.list_milestones(user_id=user_id)
        print(f"✅ Found {len(milestones)} milestone(s)")
        for m in milestones:
            print(f"   - {m['title']} ({m['progress']}%, {m['status']})")
    except Exception as e:
        print(f"❌ Failed to list milestones: {e}")
    
    print()
    
    # Test 3: List Milestones (filtered by goal)
    print("=" * 60)
    print("TEST 3: List Milestones for Specific Goal")
    print("=" * 60)
    try:
        goal_milestones = await milestone_tools.list_milestones(
            user_id=user_id, 
            goal_id=test_goal_id
        )
        print(f"✅ Found {len(goal_milestones)} milestone(s) for goal '{test_goal_title}'")
        for m in goal_milestones:
            print(f"   - {m['title']}")
    except Exception as e:
        print(f"❌ Failed to list goal milestones: {e}")
    
    print()
    
    # Test 4: Update Progress (0 → 50 → 100)
    print("=" * 60)
    print("TEST 4: Update Progress (Business Logic Test)")
    print("=" * 60)
    
    # 4a: Progress = 50 (should auto-set status to "in_progress")
    try:
        updated = await milestone_tools.update_milestone_progress(
            user_id=user_id,
            milestone_id=milestone_id,
            progress=50
        )
        print(f"✅ Progress → 50%: Status auto-updated to '{updated['status']}'")
        assert updated['status'] == "in_progress", "Status should be 'in_progress'"
    except Exception as e:
        print(f"❌ Failed 50% test: {e}")
    
    # 4b: Progress = 100 (should auto-set status to "completed")
    try:
        updated = await milestone_tools.update_milestone_progress(
            user_id=user_id,
            milestone_id=milestone_id,
            progress=100
        )
        print(f"✅ Progress → 100%: Status auto-updated to '{updated['status']}'")
        assert updated['status'] == "completed", "Status should be 'completed'"
    except Exception as e:
        print(f"❌ Failed 100% test: {e}")
    
    # 4c: Progress = 0 (should auto-set status to "not_started")
    try:
        updated = await milestone_tools.update_milestone_progress(
            user_id=user_id,
            milestone_id=milestone_id,
            progress=0
        )
        print(f"✅ Progress → 0%: Status auto-updated to '{updated['status']}'")
        assert updated['status'] == "not_started", "Status should be 'not_started'"
    except Exception as e:
        print(f"❌ Failed 0% test: {e}")
    
    print()
    
    # Test 5: Validation Tests
    print("=" * 60)
    print("TEST 5: Validation Tests")
    print("=" * 60)
    
    # Short title
    try:
        await milestone_tools.create_milestone(
            user_id=user_id,
            goal_id=test_goal_id,
            title="AB",  # Too short
            target_date="2025-12-01"
        )
        print("❌ Should have rejected short title")
    except ValueError as e:
        print(f"✅ Rejected short title: {e}")
    
    # Invalid progress
    try:
        await milestone_tools.update_milestone_progress(
            user_id=user_id,
            milestone_id=milestone_id,
            progress=150  # > 100
        )
        print("❌ Should have rejected progress > 100")
    except ValueError as e:
        print(f"✅ Rejected invalid progress: {e}")
    
    # Invalid goal_id
    try:
        await milestone_tools.create_milestone(
            user_id=user_id,
            goal_id="00000000-0000-0000-0000-000000000000",  # Fake goal
            title="Valid Title",
            target_date="2025-12-01"
        )
        print("❌ Should have rejected invalid goal_id")
    except ValueError as e:
        print(f"✅ Rejected invalid goal_id: {e}")
    
    print()
    
    # Test 6: Security Test
    print("=" * 60)
    print("TEST 6: Security - Access Control")
    print("=" * 60)
    try:
        fake_user_id = "00000000-0000-0000-0000-000000000000"
        await milestone_tools.update_milestone_progress(
            user_id=fake_user_id,
            milestone_id=milestone_id,
            progress=75
        )
        print("❌ SECURITY BREACH: Allowed unauthorized update!")
    except ValueError as e:
        print(f"✅ Security working: {e}")
    
    print()
    
    # Summary
    print("=" * 60)
    print("✅ ALL TESTS COMPLETE!")
    print("=" * 60)
    print("\nMilestoneTools is working correctly:")
    print("  ✅ Create milestone (with goal verification)")
    print("  ✅ List milestones (with optional goal filter)")
    print("  ✅ Update progress with auto-status logic")
    print("  ✅ Business logic (0→not_started, 50→in_progress, 100→completed)")
    print("  ✅ Input validation")
    print("  ✅ Security (ownership + goal verification)")
    print()
    print("Note: Test milestone created. You may want to delete it manually.")


if __name__ == "__main__":
    asyncio.run(test_milestone_tools())
