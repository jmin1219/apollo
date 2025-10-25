"""
Quick test for task deletion with explicit confirmation.
Run: python -m app.agents.tests.test_deletion
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
from app.agents.tools.task_tools import TaskTools
from app.db.supabase_client import supabase


async def test_deletion():
    env_path = backend_dir / '.env'
    load_dotenv(env_path)
    api_key = os.getenv("OPENAI_API_KEY")
    user_id = "80107cd3-82b9-4c36-9981-00418f9b63f8"
    
    agent = LifeCoordinator(api_key=api_key)
    task_tools = TaskTools(supabase)
    
    # Get context
    agent_context = await create_agent_context(user_id=user_id, message="")
    user_context = agent_context_to_dict(agent_context)
    
    print("📋 Current tasks:")
    for task in user_context['tasks']:
        print(f"   - ID: {task['id'][:8]}... | [{task['status']}] {task['title']}")
    
    # More explicit deletion request
    messages = [
        {"role": "user", "content": "Remove the 'Buy groceries this weekend' task. Yes, I'm sure, delete it."}
    ]
    
    print("\n📤 User: 'Remove the Buy groceries this weekend task. Yes, I'm sure, delete it.'")
    print("⏳ Waiting...\n")
    
    result = await agent.generate_response(
        user_id=user_id,
        messages=messages,
        user_context=user_context,
        task_tools=task_tools
    )
    
    print("📥 Agent Response:")
    print(result["response"])
    print()
    
    if result["tool_calls"]:
        print("🔧 Tool Calls:")
        for call in result["tool_calls"]:
            print(f"   - {call['tool']}: {call['status']}")
            if call['status'] == 'error':
                print(f"     ❌ Error: {call['error']}")
    
    # Verify
    print("\n🔍 Verifying...")
    new_context = await create_agent_context(user_id=user_id, message="")
    new_user_context = agent_context_to_dict(new_context)
    
    grocery_task = next((t for t in new_user_context['tasks'] if 'groceries' in t['title'].lower()), None)
    
    if grocery_task:
        print("❌ Task still exists")
    else:
        print("✅ Task deleted successfully!")
    
    print(f"\nTask count: {len(user_context['tasks'])} → {len(new_user_context['tasks'])}")


if __name__ == "__main__":
    asyncio.run(test_deletion())
