"""
Test streaming responses from LifeCoordinator.
Run: python -m app.agents.tests.test_streaming
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.agents.life_coordinator import LifeCoordinator
from app.agents.context import create_agent_context, agent_context_to_dict


async def test_streaming():
    """Test streaming response from agent."""
    
    env_path = backend_dir / '.env'
    load_dotenv(env_path)
    api_key = os.getenv("OPENAI_API_KEY")
    user_id = "80107cd3-82b9-4c36-9981-00418f9b63f8"
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return
    
    print("🚀 Testing streaming response...")
    print()
    
    # Initialize agent
    agent = LifeCoordinator(api_key=api_key)
    
    # Get real context
    agent_context = await create_agent_context(user_id=user_id, message="")
    user_context = agent_context_to_dict(agent_context)
    
    # Test query
    messages = [
        {"role": "user", "content": "What should I focus on for the next 2 hours?"}
    ]
    
    print("📤 User: 'What should I focus on for the next 2 hours?'")
    print()
    print("📥 Agent (streaming):")
    print("-" * 60)
    
    # Stream response word-by-word
    full_response = ""
    async for chunk in agent.generate_response_stream(
        user_id=user_id,
        messages=messages,
        user_context=user_context
    ):
        print(chunk, end="", flush=True)  # Print without newline
        full_response += chunk
    
    print()
    print("-" * 60)
    print()
    print("✅ Streaming complete!")
    print(f"📊 Total characters: {len(full_response)}")
    print()
    
    # Test 2: No context (should ask questions)
    print("=" * 60)
    print("TEST 2: Streaming without context")
    print("=" * 60)
    print()
    
    messages2 = [
        {"role": "user", "content": "Help me plan my day"}
    ]
    
    print("📤 User: 'Help me plan my day'")
    print()
    print("📥 Agent (streaming):")
    print("-" * 60)
    
    async for chunk in agent.generate_response_stream(
        user_id=user_id,
        messages=messages2,
        user_context=None
    ):
        print(chunk, end="", flush=True)
    
    print()
    print("-" * 60)
    print()
    print("✅ All streaming tests complete!")


if __name__ == "__main__":
    asyncio.run(test_streaming())
