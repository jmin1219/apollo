# APOLLO

**Autonomous Productivity & Optimization Life Logic Orchestrator**

A production-grade AI agent system for strategic productivity and life planning. Built as a full-stack portfolio capstone demonstrating AI architecture, secure tool execution, and streaming interfaces.

> *Renamed from ATLAS to APOLLO (Oct 2025) to differentiate from OpenAI's Atlas browser*

---

## 🎯 What Makes This Different

Most productivity apps are glorified to-do lists. APOLLO is an **AI system that thinks strategically** about your goals:

```
You: "What should I focus on today?"

APOLLO: "Based on your current tasks and goals, I recommend:

1. Complete Module 2.1 Phase 3 (~2 hours). This advances your APOLLO 
   portfolio milestone, which builds toward your Spring 2027 SWE goal.

2. After that, tackle NeetCode: Valid Anagram (~30 min). This reinforces 
   your CS fundamentals and prepares you for technical interviews.

3. Zone 2 cardio session (30 min). This maintains your concurrent training 
   goal for an antifragile body.

Remember, completing Module 2.1 Phase 3 is crucial - it's your highest-
leverage task connecting to your primary goal."
```

**Not just advice** - APOLLO can execute:
```
You: "Add a task to review Module 2.1 notes"
APOLLO: [creates task in database] "I've added 'Review Module 2.1 notes' 
        to your list. Given your current schedule, I suggest fitting this 
        in after your NeetCode session around 7 PM."
```

---

## ✨ Features

### 🤖 AI Agent with Strategic Intelligence
- **LifeCoordinator Agent** - Multi-horizon planning across day/week/month/year
- **Goal Hierarchy Thinking** - Tasks → Projects → Milestones → Goals
- **Context-Aware** - Knows your actual tasks, progress, and constraints
- **95% Confidence Rule** - Asks clarifying questions when uncertain

### ⚡ Secure Function Calling
- **Natural Language Actions** - Create, update, delete tasks via conversation
- **Security-First Design** - Agent requests, system validates and executes
- **Ownership Verification** - user_id injection prevents cross-user access
- **Field Whitelisting** - Agent can't modify unauthorized fields

### 🌊 Streaming Responses
- **Server-Sent Events (SSE)** - Word-by-word display like ChatGPT
- **Hybrid Execution Mode** - Streams conversation, instant actions
- **Smart Routing** - Keyword detection routes to appropriate mode
- **Production UX** - Feels responsive and alive

### 🔐 Enterprise-Grade Auth
- **JWT Authentication** - OAuth2 bearer tokens
- **bcrypt Password Hashing** - Industry-standard security
- **Protected Routes** - All task endpoints require authentication
- **User Isolation** - Can only access your own data

### 📊 Full CRUD Task Management
- Create, Read, Update, Delete tasks via REST API
- Status tracking (pending, in_progress, completed)
- Flexible filtering (by user, by status)
- Partial updates (PATCH semantics)

---

## 🏗️ Architecture

### Backend (FastAPI + Python)

```
backend/app/
├── agents/                      # AI Agent system
│   ├── base.py                  # BaseAgent ABC interface
│   ├── life_coordinator.py      # Strategic planning agent
│   ├── context.py               # Context management & token budgeting
│   ├── token_utils.py           # LRU-cached token counting (99% faster)
│   ├── tools/
│   │   └── task_tools.py        # CRUD operations with security
│   └── tests/                   # Agent test suite
├── auth/                        # JWT authentication
│   ├── dependencies.py          # OAuth2PasswordBearer, get_current_user
│   └── jwt.py                   # Token creation/verification
├── db/                          # Database layer
│   └── supabase_client.py       # Supabase connection
├── models/                      # Pydantic data models
│   ├── user.py                  # User, UserCreate, UserResponse
│   └── task.py                  # Task, TaskCreate, TaskUpdate
├── routes/                      # API endpoints
│   ├── auth.py                  # /auth/* endpoints
│   ├── tasks.py                 # /tasks/* endpoints
│   └── chat.py                  # /chat/* endpoints (Phase 5)
└── main.py                      # FastAPI application
```

### Frontend (Next.js 15 + React)

```
frontend/app/
├── login/                       # Login page
├── register/                    # Registration page
├── dashboard/                   # Protected dashboard
├── chat/                        # AI chat interface (Phase 5)
└── layout.tsx                   # Root layout

frontend/lib/
├── api.ts                       # Type-safe API wrapper
└── auth.ts                      # Auth utilities (login, logout, getCurrentUser)
```

### Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  User: "Add task to buy milk"                               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  LifeCoordinator Agent (GPT-4)                              │
│  - Analyzes: User wants to create task                      │
│  - Decides: Should call create_task()                       │
│  - Returns: Function call request                           │
│    {"name": "create_task", "arguments": {"title": "..."}}   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  TaskTools (Secure Execution Layer)                         │
│  - Validates: user_id from auth (not from agent!)           │
│  - Checks: Input validation, ownership                      │
│  - Executes: Actual database INSERT                         │
│  - Returns: {"id": "...", "title": "Buy milk"}              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Agent (2nd API Call)                                       │
│  - Receives: Function execution result                      │
│  - Generates: "I've added 'Buy milk' to your tasks!         │
│    You now have 5 pending tasks. Consider prioritizing      │
│    Module 2.1 as it advances your Spring 2027 goal."        │
└─────────────────────────────────────────────────────────────┘
```

**Key Insight:** Agent requests actions but doesn't execute them. System maintains control.

---

## 🔒 Security Model

### Authentication Flow
1. User registers → Password hashed with bcrypt → Stored in database
2. User logs in → Credentials verified → JWT token issued (24h expiry)
3. Protected requests → JWT validated → User identity extracted
4. All task operations → Filtered by authenticated user_id

### Agent Security
1. **Agent is untrusted** - Treats AI as external actor
2. **System validates everything** - Ownership checks, input validation
3. **user_id injection** - Agent can't specify user_id (we inject from auth)
4. **Field whitelisting** - Agent can only modify approved fields
5. **Audit capability** - All tool calls logged (future: audit table)

---

## 📈 Performance Optimizations

### Token Counting with LRU Cache
```python
@lru_cache(maxsize=10)
def _get_encoding_cached(model: str):
    # First call: 100ms (loads tokenizer)
    # Cached calls: 0.1ms (99% faster!)
```

### Context Window Management
- **Budget:** GPT-4 has 8,192 token context window
- **Strategy:** Fetch only 20 most recent tasks (~800 tokens)
- **Prioritization:** Recent > old, active > completed
- **Future:** Semantic search for relevant context

### Database Queries
- **Indexed columns:** user_id, status, created_at
- **Limit results:** Default 20 tasks (token budget)
- **Filter at DB:** `.eq("user_id", user_id)` not Python filtering

---

## 🎓 Learning Outcomes

This project demonstrates mastery of:

**Backend Development:**
- RESTful API design (FastAPI)
- Database modeling (PostgreSQL, foreign keys, indexes)
- Authentication patterns (JWT, OAuth2, bcrypt)
- Async programming (Python asyncio)
- Input validation (Pydantic V2)

**AI/ML Engineering:**
- OpenAI Chat Completions API
- Function calling (tool definition, execution, security)
- Context management (token budgeting, data prioritization)
- System prompt engineering (behavior design)
- Multi-turn conversations (state management)

**Frontend Development:**
- Next.js 15 App Router
- React hooks (useState, useEffect, useRef)
- TypeScript (generic types, interfaces)
- API integration (fetch, JWT handling)
- Component architecture (shadcn/ui)

**System Design:**
- Abstract Base Class pattern (polymorphism)
- Separation of concerns (agents, tools, routes)
- Security-first architecture (untrusted actors)
- Performance optimization (caching, token budgeting)

**Interview-Ready Topics:**
- "I built a multi-agent AI system with secure function calling"
- "Implemented LRU caching for 99% performance improvement"
- "Designed strategic system prompts with goal-hierarchy thinking"
- "Enforced security in AI systems with validation layers"

---

## 🚀 Future Enhancements

### Phase 3 (Planned)
- **Calendar Integration** - Schedule awareness for planning
- **Energy Tracking** - Capacity-aware task recommendations
- **Conversation Memory** - Persistent chat history in database
- **User Preferences** - Learn and adapt to communication style

### Phase 4 (Vision)
- **Specialized Sub-Agents:**
  - Task Manager (breakdown and estimation)
  - Deep Work Analyzer (productivity insights)
  - Schedule Optimizer (deadline-aware planning)
- **Agent Coordination** - Multi-agent orchestration
- **Advanced Context** - Vector database for semantic search

---

## 📝 Development Log

### Module 2.1: AI Agent Foundation
- **Oct 24:** Phases 1-4 complete (7h 41min) - 90% done
  - Token utils, BaseAgent, Context, Function calling
- **Oct 25:** Phase 5 in progress - Streaming & Frontend
- **Status:** 80% complete

See [[Module 2.1 - AI Agent Foundation]] for detailed development notes.

---

## 🤝 Acknowledgments

**Teaching Methodology:**
- 60/40 manual coding to AI assistance ratio
- Problem-first learning approach
- Quality gates at module completion
- Comprehensive documentation for knowledge retention

**Technologies:**
- OpenAI for GPT-4 API
- Supabase for database infrastructure
- Vercel for (future) deployment
- shadcn/ui for component library

---

## 📬 Contact

**Jaymin Chang**  
MS Computer Science Student @ Northeastern University (Align Program)  
Targeting visa-sponsored SWE roles (Spring 2027)

GitHub: [jmin1219](https://github.com/jmin1219/atlas)  
Email: chang.jaym@northeastern.edu

---

## 📄 License

MIT License - Feel free to learn from this code!

---

**Status:** Active Development | **Last Updated:** October 25, 2025  
**Portfolio Project** | **Interview-Ready Demo** | **Production Architecture**

*Built with strategic thinking in Vancouver, BC 🇨🇦*
