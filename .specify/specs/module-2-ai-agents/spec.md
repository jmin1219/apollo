# Module 2: AI Agent Foundation - TECHSPEC

**Module:** 2.1 - AI Agent Foundation  
**Timeline:** 2 weeks (Nov 2-15, 2025)  
**Status:** 🟡 Planning Complete  
**Dependencies:** Module 1 Complete (Backend + Frontend + Auth)

---

## Executive Summary

Transform APOLLO from a task management system into an AI-powered life assistant by integrating OpenAI Agents SDK. This module establishes the foundation for multi-agent orchestration, enabling natural language interaction with task planning, strategic advice, and context-aware responses.

**Key Achievement:** User can have a conversation with APOLLO that understands their tasks, goals, and preferences to provide intelligent recommendations.

---

## Problem Statement

**Current State (Module 1):**
- Users manually create/update tasks through UI forms
- No intelligence or recommendations
- Static system with no adaptability
- No conversation or natural language interface

**Target State (Module 2):**
- Users converse with AI agent in natural language
- Agent understands user context (tasks, history, preferences)
- Agent provides strategic advice and task breakdowns
- Agent creates/modifies tasks on user's behalf
- Foundation for future multi-agent expansion (Task Manager, Deep Work Analyzer)

**Business Value:**
- Differentiates APOLLO from basic task apps
- Demonstrates AI agent architecture (portfolio value)
- Enables personalized productivity coaching
- Prepares for vision: "autonomous productivity orchestrator"

---

## System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────┐
│  Frontend (Next.js)                             │
│  ┌─────────────────────────────────────────┐   │
│  │  Chat Interface                         │   │
│  │  - Message history                      │   │
│  │  - Streaming responses                  │   │
│  │  - Action confirmations                 │   │
│  └─────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────┘
                  │ REST API
                  ▼
┌─────────────────────────────────────────────────┐
│  Backend API (FastAPI)                          │
│  ┌─────────────────────────────────────────┐   │
│  │  /chat/message                          │   │
│  │  - Receives user message                │   │
│  │  - Builds agent context                 │   │
│  │  - Calls agent orchestrator             │   │
│  │  - Streams response                     │   │
│  └─────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  Agent Orchestrator                             │
│  ┌─────────────────────────────────────────┐   │
│  │  Life Coordinator Agent                 │   │
│  │  - Natural language understanding       │   │
│  │  - Context management                   │   │
│  │  - Tool calling (task CRUD)             │   │
│  │  - Response generation                  │   │
│  └─────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  Database (PostgreSQL)                          │
│  - Users, Tasks (existing)                      │
│  - + Conversations                              │
│  - + Messages                                   │
│  - + Agent Actions                              │
└─────────────────────────────────────────────────┘
```

### Component Responsibilities

**Agent Orchestrator (`/backend/app/agents/`)**
- **Purpose:** Manages AI agent lifecycle and tool integration
- **Input:** User message + context (user_id, conversation_id)
- **Output:** Streaming agent response + executed actions
- **Key Functions:**
  - Build context from database (user tasks, preferences, history)
  - Call OpenAI Agents SDK with tools
  - Handle streaming responses
  - Execute tool calls (create/update tasks)
  - Store conversation history

**Life Coordinator Agent (`/backend/app/agents/life_coordinator.py`)**
- **Purpose:** First agent implementation - strategic planning and task management
- **Capabilities:**
  - Answer questions about tasks and productivity
  - Break down goals into actionable tasks
  - Provide strategic advice on prioritization
  - Create/update/delete tasks via tool calls
- **Tools Available:**
  - `get_user_tasks()` - Retrieve current task list
  - `create_task(title, description)` - Add new task
  - `update_task(id, updates)` - Modify existing task
  - `delete_task(id)` - Remove task
  - `get_user_context()` - Fetch user preferences and history

**Chat API (`/backend/app/routes/chat.py`)**
- **Purpose:** REST endpoint for frontend chat interface
- **Endpoints:**
  - `POST /chat/message` - Send message, get streaming response
  - `GET /chat/conversations` - List user conversations
  - `GET /chat/conversations/{id}/messages` - Get message history
- **Authentication:** JWT-protected, user-isolated

**Chat Interface (`/frontend/app/chat/`)**
- **Purpose:** User-facing conversational UI
- **Features:**
  - Message input with real-time streaming
  - Conversation history display
  - Action confirmations (when agent creates tasks)
  - Loading states and error handling

---

## Technical Decisions

### Decision 1: OpenAI Agents SDK vs Raw API

**Choice:** OpenAI Agents SDK

**Rationale:**
- Built-in tool calling and function management
- Streaming support out of box
- Agent state management included
- Better error handling and retries
- Production-ready patterns
- Learning opportunity: SDK design patterns

**Trade-offs:**
- Vendor lock-in (OpenAI specific)
- Less control over low-level details
- But: Faster development, fewer bugs, better maintainability

**Interview Answer:** "Used SDK for rapid prototyping and production patterns. Can explain raw API underneath. For MVP, SDK's reliability > flexibility. Would abstract with provider interface if multi-model needed."

---

### Decision 2: Streaming vs Request-Response

**Choice:** Streaming responses (Server-Sent Events)

**Rationale:**
- Better UX (see response in real-time like ChatGPT)
- Lower perceived latency
- Shows agent "thinking"
- Industry standard for AI chat interfaces
- Educational value: implementing streaming in FastAPI

**Trade-offs:**
- More complex implementation
- Harder to debug
- But: Essential for production AI apps

**Implementation:**
- FastAPI `StreamingResponse` with async generator
- Frontend `EventSource` or fetch with `ReadableStream`

**Interview Answer:** "Streaming crucial for LLM UX. Implemented with async generators in Python, handles backpressure naturally. Alternative: polling expensive and wasteful."

---

### Decision 3: Context Management Strategy

**Choice:** Database retrieval + window management (not vector DB... yet)

**Rationale:**
- Current data scale: small (one user's tasks)
- Database query sufficient for context building
- Vector DB overkill for MVP
- Can add later if needed (embeddings + semantic search)

**Context Window Strategy:**
- Include: Last 10 messages + current user tasks + user preferences
- Estimated tokens: ~2k tokens (well under 8k GPT-4 limit)
- If exceeds: Truncate old messages, keep system prompt + recent context

**Interview Answer:** "Chose simple context retrieval for MVP. Explained token economics. Aware of compression strategies (summarization, sliding window, vector DB). Designed system to add complexity when data justifies it."

---

### Decision 4: Tool Calling Architecture

**Choice:** Register functions as tools, let agent decide when to call

**How it works:**
1. Define Python functions (e.g., `create_task()`)
2. Register with OpenAI SDK using function schemas
3. Agent decides if/when to call based on user message
4. We execute function, return result to agent
5. Agent incorporates result in response

**Example:**
```python
# User: "Add a task to email the team tomorrow"
# Agent thinking: I need create_task tool
# Agent calls: create_task(title="Email team", description="Send update", due_date="2025-11-03")
# We execute: Task created in database
# Agent responds: "I've added 'Email team' to your tasks for tomorrow"
```

**Interview Answer:** "Function calling pattern: declarative tool definition, agent autonomy in tool selection, execution sandboxing. Trade-off: Agent might call unexpected tools (need guardrails). Alternative: Intent classification + deterministic flows (less flexible)."

---

### Decision 5: Conversation Storage

**Choice:** Store all conversations and messages in database

**Schema:**
```sql
conversations:
  - id (UUID)
  - user_id (FK to users)
  - title (generated from first message)
  - created_at, updated_at

messages:
  - id (UUID)
  - conversation_id (FK to conversations)
  - role (user/assistant/system)
  - content (TEXT)
  - tool_calls (JSONB) -- if agent called tools
  - created_at
```

**Rationale:**
- Enables conversation history and context
- Audit trail (what did agent do?)
- Analytics (user patterns, agent effectiveness)
- Future: Fine-tuning data, evaluation

**Interview Answer:** "Stored conversations for context continuity, not just agent memory. JSONB for flexible tool call storage. Considered: Redis for hot data, but PSQL sufficient for MVP scale. Foreign keys ensure data integrity."

---

## Data Model Changes

### New Tables

**conversations**
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
```

**messages**
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
```

---

## API Specification

### POST /chat/message

**Purpose:** Send user message, receive streaming agent response

**Request:**
```json
{
  "conversation_id": "uuid | null",  // null = new conversation
  "message": "Help me plan my week"
}
```

**Response:** `text/event-stream` (Server-Sent Events)
```
event: message
data: {"chunk": "Let", "delta": true}

event: message
data: {"chunk": " me", "delta": true}

event: tool_call
data: {"tool": "get_user_tasks", "status": "calling"}

event: tool_call
data: {"tool": "get_user_tasks", "status": "complete", "result": {...}}

event: message
data: {"chunk": " help", "delta": true}

event: done
data: {"conversation_id": "uuid", "message_id": "uuid"}
```

**Authentication:** JWT required

---

### GET /chat/conversations

**Purpose:** List user's conversations

**Response:**
```json
[
  {
    "id": "uuid",
    "title": "Weekly planning discussion",
    "last_message": "Sure, let's break that down...",
    "updated_at": "2025-11-02T14:30:00Z",
    "message_count": 15
  }
]
```

---

### GET /chat/conversations/{id}/messages

**Purpose:** Retrieve full conversation history

**Response:**
```json
{
  "conversation_id": "uuid",
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "Help me plan my week",
      "created_at": "2025-11-02T14:25:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "I'd be happy to help...",
      "tool_calls": [
        {"tool": "get_user_tasks", "result": {...}}
      ],
      "created_at": "2025-11-02T14:25:15Z"
    }
  ]
}
```

---

## Security Considerations

1. **User Isolation:**
   - All database queries filtered by `user_id`
   - Agent cannot access other users' tasks/conversations
   - JWT authentication on all endpoints

2. **Tool Call Validation:**
   - Agent can only call registered tools
   - Functions validate input (task_id belongs to user)
   - No arbitrary code execution

3. **Rate Limiting (Future):**
   - Limit messages per user per hour
   - Prevent OpenAI API abuse
   - Track token usage per user

4. **Content Filtering:**
   - OpenAI's moderation API (future enhancement)
   - Log inappropriate requests
   - User safety

---

## Testing Strategy

**Unit Tests:**
- Agent context building (correct data retrieved)
- Tool function execution (task CRUD operations)
- Message storage (correct format, relationships)

**Integration Tests:**
- Full conversation flow (user message → agent response → task created)
- Streaming response handling
- Error scenarios (OpenAI API down, invalid tool calls)

**Manual Testing:**
- Conversation quality (does agent give good advice?)
- Tool calling accuracy (agent creates correct tasks)
- UX testing (streaming feels responsive)

---

## Success Criteria

**Functional:**
- ✅ User can send message to agent
- ✅ Agent responds with helpful, contextual advice
- ✅ Agent can create/update/delete tasks when needed
- ✅ Conversation history persists across sessions
- ✅ Streaming responses work in frontend

**Technical:**
- ✅ <2s first token latency
- ✅ Correct tool calls (agent understands when to use tools)
- ✅ No data leakage between users
- ✅ Error handling for API failures

**Learning:**
- ✅ Understand OpenAI Agents SDK architecture
- ✅ Can explain context window management
- ✅ Can implement streaming in FastAPI
- ✅ Can design tool calling patterns
- ✅ Interview-ready on agent systems

---

## Future Enhancements (Module 3+)

**Multi-Agent System:**
- Task Manager Agent (specialized for task breakdown)
- Deep Work Analyzer Agent (productivity insights)
- Agent coordination and delegation

**Advanced Features:**
- Long-term memory (vector DB for semantic search)
- Scheduled agent actions (proactive reminders)
- Integration with external tools (calendar, email)
- Fine-tuned models (APOLLO-specific training)

**Infrastructure:**
- Caching (Redis for hot conversations)
- Monitoring (agent performance metrics)
- A/B testing (different prompts/models)

---

## Technical Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenAI API rate limits | Can't serve users | Implement request queuing, caching |
| Context window exceeded | Poor responses | Token counting, compression |
| Agent hallucinates | Creates wrong tasks | Human-in-loop confirmations (future) |
| High API costs | Budget issues | Track token usage, optimize prompts |
| Streaming connection drops | Poor UX | Reconnection logic, fallback |

---

**Last Updated:** 2025-10-24  
**Author:** Jaymin Chang  
**Review Status:** Ready for Implementation
