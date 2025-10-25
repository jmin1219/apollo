"""
Manual test for LifeCoordinator agent.
Run: python -m backend.test_agent
"""
import asyncio
import os
from dotenv import load_dotenv
from app.agents.life_coordinator import LifeCoordinator  # ← Fixed import

async def test_agent():
    # Load API key
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env")
        return

    print("🚀 Initializing Life Coordinator agent...")
    agent = LifeCoordinator(api_key=api_key)

    print("✅ Agent initialized!")
    print(f"   Model: {agent.model}")
    print(f"   System prompt length: {len(agent.system_prompt)} chars\n")

    # Test 1: Simple query without context
    print("=" * 60)
    print("TEST 1: Simple query (no user context)")
    print("=" * 60)

    messages = [
        {"role": "user", "content": "What should I focus on today?"}
    ]

    print("\n📤 Sending: 'What should I focus on today?'")
    print("⏳ Waiting for response...\n")

    response = await agent.generate_response(
        user_id="test_user",
        messages=messages,
        user_context=None
    )

    print("📥 Response:")
    print(response)
    print()

    # Test 2: Query with mock context
    print("=" * 60)
    print("TEST 2: Query with user context")
    print("=" * 60)

    mock_context = {
        "tasks": [
            {"title": "Complete APOLLO Module 2.1", "status": "in_progress"},
            {"title": "NeetCode: Two Sum", "status": "pending"},
            {"title": "CS5001 Assignment 3", "status": "pending"},
            {"title": "Zone 2 cardio - 30 min", "status": "pending"}
        ],
        "stats": {
            "total_tasks": 15,
            "pending_tasks": 12
        }
    }

    messages = [
        {"role": "user", "content": "I have 2 hours today. What's the highest priority?"}
    ]

    print("\n📤 Sending: 'I have 2 hours today. What's the highest priority?'")
    print("📋 User Context:")
    print(f"   - 4 tasks visible (15 total, 12 pending)")
    print("⏳ Waiting for response...\n")

    response = await agent.generate_response(
        user_id="test_user",
        messages=messages,
        user_context=mock_context
    )

    print("📥 Response:")
    print(response)
    print()

    print("=" * 60)
    print("✅ Tests complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_agent())
