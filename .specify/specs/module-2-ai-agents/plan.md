# Module 2: AI Agent Foundation - IMPLEMENTATION PLAN

**Module:** 2.1 - AI Agent Foundation  
**Estimated Time:** 10-12 hours across 4-5 sessions  
**Prerequisites:** Module 1 Complete (REST API + Auth + Frontend)

---

## Implementation Approach

**Philosophy:** Build incrementally, learn deeply, test frequently

**Phases:**
1. **Setup & Dependencies** (1 hour) - Install SDK, create project structure
2. **Agent Foundation** (2 hours) - Basic agent that responds to messages
3. **Context Management** (2 hours) - Agent accesses user tasks
4. **Tool Calling** (3 hours) - Agent can create/modify tasks
5. **Streaming & Frontend** (3 hours) - Real-time chat interface
6. **Testing & Polish** (1 hour) - Verification and cleanup

---

## Phase 1: Setup & Dependencies (1 hour)

### Learning Objectives
- **NEW:** Understanding Python package management and dependencies
- **NEW:** Project structure for agent-based systems
- **Review:** Environment variable security patterns

### Tasks

#### 1.1: Install OpenAI SDK and Dependencies

```bash
# In backend/ directory
pip install openai python-dotenv
pip freeze > requirements.txt
```

**Concepts to Learn:**
- What is the OpenAI SDK? (wrapper around REST API)
- Why use SDK vs raw API calls? (convenience, error handling, types)
- Package versioning (semantic versioning: major.minor.patch)

**Teaching Moment:**
- Show package dependencies: `pip show openai`
- Explain: SDK depends on httpx, pydantic, etc.
- Trade-off: Convenience vs control vs bundle size

---

#### 1.2: Configure OpenAI API Key

**TODO:** Add to `.env`
```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
```

**Concepts to Learn:**
- **NEW:** API keys and authentication patterns
- **NEW:** Environment variables vs hardcoded secrets
- **Security:** Why .env should NEVER be committed

**Teaching Moment:**
- What happens if API key leaks? (costs money, security risk)
- How does .env work? (loaded by python-dotenv at runtime)
- Best practice: Different keys for dev/staging/prod

**Interview Question:** "How do you manage secrets in production?"
**Answer:** Environment variables, secret managers (AWS Secrets Manager, HashiCorp Vault), never in code or version control

---

#### 1.3: Create Project Structure

```
backend/
└── app/
    ├── agents/
    │   ├── __init__.py
    │   ├── base.py                  # Agent base class/interface
    │   ├── life_coordinator.py      # First agent implementation
    │   └── tools/
    │       ├── __init__.py
    │       └── task_tools.py        # Tool functions (CRUD)
    ├── routes/
    │   └── chat.py                  # NEW: Chat API endpoints
    └── models/
        └── conversation.py          # NEW: Conversation/Message models
```

**Concepts to Learn:**
- **NEW:** Module organization for agent systems
- **NEW:** Separation of concerns (agents, tools, routes)
- **Review:** Python modules and imports

**Teaching Moment:**
- Why separate `agents/` from `routes/`? (business logic vs API layer)
- Why `tools/` subdirectory? (reusable functions, testable)
- Pattern: Keep agents framework-agnostic (could swap FastAPI for Flask)

---

### Phase 1 Checkpoint

**Verify:**
- [ ] OpenAI SDK installed (`pip list | grep openai`)
- [ ] .env contains OPENAI_API_KEY
- [ ] Directory structure created
- [ ] All `__init__.py` files present (makes directories Python modules)

**Understanding Check:**
Before moving forward, answer:
1. What's the difference between SDK and API?
2. Why do we use environment variables for secrets?
3. Why separate agents/ from routes/?

---

## Phase 2: Agent Foundation (2 hours)

### Learning Objectives
- **NEW:** OpenAI Chat Completions API (messages, roles, models)
- **NEW:** Async programming with OpenAI SDK
- **NEW:** System prompts vs user messages
- **NEW:** Token counting and context windows

### Tasks

#### 2.1: Create Base Agent Interface

**File:** `backend/app/agents/base.py`

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseAgent(ABC):
    """
    Base class for all APOLLO agents.
    
    TODO: Why use ABC (Abstract Base Class)?
    - Defines interface contract
    - Ensures all agents have required methods
    - Enables polymorphism (can swap agents)
    """
    
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.system_prompt = self._get_system_prompt()
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """
        Define agent personality and capabilities.
        
        TODO: Research prompt engineering best practices
        - What makes a good system prompt?
        - How specific vs general should it be?
        """
        pass
    
    @abstractmethod
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        user_context: Dict[str, Any]
    ) -> str:
        """
        Generate response to user message.
        
        TODO: What is user_context?
        - Current user's tasks
        - Preferences
        - Conversation history
        """
        pass
```

**Concepts to Learn:**
- **NEW:** Abstract Base Class (ABC) pattern
  - Why use ABC? (interface contracts, type safety, polymorphism)
  - `@abstractmethod` decorator forces subclasses to implement
- **NEW:** Type hints for complex types (`List[Dict[str, str]]`)
- **Review:** Async methods (`async def`)

**Teaching Moment:**
Before implementing, explain:
1. **What is an interface?** (contract without implementation)
2. **Why define base class?** (multiple agents will share patterns)
3. **Alternative:** No base class, just implement each agent independently
   - Pro: Flexibility
   - Con: Code duplication, no type checking

**Interview Answer:** "Used ABC to enforce consistent agent interface across multiple agent types. Enables dependency injection and testing. Trade-off: slight complexity for maintainability."

---

#### 2.2: Implement Life Coordinator Agent

**File:** `backend/app/agents/life_coordinator.py`

```python
from openai import AsyncOpenAI
from .base import BaseAgent
from typing import List, Dict, Any

class LifeCoordinator(BaseAgent):
    """
    Life Coordinator Agent - Strategic planning and task management.
    
    Capabilities:
    - Answer questions about productivity
    - Break down goals into tasks
    - Provide strategic advice
    - Create/modify tasks (via tools - coming in Phase 4)
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(model)
        self.client = AsyncOpenAI(api_key=api_key)
    
    def _get_system_prompt(self) -> str:
        """
        TODO: Craft agent personality
        
        This is CRITICAL - the system prompt defines agent behavior.
        
        Research:
        - How specific should instructions be?
        - What tone/personality for APOLLO?
        - What capabilities to mention?
        """
        return """
        You are the Life Coordinator for APOLLO, an AI life assistant.
        
        Your role:
        - Help users plan their week and prioritize tasks
        - Break down goals into actionable steps
        - Provide strategic productivity advice
        - Be concise but helpful
        
        Personality:
        - Professional but friendly
        - Focus on actionable advice
        - Ask clarifying questions when needed
        
        Remember:
        - User's time is valuable (be concise)
        - Provide specific, actionable guidance
        - Don't just sympathize - solve problems
        """
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        user_context: Dict[str, Any] = None
    ) -> str:
        """
        Generate response using OpenAI Chat Completions.
        
        TODO: Understand the API call structure
        - What are 'messages'? (conversation history)
        - What is 'role'? (system/user/assistant)
        - How does the API use context?
        """
        
        # Build full message list: system prompt + conversation
        full_messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add user context if available
        # TODO: How should we format user_context?
        # Should it be in system prompt or separate message?
        if user_context and user_context.get("tasks"):
            context_msg = self._format_user_context(user_context)
            full_messages.append({
                "role": "system",
                "content": f"User Context:\n{context_msg}"
            })
        
        # Add conversation history
        full_messages.extend(messages)
        
        # Call OpenAI API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            temperature=0.7,  # TODO: What does temperature do?
            max_tokens=500    # TODO: Why limit tokens?
        )
        
        return response.choices[0].message.content
    
    def _format_user_context(self, user_context: Dict[str, Any]) -> str:
        """
        TODO: Format user tasks for agent consumption
        
        Question: How should tasks be presented to the agent?
        - JSON format?
        - Natural language?
        - Structured list?
        
        Think about token efficiency vs clarity.
        """
        tasks = user_context.get("tasks", [])
        if not tasks:
            return "User has no active tasks."
        
        # Simple format for now
        task_list = "\n".join([
            f"- {task['title']} (status: {task['status']})"
            for task in tasks
        ])
        return f"Current Tasks:\n{task_list}"
```

**Concepts to Learn:**

1. **OpenAI Chat Completions API**
   - **Messages structure:** `{"role": "system|user|assistant", "content": "..."}`
   - **System vs User messages:** System sets behavior, User is actual input
   - **Message history:** Each API call includes full conversation (stateless)

2. **Temperature Parameter**
   - Range: 0.0 (deterministic) to 2.0 (very random)
   - Low temp (0.2): Focused, consistent (good for Q&A)
   - High temp (0.9): Creative, varied (good for brainstorming)
   - Default 0.7: Balanced for chat

3. **Token Limits**
   - **max_tokens:** Limit response length (cost control + latency)
   - **Context window:** Total input + output tokens (GPT-4: 8k)
   - **Why limit?** Costs money per token, long responses = slow

4. **Async/Await Pattern**
   - Why `AsyncOpenAI`? (non-blocking I/O, handle multiple requests)
   - `await` keyword: Wait for API call without blocking event loop
   - FastAPI is async-native (can handle concurrent requests)

**Teaching Moment - Context Window Deep Dive:**

```
┌─────────────────────────────────────────┐
│ GPT-4 Context Window: 8,192 tokens      │
├─────────────────────────────────────────┤
│ System Prompt:          ~200 tokens     │
│ User Context (tasks):   ~300 tokens     │
│ Conversation History:   ~2,000 tokens   │
│ Current User Message:   ~50 tokens      │
├─────────────────────────────────────────┤
│ Available for Response: ~5,642 tokens   │
│ (max_tokens=500 reserves budget)        │
└─────────────────────────────────────────┘

What happens if we exceed 8k?
- API truncates oldest messages
- System prompt always included (highest priority)
- OR returns error (depends on model)

Mitigation strategies:
1. **Sliding window:** Keep only last N messages
2. **Summarization:** Compress old messages
3. **Semantic search:** Retrieve only relevant history
```

**Interview Question:** "How do you handle context window limits in a long conversation?"

**Answer:** "Three strategies: sliding window (simple, loses context), summarization (preserves meaning, adds complexity), or semantic search via vector DB (best, requires infrastructure). Chose sliding window for MVP, designed for vector DB upgrade. Token counting critical—track input size before API call."

---

### Phase 2 Checkpoint

**Verify:**
- [ ] `BaseAgent` class created with ABC pattern
- [ ] `LifeCoordinator` inherits from BaseAgent
- [ ] Can instantiate agent: `agent = LifeCoordinator(api_key="...")`
- [ ] System prompt defined

**Understanding Check:**
1. Explain the difference between system and user messages
2. What is temperature and when would you use 0.2 vs 0.9?
3. Why use async with OpenAI SDK?
4. What happens if context exceeds 8k tokens?

**Manual Test (Optional):**
```python
# In Python REPL or Jupyter
import asyncio
from app.agents.life_coordinator import LifeCoordinator

agent = LifeCoordinator(api_key="sk-...")

messages = [{"role": "user", "content": "How should I plan my day?"}]
response = asyncio.run(agent.generate_response(messages))
print(response)
```

---

## Phase 3: Context Management (2 hours)

### Learning Objectives
- **NEW:** Database queries for agent context
- **NEW:** Token counting and budget management
- **NEW:** Formatting data for LLM consumption
- **Review:** SQL joins and aggregations

### Tasks

#### 3.1: Create Context Builder

**File:** `backend/app/agents/context_builder.py`

```python
from supabase import Client
from typing import Dict, List, Any

class ContextBuilder:
    """
    Retrieves and formats user context for agents.
    
    TODO: Think about what context means
    - What data does agent need?
    - How much is too much? (token budget)
    - How to format for clarity?
    """
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    async def build_context(self, user_id: str) -> Dict[str, Any]:
        """
        Build comprehensive user context.
        
        Returns:
        {
            "tasks": [...],
            "stats": {...},
            "preferences": {...}
        }
        """
        
        # TODO: Implement parallel data fetching
        # Why parallel? (faster than sequential)
        # How in Python? (asyncio.gather)
        
        tasks = await self._get_user_tasks(user_id)
        stats = await self._get_user_stats(user_id)
        
        return {
            "tasks": tasks,
            "stats": stats
        }
    
    async def _get_user_tasks(self, user_id: str) -> List[Dict]:
        """
        TODO: Query tasks from database
        
        Question: Which tasks should we include?
        - All tasks? (could be hundreds)
        - Only active/pending? (most relevant)
        - Last N tasks? (recency matters)
        
        Token efficiency vs completeness trade-off
        """
        response = self.supabase.table("tasks")\
            .select("*")\
            .eq("user_id", user_id)\
            .in_("status", ["pending", "in_progress"])\
            .order("created_at", desc=True)\
            .limit(20)\  # TODO: Why 20? Token budget
            .execute()
        
        return response.data
    
    async def _get_user_stats(self, user_id: str) -> Dict:
        """
        TODO: Calculate user statistics
        
        Useful context for agent:
        - Total tasks completed
        - Current pending count
        - Recent activity level
        
        Question: SQL aggregation or Python calculation?
        """
        # Count total tasks
        total_response = self.supabase.table("tasks")\
            .select("*", count="exact")\
            .eq("user_id", user_id)\
            .execute()
        
        # Count pending
        pending_response = self.supabase.table("tasks")\
            .select("*", count="exact")\
            .eq("user_id", user_id)\
            .eq("status", "pending")\
            .execute()
        
        return {
            "total_tasks": total_response.count,
            "pending_tasks": pending_response.count
        }
```

**Concepts to Learn:**

1. **Token Budget Management**
   - **Problem:** Can't send all user data (exceeds context window)
   - **Solution:** Prioritize recent/relevant data
   - **Question:** How to choose limit? (estimate tokens, test)
   - **Formula:** ~1 task = 50-100 tokens → 20 tasks = 1,000-2,000 tokens

2. **Query Optimization**
   - Why `.limit(20)`? (reduce data transfer, token usage)
   - Why `.order("created_at", desc=True)`? (recency matters)
   - Alternative: Pagination (get more if needed)

3. **Parallel Data Fetching**
   ```python
   # Sequential (slow)
   tasks = await get_tasks()       # Wait 100ms
   stats = await get_stats()       # Wait 100ms
   # Total: 200ms
   
   # Parallel (fast)
   tasks, stats = await asyncio.gather(
       get_tasks(),
       get_stats()
   )
   # Total: 100ms (concurrent execution)
   ```

**Teaching Moment:** 
Before implementing, discuss:
- What data does the agent NEED vs NICE-TO-HAVE?
- How to balance completeness with token efficiency?
- Interview question: "How do you prioritize data for ML model input?"

---

#### 3.2: Integrate Context into Agent

**Update:** `backend/app/agents/life_coordinator.py`

```python
# Add context_builder parameter
def __init__(self, api_key: str, context_builder: ContextBuilder, model: str = "gpt-4"):
    super().__init__(model)
    self.client = AsyncOpenAI(api_key=api_key)
    self.context_builder = context_builder

async def generate_response(
    self,
    user_id: str,  # NEW: Need user_id to fetch context
    messages: List[Dict[str, str]]
) -> str:
    # Build user context from database
    user_context = await self.context_builder.build_context(user_id)
    
    # Rest of implementation...
```

**Concepts to Learn:**
- **Dependency Injection:** Pass `context_builder` to agent
  - Why? (testable, flexible, separation of concerns)
  - Alternative: Agent creates its own context builder (tight coupling)

---

### Phase 3 Checkpoint

**Verify:**
- [ ] ContextBuilder retrieves tasks and stats
- [ ] Agent receives user context
- [ ] Context formatted in system message

**Understanding Check:**
1. Why limit tasks to 20? What's the trade-off?
2. Explain token budget management
3. Why use dependency injection for context_builder?

**Manual Test:**
```python
context = await context_builder.build_context(user_id)
print(f"Tasks: {len(context['tasks'])}")
print(f"Tokens (estimate): {len(str(context)) * 0.5}")  # Rough estimate
```

---

## Phase 4: Tool Calling (3 hours)

### Learning Objectives
- **NEW:** OpenAI Function Calling (tool definitions, execution)
- **NEW:** JSON schemas for function parameters
- **NEW:** Agentic workflows (decide → call → incorporate)
- **NEW:** Error handling in agent systems

**This is the most complex phase. Take your time.**

### Conceptual Foundation (15 min before coding)

**What is Function Calling?**

Traditional:
```
User: "Add a task to email the team"
Agent: "Okay, I've added that task" [but actually did nothing]
```

With Function Calling:
```
User: "Add a task to email the team"
Agent decides: I should use create_task()
Agent calls: create_task(title="Email team", description="...")
We execute: Actually creates task in database
Agent responds: "I've added 'Email team' to your tasks"
```

**Flow:**
1. Define functions as "tools" (JSON schema)
2. Agent decides if/when to call
3. Agent returns function call request (not actual execution!)
4. We execute the function
5. Send result back to agent
6. Agent incorporates result in final response

**Key Insight:** Agent doesn't execute functions—it requests them. We maintain control.

---

### Tasks

#### 4.1: Define Task Tools

**File:** `backend/app/agents/tools/task_tools.py`

```python
from typing import Dict, Any, Optional
from supabase import Client

class TaskTools:
    """
    Tool functions for agent to manipulate tasks.
    
    TODO: Why separate class?
    - Testable (can mock Supabase)
    - Reusable across agents
    - Clear responsibility
    """
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    async def create_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        status: str = "pending"
    ) -> Dict[str, Any]:
        """
        Create new task for user.
        
        TODO: Why user_id parameter?
        - Security: Agent can't create tasks for other users
        - Validation: Check user_id matches authenticated user
        """
        
        # Validate input
        if not title or len(title) < 3:
            raise ValueError("Title must be at least 3 characters")
        
        # Create task
        response = self.supabase.table("tasks").insert({
            "user_id": user_id,
            "title": title,
            "description": description,
            "status": status
        }).execute()
        
        if not response.data:
            raise Exception("Failed to create task")
        
        return response.data[0]
    
    async def update_task(
        self,
        user_id: str,
        task_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        TODO: Implement task update
        
        Security consideration: Verify task belongs to user
        """
        # Verify ownership
        task = self.supabase.table("tasks")\
            .select("*")\
            .eq("id", task_id)\
            .eq("user_id", user_id)\
            .execute()
        
        if not task.data:
            raise ValueError("Task not found or access denied")
        
        # Update
        response = self.supabase.table("tasks")\
            .update(updates)\
            .eq("id", task_id)\
            .execute()
        
        return response.data[0]
    
    async def delete_task(self, user_id: str, task_id: str) -> bool:
        """TODO: Implement task deletion with ownership check"""
        pass
```

**Concepts to Learn:**

1. **Security in Tool Functions**
   - **Always** validate user_id (prevent cross-user access)
   - Check ownership before update/delete
   - Treat all input as untrusted (even from agent)

2. **Error Handling**
   - Raise meaningful exceptions
   - Agent can see these and respond appropriately
   - Example: "I couldn't create that task because the title is too short"

**Interview Question:** "How do you secure AI agent tool calls?"

**Answer:** "Three layers: 1) Tool functions validate ownership and permissions, 2) Functions operate on authenticated user context only, 3) Audit log all tool calls for security review. Agent is untrusted actor—functions enforce security."

---

#### 4.2: Define Function Schemas

**Update:** `backend/app/agents/life_coordinator.py`

```python
def _get_function_definitions(self) -> List[Dict]:
    """
    Define tools available to agent.
    
    TODO: Understand JSON schema format
    This tells the agent:
    - What functions exist
    - What parameters they take
    - What each parameter means
    
    Agent uses this to decide what to call and with what arguments.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "create_task",
                "description": "Create a new task for the user. Use this when user asks to add, create, or remember something.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Short task title (e.g., 'Email team', 'Buy groceries')"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional detailed description of the task"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "completed"],
                            "description": "Initial task status. Default: pending"
                        }
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update an existing task. Use when user wants to modify, change, or mark task complete.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "ID of task to update (from user context)"
                        },
                        "updates": {
                            "type": "object",
                            "description": "Fields to update (title, description, status)"
                        }
                    },
                    "required": ["task_id", "updates"]
                }
            }
        }
        # TODO: Add delete_task definition
    ]
```

**Concepts to Learn:**

1. **JSON Schema**
   - Standard way to describe data structures
   - `type`: string, number, object, array
   - `enum`: Limited set of values
   - `required`: Mandatory fields
   - `description`: Helps agent understand when/how to use

2. **Good Function Descriptions**
   - ✅ "Create a new task for the user. Use this when user asks to add, create, or remember something."
   - ❌ "Creates a task" (too vague)
   - **Guideline:** Tell agent WHEN to use the function, not just what it does

**Teaching Moment:**
The description field is CRITICAL for agent decision-making. Compare:

**Vague:**
```json
{
  "name": "create_task",
  "description": "Creates a task"
}
```
Agent confused: When should I use this?

**Clear:**
```json
{
  "name": "create_task",
  "description": "Create a new task when user asks to add, remember, or create something they need to do. Examples: 'Add buy milk to my list', 'Remember to call Mom', 'Create a task for the meeting'"
}
```
Agent knows exactly when to call!

---

#### 4.3: Implement Function Calling Logic

**Update:** `backend/app/agents/life_coordinator.py`

```python
async def generate_response(
    self,
    user_id: str,
    messages: List[Dict[str, str]],
    task_tools: TaskTools  # NEW: Pass tools
) -> Dict[str, Any]:
    """
    Generate response with function calling support.
    
    Returns:
    {
        "response": "I've added that task for you!",
        "tool_calls": [{"tool": "create_task", "result": {...}}]
    }
    """
    
    # Build context
    user_context = await self.context_builder.build_context(user_id)
    
    # Prepare messages
    full_messages = [
        {"role": "system", "content": self.system_prompt},
        {"role": "system", "content": self._format_user_context(user_context)}
    ]
    full_messages.extend(messages)
    
    # Call OpenAI with tools
    response = await self.client.chat.completions.create(
        model=self.model,
        messages=full_messages,
        tools=self._get_function_definitions(),  # NEW: Available tools
        tool_choice="auto",  # Agent decides if/when to call
        temperature=0.7
    )
    
    message = response.choices[0].message
    
    # Check if agent wants to call functions
    if message.tool_calls:
        # TODO: Execute requested tool calls
        tool_results = await self._execute_tool_calls(
            message.tool_calls,
            user_id,
            task_tools
        )
        
        # TODO: Send results back to agent for final response
        final_response = await self._get_final_response(
            full_messages,
            message,
            tool_results
        )
        
        return {
            "response": final_response,
            "tool_calls": tool_results
        }
    
    # No tool calls needed
    return {
        "response": message.content,
        "tool_calls": []
    }

async def _execute_tool_calls(
    self,
    tool_calls: List,
    user_id: str,
    task_tools: TaskTools
) -> List[Dict]:
    """
    Execute agent's requested tool calls.
    
    TODO: Understand the flow
    1. Agent says: "I want to call create_task(...)"
    2. We parse the request
    3. We execute the actual function
    4. We return result to agent
    
    CRITICAL: We control execution, not the agent
    """
    results = []
    
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        try:
            # Route to appropriate tool function
            if function_name == "create_task":
                result = await task_tools.create_task(
                    user_id=user_id,
                    **function_args
                )
                results.append({
                    "tool": function_name,
                    "status": "success",
                    "result": result
                })
            elif function_name == "update_task":
                result = await task_tools.update_task(
                    user_id=user_id,
                    **function_args
                )
                results.append({
                    "tool": function_name,
                    "status": "success",
                    "result": result
                })
            else:
                # Unknown function
                results.append({
                    "tool": function_name,
                    "status": "error",
                    "error": f"Unknown function: {function_name}"
                })
        
        except Exception as e:
            # Tool execution failed
            results.append({
                "tool": function_name,
                "status": "error",
                "error": str(e)
            })
    
    return results

async def _get_final_response(
    self,
    original_messages: List[Dict],
    agent_message: Any,
    tool_results: List[Dict]
) -> str:
    """
    TODO: Multi-step conversation
    
    After executing tools, agent needs to incorporate results into response.
    
    Flow:
    1. User: "Add task to buy milk"
    2. Agent: [calls create_task]
    3. We: [execute, return {"id": "123", "title": "Buy milk"}]
    4. Agent: [sees result, generates] "I've added 'Buy milk' to your tasks!"
    """
    
    # Add agent's tool call message
    messages = original_messages + [agent_message]
    
    # Add tool results
    for tool_result in tool_results:
        messages.append({
            "role": "function",
            "name": tool_result["tool"],
            "content": json.dumps(tool_result["result"])
        })
    
    # Get final response from agent
    final_response = await self.client.chat.completions.create(
        model=self.model,
        messages=messages,
        temperature=0.7
    )
    
    return final_response.choices[0].message.content
```

**Concepts to Learn:**

1. **Multi-Turn Agent Conversation**
   ```
   Turn 1: User → Agent
   Agent: "I need to call create_task"
   
   Turn 2: System → Agent (with tool results)
   Agent: "Okay, I created the task. Here's my response to user..."
   ```

2. **Error Handling in Agentic Systems**
   - Tool execution might fail (database error, validation)
   - Agent should handle gracefully
   - Return error to agent, let it explain to user
   - Example: Agent sees "Task title too short" → "I couldn't create that task because the title needs to be longer. Could you provide more detail?"

3. **The `tool_choice` Parameter**
   - `"auto"`: Agent decides (recommended)
   - `"none"`: Disable function calling
   - `{"type": "function", "function": {"name": "..."}}`: Force specific function
   - When to force? (rare - when you KNOW agent should call something)

**Teaching Moment - Agentic Workflow:**

```
┌──────────────────────────────────────────┐
│ User: "Add buy milk to my tasks"         │
└────────────┬─────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│ Agent (GPT-4):                                  │
│ - Analyzes: User wants to create task          │
│ - Decides: I should call create_task()         │
│ - Returns: Function call request               │
│   {                                             │
│     "name": "create_task",                      │
│     "arguments": {"title": "Buy milk"}          │
│   }                                             │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│ Our Code:                                       │
│ - Parses function call                          │
│ - Validates user_id                             │
│ - Executes: task_tools.create_task(...)        │
│ - Returns: {"id": "123", "title": "Buy milk"}  │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────┐
│ Agent (GPT-4) - Second Call:                    │
│ - Sees: Function succeeded, task created        │
│ - Generates: "I've added 'Buy milk' to your     │
│   tasks! You now have 3 pending tasks."         │
└──────────────────────────────────────────────────┘
             │
             ▼
┌───────────────────────────────────────────┐
│ User sees: Final response                 │
└───────────────────────────────────────────┘

Key: Agent REQUESTS, we EXECUTE, agent RESPONDS
```

**Interview Question:** "Explain the function calling flow in OpenAI's API."

**Answer:** "Three-step process: 1) Agent receives function definitions as tools, decides if/when to call based on user message, 2) Agent returns function call request (JSON), doesn't execute, 3) We parse, validate, execute, and return results to agent for final response. Agent autonomy with execution control—critical for security and reliability."

---

### Phase 4 Checkpoint

**Verify:**
- [ ] TaskTools class created with create/update/delete
- [ ] Function schemas defined with clear descriptions
- [ ] Agent can request tool calls
- [ ] Tool execution works and returns results
- [ ] Agent incorporates results in final response

**Understanding Check (CRITICAL):**
1. Explain the function calling flow (3 steps)
2. Why does the agent not execute functions directly?
3. What's the role of function descriptions in JSON schema?
4. How do you secure tool functions?
5. What happens if a tool execution fails?

**Manual Test:**
```python
# Test flow end-to-end
messages = [{"role": "user", "content": "Add a task to call Mom tomorrow"}]
response = await agent.generate_response(user_id, messages, task_tools)

print(response["response"])  # Should mention task created
print(response["tool_calls"])  # Should show create_task called

# Verify task in database
tasks = supabase.table("tasks").select("*").eq("user_id", user_id).execute()
assert any("call Mom" in task["title"] for task in tasks.data)
```

---

## Phase 5: Streaming & Frontend (3 hours)

### Learning Objectives
- **NEW:** Server-Sent Events (SSE) for streaming
- **NEW:** FastAPI `StreamingResponse`
- **NEW:** Async generators in Python
- **NEW:** Frontend streaming (EventSource or fetch)
- **Review:** React state management for real-time updates

**This phase connects backend to frontend with real-time updates.**

---

### Part A: Backend Streaming (1.5 hours)

#### 5.1: Create Chat API Endpoint

**File:** `backend/app/routes/chat.py`

```python
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.auth.dependencies import get_current_user
from app.models.user import User
from typing import AsyncGenerator
import json

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/message")
async def send_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send message to agent, receive streaming response.
    
    TODO: What is streaming?
    - Response sent in chunks (not all at once)
    - User sees response appear word-by-word (like ChatGPT)
    - Better UX (lower perceived latency)
    
    Technical: Server-Sent Events (SSE)
    - text/event-stream MIME type
    - event: [type] / data: [content] format
    - Frontend uses EventSource API
    """
    
    async def generate_stream() -> AsyncGenerator[str, None]:
        """
        TODO: Understand async generators
        
        What is yield?
        - Like return, but doesn't exit function
        - Produces one value, pauses, resumes
        - Enables streaming (produce data incrementally)
        
        Why async?
        - Await OpenAI API chunks
        - Non-blocking (handle multiple requests)
        """
        
        # Initialize agent
        agent = LifeCoordinator(...)
        
        # Stream agent response
        async for chunk in agent.generate_response_stream(
            user_id=current_user.id,
            message=request.message
        ):
            # Format as SSE
            event_data = {
                "type": "message",
                "content": chunk
            }
            yield f"data: {json.dumps(event_data)}\n\n"
        
        # Send completion event
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )
```

**Concepts to Learn:**

1. **Server-Sent Events (SSE)**
   - Protocol for server → client streaming
   - Format: `data: {json}\n\n` (two newlines important!)
   - Frontend connects with `EventSource` or `fetch`
   - Alternative: WebSockets (bidirectional, more complex)

2. **Async Generators (`async def` + `yield`)**
   ```python
   async def count_to_five():
       for i in range(5):
           await asyncio.sleep(1)  # Simulate async work
           yield i
   
   # Usage
   async for num in count_to_five():
       print(num)  # Prints 0, 1, 2, 3, 4 (one per second)
   ```

3. **FastAPI StreamingResponse**
   - Accepts async generator
   - Sends chunks as they're produced
   - Keeps connection open until generator exhausted
   - `media_type="text/event-stream"` tells browser it's SSE

**Teaching Moment - Why Streaming?**

```
Without Streaming:
┌───────────────────────────────────────┐
│ User sends message                    │
└─────────┬─────────────────────────────┘
          │ Wait... wait... wait...
          │ (15 seconds)
          ▼
┌───────────────────────────────────────┐
│ Full response appears                 │
└───────────────────────────────────────┘

User experience: "Is it broken?"


With Streaming:
┌───────────────────────────────────────┐
│ User sends message                    │
└─────────┬─────────────────────────────┘
          │ 1 second
          ▼
┌───────────────────────────────────────┐
│ "Let"                                 │
└─────────┬─────────────────────────────┘
          │ 0.5 seconds
          ▼
┌───────────────────────────────────────┐
│ "Let me"                              │
└─────────┬─────────────────────────────┘
          │ 0.5 seconds
          ▼
┌───────────────────────────────────────┐
│ "Let me help"                         │
└───────────────────────────────────────┘

User experience: "It's responding!" (feels faster)
```

**Interview Question:** "Why use streaming for LLM responses?"

**Answer:** "Three benefits: 1) Lower perceived latency—user sees output immediately, 2) Better UX for long responses—progressively rendered vs stare at loading, 3) Enables interruptibility—user can cancel mid-stream. Trade-off: implementation complexity, but essential for production AI chat."

---

#### 5.2: Add Streaming to Agent

**Update:** `backend/app/agents/life_coordinator.py`

```python
async def generate_response_stream(
    self,
    user_id: str,
    messages: List[Dict[str, str]],
    task_tools: TaskTools
) -> AsyncGenerator[str, None]:
    """
    Generate streaming response.
    
    TODO: How does OpenAI streaming work?
    - API returns chunks instead of full response
    - Each chunk has delta (incremental content)
    - We yield each delta to FastAPI
    - FastAPI sends to frontend
    """
    
    # Build context (same as before)
    user_context = await self.context_builder.build_context(user_id)
    full_messages = [...]  # Same setup
    
    # Call OpenAI with stream=True
    response = await self.client.chat.completions.create(
        model=self.model,
        messages=full_messages,
        tools=self._get_function_definitions(),
        stream=True,  # Enable streaming
        temperature=0.7
    )
    
    # Collect tool calls (if any)
    tool_calls = []
    
    # Stream response
    async for chunk in response:
        delta = chunk.choices[0].delta
        
        # Check for content
        if delta.content:
            yield delta.content
        
        # Check for tool calls
        # TODO: Handle streaming tool calls
        # This is complex - tool calls come in chunks too!
        if delta.tool_calls:
            # Collect tool call chunks...
            pass
    
    # If tool calls collected, execute and continue
    # TODO: Implement tool execution in streaming context
```

**Concepts to Learn:**

1. **OpenAI Streaming Format**
   ```python
   # Non-streaming
   response = await client.chat.completions.create(...)
   content = response.choices[0].message.content
   
   # Streaming
   response = await client.chat.completions.create(..., stream=True)
   async for chunk in response:
       delta = chunk.choices[0].delta  # Incremental content
       if delta.content:
           print(delta.content, end="")  # "Let" -> " me" -> " help"
   ```

2. **Streaming with Tool Calls (COMPLEX)**
   - Tool calls also arrive in chunks
   - Need to buffer until complete
   - Execute tools, then continue streaming
   - This is tricky—start without tools, add later if time

**Teaching Moment:**
Tool calls in streaming are advanced. For MVP:
- Option A: Disable streaming if tool calls needed (fallback to regular)
- Option B: Implement tool call buffering (complex but complete)

Choose Option A for learning—understand streaming first, add complexity later.

---

### Part B: Frontend Streaming (1.5 hours)

#### 5.3: Create Chat Interface

**File:** `frontend/app/chat/page.tsx`

```typescript
'use client';

import { useState, useRef, useEffect } from 'react';

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  
  async function sendMessage(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    
    // Add user message
    const userMessage: Message = {
      role: 'user',
      content: input
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);
    
    // TODO: Implement streaming fetch
    // What is fetch with ReadableStream?
    // Alternative: EventSource API
    
    try {
      const response = await fetch('http://localhost:8000/chat/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({ message: input })
      });
      
      // Read stream
      // TODO: How to handle ReadableStream?
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      let assistantMessage: Message = {
        role: 'assistant',
        content: ''
      };
      
      // Add empty message, will update with chunks
      setMessages(prev => [...prev, assistantMessage]);
      
      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            
            if (data.type === 'message') {
              // Update message content
              assistantMessage.content += data.content;
              setMessages(prev => [
                ...prev.slice(0, -1),
                { ...assistantMessage }
              ]);
            } else if (data.type === 'done') {
              setIsStreaming(false);
            }
          }
        }
      }
    } catch (error) {
      console.error('Streaming error:', error);
      setIsStreaming(false);
    }
  }
  
  return (
    <div className="flex flex-col h-screen">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((msg, i) => (
          <div key={i} className={`mb-4 ${msg.role === 'user' ? 'text-right' : ''}`}>
            <div className={`inline-block p-3 rounded ${
              msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {isStreaming && <div className="text-gray-500">...</div>}
      </div>
      
      <form onSubmit={sendMessage} className="p-4 border-t">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isStreaming}
          placeholder="Ask APOLLO..."
          className="w-full p-2 border rounded"
        />
      </form>
    </div>
  );
}
```

**Concepts to Learn:**

1. **ReadableStream in Browser**
   ```javascript
   const response = await fetch('/api/stream');
   const reader = response.body.getReader();
   const decoder = new TextDecoder();
   
   while (true) {
     const { done, value } = await reader.read();
     if (done) break;
     
     const text = decoder.decode(value);
     console.log(text);  // Process chunk
   }
   ```

2. **React State Updates for Streaming**
   - Create message with empty content
   - Append chunks as they arrive
   - Replace message in state array

3. **Parsing SSE Format**
   - Lines like `data: {"type": "message"}\n\n`
   - Split by `\n`, filter lines starting with `data:`
   - Parse JSON from each line

**Teaching Moment:**
Streaming in React is tricky because state updates are async. Pattern:
```typescript
// ❌ Wrong: content will be empty
assistantMessage.content += chunk;
setMessages([...messages, assistantMessage]);

// ✅ Right: use functional update
setMessages(prev => [
  ...prev.slice(0, -1),  // All except last
  { ...prev[prev.length - 1], content: prev[prev.length - 1].content + chunk }
]);
```

---

### Phase 5 Checkpoint

**Verify:**
- [ ] Backend sends SSE format correctly
- [ ] Frontend receives and parses stream
- [ ] Message appears word-by-word in UI
- [ ] Streaming feels responsive

**Understanding Check:**
1. Explain Server-Sent Events vs WebSockets
2. What is an async generator and why use it?
3. How do you handle ReadableStream in browser?
4. Why is functional state update needed for streaming?

**Manual Test:**
- Send message "Help me plan my day"
- Watch response stream in real-time
- Verify no jarring UI updates

---

## Phase 6: Testing & Polish (1 hour)

### Final Integration Tests

1. **Full conversation flow**
   - User sends message
   - Agent responds with streaming
   - Agent calls tools when needed
   - Tasks created in database
   - UI updates correctly

2. **Error scenarios**
   - OpenAI API timeout
   - Invalid tool call
   - Network interruption
   - User not authenticated

3. **Edge cases**
   - Very long messages
   - Rapid successive messages
   - Empty input
   - Special characters

---

## Module 2 Complete! 🎉

### What You Built
- ✅ OpenAI agent integration with tool calling
- ✅ Context-aware responses using user data
- ✅ Streaming chat interface
- ✅ Tool execution (create/update/delete tasks)
- ✅ Full-stack real-time communication

### What You Learned
- **AI/ML:** OpenAI Chat Completions, function calling, prompt engineering
- **System Design:** Agent architecture, context management, streaming
- **Backend:** FastAPI streaming, async generators, SSE
- **Frontend:** React streaming, ReadableStream API
- **Security:** Tool validation, user isolation, error handling

### Interview Readiness
You can now explain:
- Multi-agent system architecture
- Context window management strategies
- Function calling flow and security
- Streaming implementation (backend + frontend)
- Trade-offs in agent design

---

## Next Steps (Module 3)

**Module 3 Preview: Multi-Agent Orchestration**
- Task Manager Agent (specialized for task breakdown)
- Deep Work Analyzer Agent (productivity insights)
- Agent coordination and delegation
- Conversation routing (which agent handles query?)

**But first:** Commit Module 2, update professional docs, rest!

---

**Last Updated:** 2025-10-24  
**Estimated Completion:** Nov 15, 2025  
**Status:** Ready for Implementation
