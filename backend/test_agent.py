"""
Manual test for LifeCoordinator agent with REAL Supabase data.
Run from backend directory: python -m app.agents.test_agent
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend directory to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.agents.life_coordinator import LifeCoordinator
from app.agents.context import create_agent_context, agent_context_to_dict

async def test_agent():
    # Load API key from backend/.env
    env_path = backend_dir / '.env'
    load_dotenv(env_path)
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env")
        return

    print("🚀 Initializing Life Coordinator agent...")
    agent = LifeCoordinator(api_key=api_key)

    print("✅ Agent initialized!")
    print(f"   Model: {agent.model}")
    print(f"   System prompt length: {len(agent.system_prompt)} chars\n")

    # Get your actual user_id from database
    # TODO: Replace with your real user_id
    # You can find it by logging into your app or checking Supabase
    user_id = "80107cd3-82b9-4c36-9981-00418f9b63f8"  # ← Replace this!

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
        user_id=user_id,
        messages=messages,
        user_context=None
    )

    print("📥 Response:")
    print(response)
    print()

    # Test 2: Query with REAL context from Supabase
    print("=" * 60)
    print("TEST 2: Query with REAL user context from Supabase")
    print("=" * 60)

    # Fetch real context
    print("\n🔍 Fetching your real tasks from Supabase...")
    agent_context = await create_agent_context(
        user_id=user_id,
        message="I have 2 hours today. What's the highest priority?"
    )

    # Convert to format LifeCoordinator expects
    user_context = agent_context_to_dict(agent_context)

    print(f"✅ Fetched {len(user_context['tasks'])} tasks")
    print("📋 Your actual tasks:")
    for task in user_context['tasks'][:5]:  # Show first 5
        print(f"   - [{task['status']}] {task['title']}")
    if len(user_context['tasks']) > 5:
        print(f"   ... and {len(user_context['tasks']) - 5} more\n")

    messages = [
        {"role": "user", "content": "I have 2 hours today. What's the highest priority?"}
    ]

    print("📤 Sending: 'I have 2 hours today. What's the highest priority?'")
    print("⏳ Waiting for response...\n")

    response = await agent.generate_response(
        user_id=user_id,
        messages=messages,
        user_context=user_context
    )

    print("📥 Response:")
    print(response)
    print()

    print("=" * 60)
    print("✅ Tests complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_agent())
