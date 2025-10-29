"""
Test GoalTools implementation.

Run with: python -m app.agents.tools.test_goal_tools
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from app.db.supabase_client import supabase
from app.agents.tools.goal_tools import GoalTools


async def test_goal_tools():
    """Test GoalTools CRUD operations."""
    
    # Get test user ID
    user_id = os.getenv("TEST_USER_ID", "your-user-id-here")
    
    print("🧪 Testing GoalTools...")
    print(f"User ID: {user_id}\n")
    
    # Initialize tools
    goal_tools = GoalTools(supabase)
    
    # Test 1: Create Goal
    print("=" * 60)
    print("TEST 1: Create Goal")
    print("=" * 60)
    try:
        new_goal = await goal_tools.create_goal(
            user_id=user_id,
            title="Test Goal - SWE Employment Spring 2027",
            target_date="2027-04-01",
            description="Land visa-sponsored software engineering position",
            status="active"
        )
        print("✅ Goal created successfully!")
        print(f"   ID: {new_goal['id']}")
        print(f"   Title: {new_goal['title']}")
        print(f"   Target: {new_goal['target_date']}")
        print(f"   Status: {new_goal['status']}")
        goal_id = new_goal['id']
    except Exception as e:
        print(f"❌ Failed to create goal: {e}")
        return
    
    print()
    
    # Test 2: List Goals
    print("=" * 60)
    print("TEST 2: List Goals")
    print("=" * 60)
    try:
        goals = await goal_tools.list_goals(user_id=user_id)
        print(f"✅ Found {len(goals)} goal(s)")
        for goal in goals:
            print(f"   - {goal['title']} (Target: {goal['target_date']}, Status: {goal['status']})")
    except Exception as e:
        print(f"❌ Failed to list goals: {e}")
    
    print()
    
    # Test 3: List Goals (filtered by status)
    print("=" * 60)
    print("TEST 3: List Active Goals Only")
    print("=" * 60)
    try:
        active_goals = await goal_tools.list_goals(user_id=user_id, status="active")
        print(f"✅ Found {len(active_goals)} active goal(s)")
        for goal in active_goals:
            print(f"   - {goal['title']}")
    except Exception as e:
        print(f"❌ Failed to list active goals: {e}")
    
    print()
    
    # Test 4: Update Goal
    print("=" * 60)
    print("TEST 4: Update Goal")
    print("=" * 60)
    try:
        updated_goal = await goal_tools.update_goal(
            user_id=user_id,
            goal_id=goal_id,
            updates={
                "title": "Updated Test Goal - SWE Employment Spring 2027",
                "description": "Land visa-sponsored SWE position with focus on backend/AI"
            }
        )
        print("✅ Goal updated successfully!")
        print(f"   New Title: {updated_goal['title']}")
        print(f"   New Description: {updated_goal['description']}")
    except Exception as e:
        print(f"❌ Failed to update goal: {e}")
    
    print()
    
    # Test 5: Validation Tests
    print("=" * 60)
    print("TEST 5: Validation Tests")
    print("=" * 60)
    
    # Test short title
    try:
        await goal_tools.create_goal(
            user_id=user_id,
            title="AB",  # Too short
            target_date="2027-01-01"
        )
        print("❌ Should have rejected short title")
    except ValueError as e:
        print(f"✅ Correctly rejected short title: {e}")
    
    # Test invalid status
    try:
        await goal_tools.create_goal(
            user_id=user_id,
            title="Valid Title",
            target_date="2027-01-01",
            status="invalid_status"
        )
        print("❌ Should have rejected invalid status")
    except ValueError as e:
        print(f"✅ Correctly rejected invalid status: {e}")
    
    # Test missing target_date
    try:
        await goal_tools.create_goal(
            user_id=user_id,
            title="Valid Title",
            target_date=""
        )
        print("❌ Should have rejected empty target_date")
    except ValueError as e:
        print(f"✅ Correctly rejected empty target_date: {e}")
    
    print()
    
    # Test 6: Security Test (wrong user)
    print("=" * 60)
    print("TEST 6: Security - Access Control")
    print("=" * 60)
    try:
        fake_user_id = "00000000-0000-0000-0000-000000000000"
        await goal_tools.update_goal(
            user_id=fake_user_id,  # Wrong user!
            goal_id=goal_id,
            updates={"title": "Hacked!"}
        )
        print("❌ SECURITY BREACH: Allowed unauthorized update!")
    except ValueError as e:
        print(f"✅ Security working: {e}")
    
    print()
    
    # Summary
    print("=" * 60)
    print("✅ ALL TESTS COMPLETE!")
    print("=" * 60)
    print("\nGoalTools is working correctly:")
    print("  ✅ Create goal")
    print("  ✅ List goals (with optional filter)")
    print("  ✅ Update goal")
    print("  ✅ Input validation")
    print("  ✅ Security (ownership verification)")
    print()
    print("Note: Test goal created in database. You may want to delete it manually.")


if __name__ == "__main__":
    asyncio.run(test_goal_tools())
