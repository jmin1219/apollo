# APOLLO

**Autonomous Productivity & Optimization Life Logic Orchestrator**

A multi-agent AI system for personal productivity and strategic life planning, built as a portfolio capstone project.

---

## Project Overview

APOLLO is a sophisticated productivity system that combines:
- **AI Agent Architecture** - Natural language task management with strategic coaching
- **Multi-Horizon Planning** - Connect daily tasks to yearly goals
- **Secure Tool Calling** - AI agents that can actually do things (CRUD operations)
- **Real-time Intelligence** - Context-aware recommendations based on your actual work

**Note:** This project was originally named ATLAS but was renamed to APOLLO on 2025-10-22 to differentiate from OpenAI's Atlas browser product.

---

## Tech Stack

**Backend:**
- FastAPI (Python 3.13) - Async REST API framework
- Supabase (PostgreSQL) - Database with real-time capabilities
- Pydantic V2 - Data validation and serialization
- OpenAI SDK - Chat Completions API with function calling
- JWT Authentication - OAuth2 with bcrypt password hashing

**Frontend:**
- Next.js 15 - React framework with App Router
- TypeScript - Type-safe development
- Tailwind CSS + shadcn/ui - Modern component library

**AI/ML:**
- GPT-4 - Strategic reasoning and multi-horizon planning
- Function Calling - Secure tool execution via natural language
- Context Management - Token-optimized user data injection

---

## Current Status (Module 2.1 - 80% Complete)

**Module 1: Foundation ✅**
- [x] FastAPI setup with health checks
- [x] PostgreSQL database via Supabase (users, tasks tables)
- [x] Task Management CRUD (5 endpoints)
- [x] JWT Authentication (register, login, protected routes)
- [x] Frontend auth UI (login, dashboard, logout)

**Module 2: AI Agents (80% Complete) 🚀**
- [x] OpenAI SDK integration with token counting
- [x] BaseAgent abstract class (ABC pattern)
- [x] **LifeCoordinator Agent** - Strategic planning with 3-goal hierarchy
  - SWE visa-sponsored job (Spring 2027)
  - Antifragile body (concurrent training)
  - Personal finance
- [x] **Function Calling** - Agent can create/update/delete tasks via conversation!
- [ ] Streaming responses (Phase 5 - next)

**Next:** Streaming & Frontend chat interface

---

## Key Features

### 🤖 AI-Powered Task Management
```
You: "Add a task to buy groceries this weekend"
APOLLO: [creates task in database] "I've added 'Buy groceries this weekend' 
        to your tasks. Now you have 5 tasks. Remember, completing Module 2.1 
        Phase 3 will advance your APOLLO milestone toward your Spring 2027 goal."
```

### 🎯 Strategic Multi-Horizon Thinking
- Connects daily tasks to quarterly milestones and yearly goals
- Provides context-aware priority recommendations
- Balances competing priorities across life domains

### 🔒 Secure Tool Execution
- Agent requests actions, system validates and executes
- Ownership verification before update/delete
- user_id injection (agent can't manipulate other users' data)

### 📊 Real-Time Context Awareness
- Fetches your actual tasks from database
- Token-optimized context (20 tasks max, ~800 tokens)
- Future: Calendar integration, energy tracking

---

## Development Philosophy

- **60% Manual Coding** - Interview readiness and deep understanding
- **40% AI Assistance** - Productivity and best practices
- **Quality Gates** - Verify learning at each module completion
- **Test-First** - Comprehensive testing before feature expansion
- **Security-First** - Validate everything, trust nothing (even the AI)

---

## Getting Started

### Prerequisites
- Python 3.13+
- Node.js 18+
- Supabase account (free tier)
- OpenAI API key

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env with:
# - SUPABASE_URL
# - SUPABASE_KEY
# - SECRET_KEY (for JWT)
# - OPENAI_API_KEY

# Run database migrations (create tables in Supabase SQL Editor)
# See: backend/scripts/schema.sql

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Testing Agent Locally

```bash
cd backend
python -m app.agents.tests.test_tool_calling
```

---

## API Endpoints

### Authentication
- `POST /auth/register` - Create new user
- `POST /auth/login` - Login and receive JWT
- `GET /auth/me` - Get current user (protected)

### Tasks
- `POST /tasks` - Create task (protected)
- `GET /tasks` - List tasks with filters (protected)
- `GET /tasks/{task_id}` - Get specific task (protected)
- `PATCH /tasks/{task_id}` - Update task (protected)
- `DELETE /tasks/{task_id}` - Delete task (protected)

### AI Agent (Coming in Phase 5)
- `POST /chat/message` - Send message to Life Coordinator
- `POST /chat/stream` - Streaming conversation (SSE)

---

## Project Structure

```
apollo-project/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── base.py              # BaseAgent ABC
│   │   │   ├── life_coordinator.py  # Strategic planning agent
│   │   │   ├── context.py           # Context management
│   │   │   ├── token_utils.py       # Token counting (LRU cached)
│   │   │   ├── tools/
│   │   │   │   └── task_tools.py    # CRUD operations with security
│   │   │   └── tests/               # Agent test suite
│   │   ├── auth/                    # JWT authentication
│   │   ├── db/                      # Supabase client
│   │   ├── models/                  # Pydantic models
│   │   ├── routes/                  # API endpoints
│   │   └── main.py                  # FastAPI app
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── app/                         # Next.js 15 App Router
│   ├── components/                  # React components
│   ├── lib/                         # API wrappers, auth utilities
│   └── types/                       # TypeScript definitions
└── README.md
```

---

## Database Schema

### Users Table
- `id` (UUID) - Primary key
- `email` (TEXT) - Unique, validated
- `hashed_password` (TEXT) - bcrypt hashed
- `created_at`, `updated_at` (TIMESTAMPTZ)

### Tasks Table
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to users (CASCADE on delete)
- `title` (TEXT) - Task title (3-200 chars)
- `description` (TEXT) - Optional details
- `status` (TEXT) - pending | in_progress | completed
- `created_at`, `updated_at` (TIMESTAMPTZ)

**Indexes:**
- `user_id` for fast user task lookups
- `status` for filtering

---

## Development Roadmap

### ✅ Phase 1: Foundation (Complete)
- [x] Module 1.1: FastAPI Setup
- [x] Module 1.2: Database Integration (Supabase)
- [x] Module 1.3: Task Management CRUD
- [x] Module 1.4: User Authentication (JWT)
- [x] Module 1.5: Frontend Auth UI

### 🚧 Phase 2: AI Agents (80% Complete)
- [x] Module 2.1: AI Agent Foundation
  - [x] OpenAI SDK integration
  - [x] BaseAgent architecture (ABC pattern)
  - [x] LifeCoordinator agent (strategic planning)
  - [x] Function calling (tool execution)
  - [ ] Streaming responses (SSE) - In Progress

### 📋 Phase 3: Advanced Features (Planned)
- [ ] Module 3.1: Goal hierarchy management
- [ ] Module 3.2: Specialized sub-agents (Task Manager, Scheduler)
- [ ] Module 3.3: Calendar integration
- [ ] Module 3.4: Analytics and insights

---

## Key Innovations

### 1. Strategic AI Coordination
Not just task management - the Life Coordinator thinks across time horizons:
- **Daily:** "Focus on Module 2.1 Phase 3 today"
- **Weekly:** "This advances your APOLLO milestone"
- **Quarterly:** "Which builds your portfolio"
- **Yearly:** "Toward your Spring 2027 SWE job goal"

### 2. Secure Function Calling
Agent autonomy with system control:
```python
# Agent requests: create_task(title="Buy milk")
# System injects: user_id from authentication
# System validates: ownership, input, permissions
# System executes: actual database operation
# Agent incorporates: results into natural response
```

### 3. Multi-Goal Balancing
Helps prioritize across competing goals:
- SWE visa-sponsored job (Spring 2027 target)
- Antifragile body (concurrent training)
- Personal finance

---

## Architecture Highlights

**Agent Security Pattern:**
- ✅ Agent is untrusted actor (requests actions, doesn't execute)
- ✅ System validates all tool calls (ownership, permissions)
- ✅ user_id injection prevents cross-user access
- ✅ Field whitelisting prevents unauthorized modifications

**Performance Optimizations:**
- ✅ LRU-cached token counting (99% performance improvement)
- ✅ Token-budgeted context (20 tasks max, ~800 tokens)
- ✅ Async database operations
- ✅ Graceful degradation (agent works even if context fails)

---

## Testing

**Agent Tests:**
```bash
cd backend

# Test basic agent responses
python -m app.agents.test_agent

# Test function calling (create/update/delete)
python -m app.agents.tests.test_tool_calling

# Test deletion with confirmation
python -m app.agents.tests.test_deletion
```

**API Tests:**
```bash
# Interactive API documentation
# Visit: http://localhost:8000/docs

# Manual testing with authentication
# 1. POST /auth/register
# 2. POST /auth/login (get JWT)
# 3. Use "Authorize" button in /docs
# 4. Test protected endpoints
```

---

## Contributing

This is a personal portfolio project demonstrating:
- Full-stack development (FastAPI + Next.js)
- AI agent architecture with OpenAI
- Secure authentication patterns
- Production-grade code quality

Feedback and suggestions welcome via issues!

---

## License

MIT License - See LICENSE file for details

---

## Author

**Jaymin Chang**
- MS in Computer Science (Northeastern University - Align Program)
- Transitioning to Software Engineering
- Focus: AI Systems, Full-Stack Development, Security

---

**Built with ☕, 🎯, and strategic thinking in Vancouver, BC**

**Last Updated:** October 24, 2025
