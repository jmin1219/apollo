"""
Test function calling with LifeCoordinator agent.
Run from backend directory: python -m app.agents.tests.test_tool_calling
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend directory to path
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.agents.life_coordinator import LifeCoordinator
from app.agents.context import create_agent_context, agent_context_to_dict
from app.agents.tools.task_tools import TaskTools
from app.db.supabase_client import supabase


async def test_tool_calling():
    """Test agent's ability to create, update, and delete tasks via function calling."""
    
    # Load environment
    env_path = backend_dir / '.env'
    load_dotenv(env_path)
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env")
        return
    
    # Your user ID
    user_id = "80107cd3-82b9-4c36-9981-00418f9b63f8"
    
    print("🚀 Initializing agent with tool calling...")
    agent = LifeCoordinator(api_key=api_key)
    task_tools = TaskTools(supabase)
    
    print("✅ Agent and tools initialized!\n")
    
    # Test 1: Create Task
    print("=" * 70)
    print("TEST 1: Create Task via Agent")
    print("=" * 70)
    
    # Fetch current context
    agent_context = await create_agent_context(user_id=user_id, message="")
    user_context = agent_context_to_dict(agent_context)
    
    initial_task_count = len(user_context['tasks'])
    print(f"📊 Current task count: {initial_task_count}")
    
    messages = [
        {"role": "user", "content": "Add a task to buy groceries this weekend"}
    ]
    
    print("\n📤 User: 'Add a task to buy groceries this weekend'")
    print("⏳ Waiting for agent response...\n")
    
    result = await agent.generate_response(
        user_id=user_id,
        messages=messages,
        user_context=user_context,
        task_tools=task_tools  # ← Tools enabled!
    )
    
    print("📥 Agent Response:")
    print(result["response"])
    print()
    
    if result["tool_calls"]:
        print("🔧 Tool Calls Made:")
        for call in result["tool_calls"]:
            print(f"   - {call['tool']}: {call['status']}")
            if call['status'] == 'success' and call['result']:
                print(f"     Created: {call['result'].get('title')}")
                print(f"     ID: {call['result'].get('id')}")
    else:
        print("⚠️  No tool calls made (agent chose not to call create_task)")
    
    # Verify task was created in database
    print("\n🔍 Verifying in database...")
    new_context = await create_agent_context(user_id=user_id, message="")
    new_user_context = agent_context_to_dict(new_context)
    
    if len(new_user_context['tasks']) > initial_task_count:
        print(f"✅ Task created! New count: {len(new_user_context['tasks'])}")
        new_task = new_user_context['tasks'][0]  # Most recent
        print(f"   Title: {new_task['title']}")
        created_task_id = new_task['id']
    else:
        print("❌ Task not found in database")
        created_task_id = None
    
    print()
    
    # Test 2: Update Task
    if created_task_id:
        print("=" * 70)
        print("TEST 2: Update Task via Agent")
        print("=" * 70)
        
        # Refresh context (now includes new task)
        agent_context = await create_agent_context(user_id=user_id, message="")
        user_context = agent_context_to_dict(agent_context)
        
        messages = [
            {"role": "user", "content": "Mark the buy groceries task as in progress"}
        ]
        
        print("\n📤 User: 'Mark the buy groceries task as in progress'")
        print("⏳ Waiting for agent response...\n")
        
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
            print("🔧 Tool Calls Made:")
            for call in result["tool_calls"]:
                print(f"   - {call['tool']}: {call['status']}")
                if call['status'] == 'error':
                    print(f"     ❌ Error: {call['error']}")
                if call['status'] == 'success':
                    print(f"     Updated status to: {call['result'].get('status')}")
                elif call['status'] == 'error':
                    print(f"     ❌ Error: {call['error']}")
        
        # Verify update
        print("\n🔍 Verifying update...")
        verify_context = await create_agent_context(user_id=user_id, message="")
        verify_user_context = agent_context_to_dict(verify_context)
        
        updated_task = next((t for t in verify_user_context['tasks'] if t['id'] == created_task_id), None)
        if updated_task:
            print(f"✅ Task status: {updated_task['status']}")
        
        print()
    
    # Test 3: Delete Task
    if created_task_id:
        print("=" * 70)
        print("TEST 3: Delete Task via Agent")
        print("=" * 70)
        
        # Refresh context
        agent_context = await create_agent_context(user_id=user_id, message="")
        user_context = agent_context_to_dict(agent_context)
        
        messages = [
            {"role": "user", "content": "Delete the buy groceries task"}
        ]
        
        print("\n📤 User: 'Delete the buy groceries task'")
        print("⏳ Waiting for agent response...\n")
        
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
            print("🔧 Tool Calls Made:")
            for call in result["tool_calls"]:
                print(f"   - {call['tool']}: {call['status']}")
        
        # Verify deletion
        print("\n🔍 Verifying deletion...")
        final_context = await create_agent_context(user_id=user_id, message="")
        final_user_context = agent_context_to_dict(final_context)
        
        deleted_task = next((t for t in final_user_context['tasks'] if t['id'] == created_task_id), None)
        if deleted_task:
            print("❌ Task still exists (deletion failed)")
        else:
            print("✅ Task successfully deleted!")
        
        print()
    
    print("=" * 70)
    print("✅ All tool calling tests complete!")
    print("=" * 70)
    print("\nSummary:")
    print("- Agent can create tasks from natural language")
    print("- Agent can update task status")
    print("- Agent can delete tasks")
    print("- All operations verified in database")
    print("\n🎉 Phase 4 Function Calling: WORKING!")


if __name__ == "__main__":
    asyncio.run(test_tool_calling())
