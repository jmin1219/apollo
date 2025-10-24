# APOLLO Project Context for GitHub Copilot

**Updated:** 2025-10-23 5:10 PM

## Project Overview
**APOLLO** (Autonomous Productivity & Optimization Life Logic Orchestrator)
- Multi-agent AI life assistant system
- Portfolio capstone project (Spring 2027 job search)
- **Renamed from ATLAS** on 2025-10-22 (OpenAI announced Atlas browser)
- Timeline: Oct 2025 - Dec 2025 (12 weeks)
- Repository: `/Users/jayminchang/Documents/professional/atlas-project`

## Tech Stack

### Backend (`/backend`)
- **Python 3.13** with FastAPI
- **PostgreSQL** via Supabase Cloud
- **Authentication:** JWT with OAuth2PasswordBearer, bcrypt password hashing
- **Data validation:** Pydantic v2 (with `@field_validator` + `@classmethod`)
- **API:** RESTful with async/await
- **Dependencies:** python-jose, passlib, python-multipart, supabase, python-dotenv

### Frontend (`/frontend`) - IN PROGRESS
- **Next.js 15** with App Router
- **React 19** with TypeScript
- **Styling:** Tailwind CSS
- **Components:** shadcn/ui
- **State:** React hooks (useState, useEffect) - no Redux yet
- **API calls:** fetch with JWT injection wrapper
- **Auth storage:** localStorage (JWT tokens)

## Architecture Patterns

### Monorepo Structure
```
/backend          # FastAPI REST API
  /app
    /auth         # Password hashing, JWT, dependencies
    /db           # Supabase client
    /models       # Pydantic models (User, Task, etc.)
  main.py         # FastAPI app entry
  requirements.txt
  .env            # Supabase URL, SECRET_KEY

/frontend         # Next.js 15 App Router
  /app            # Pages and layouts
  /components     # React components
  /lib            # API wrapper, auth helpers
  /types          # TypeScript interfaces
```

### API Design
- **RESTful endpoints** with standard HTTP verbs
- **JWT authentication** (30-min expiration)
- **User isolation:** All queries filtered by `current_user.id`
- **UUID primary keys** (security: prevents ID enumeration)
- **Error handling:** 400 (client error), 401 (auth), 404 (not found), 500 (server error)

### Database Schema
```sql
users: 
  id (uuid PK), 
  email (unique), 
  hashed_password, 
  created_at, 
  updated_at

tasks: 
  id (uuid PK), 
  user_id (uuid FK → users.id, CASCADE), 
  title, 
  description, 
  status (default: 'pending'),
  created_at, 
  updated_at
```

### Authentication Flow
1. **Register:** POST /auth/register → hash password → store → return UserPublic (no password)
2. **Login:** POST /auth/login → verify password → generate JWT → return token
3. **Protected routes:** Extract JWT → verify → get user → inject `current_user` dependency

## Current Status (Module 1.5 IN PROGRESS)

### ✅ Completed Modules
- **Module 1.1:** FastAPI Setup & Health Check
- **Module 1.2:** Database Integration (Supabase)
- **Module 1.3:** Task Management CRUD (5 endpoints)
- **Module 1.4:** User Authentication (JWT, OAuth2, protected endpoints)

### 🚧 Current Work
- **Module 1.5:** Frontend Development (Next.js + React + TypeScript)

### API Endpoints Available
```
POST   /auth/register    # Register user (email, password → UserPublic)
POST   /auth/login       # Login (OAuth2 form → JWT token)
GET    /auth/me          # Get current user (protected)

POST   /tasks            # Create task (protected, user_id from token)
GET    /tasks            # List tasks (protected, filtered by current_user)
GET    /tasks/{id}       # Get task (protected, ownership check)
PATCH  /tasks/{id}       # Update task (protected, ownership check)
DELETE /tasks/{id}       # Delete task (protected, ownership check)
```

## Code Style & Conventions

### TypeScript/React
- **Strict mode:** Explicit types, no `any`
- **Components:** Functional with hooks, PascalCase naming
- **Files:** kebab-case for pages, PascalCase for components
- **API calls:** Wrapper function with JWT injection
- **Error handling:** try-catch with user-friendly messages
- **State:** Local state first (useState), lift up when needed

### Python/FastAPI
- **Type hints:** Always use for function params/returns
- **Async:** All route handlers are `async def`
- **Pydantic v2:** Use `@field_validator` + `@classmethod` (not deprecated `@validator`)
- **Error handling:** HTTPException with appropriate status codes
- **Security:** Never return `hashed_password`, always use `pwd_context.verify()`

### Database Patterns
- **Ownership checks:** `.eq("user_id", current_user.id)` in all queries
- **Error responses:** Return 404 (not 403) when resource belongs to another user
- **Foreign keys:** CASCADE deletion (deleting user deletes their tasks)

## Development Philosophy
- **60% manual coding / 40% AI assistance** (interview readiness)
- **Learning-first:** Understand WHY before implementing
- **Quality gates:** Must explain every architectural decision
- **Incremental:** Small, tested changes with frequent commits
- **Documentation:** Dev notes in Obsidian, comments in code

### Teaching Workflow (APOLLO Educator Standard)
**See `.atlas-dev/teaching-workflow.md` for complete methodology**

When helping Jaymin learn:
1. Start with WHY (show the problem before the solution)
2. Ask questions to verify understanding at each step
3. Use fill-in-the-blanks approach (structure provided, student completes logic)
4. Give positive-first feedback (what's right, then refinements)
5. Concrete examples before abstract concepts
6. Reveal purpose through experiencing pain points first
7. Teach TypeScript in context (not separately)
8. Errors are teaching moments (guide through fixing)

This workflow produces "aha moments" and deep understanding.

## Interview Talking Points
1. **UUID primary keys:** Prevents ID enumeration attacks, distributed-system ready
2. **JWT stateless auth:** Scales horizontally, no session storage needed
3. **User isolation:** Database-level filtering (not app logic) prevents data leakage
4. **Pydantic validation:** Type safety + automatic OpenAPI docs
5. **Monorepo:** Development velocity, single source of truth
6. **TypeScript:** Type safety catches errors at compile-time
7. **Protected routes:** Client-side auth check with token verification

## Common Patterns

### Protected API Call (Frontend)
```typescript
// lib/api.ts
export async function apiFetch(endpoint: string, options?: RequestInit) {
  const token = localStorage.getItem('token')
  const response = await fetch(`http://localhost:8000${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options?.headers
    }
  })
  if (!response.ok) throw new Error(`API error: ${response.status}`)
  return response.json()
}
```

### Protected Route (Backend)
```python
from app.auth.dependencies import get_current_user
from app.models.user import User

@app.get("/tasks")
async def list_tasks(current_user: User = Depends(get_current_user)):
    # current_user injected automatically from JWT
    tasks = supabase.table("tasks").select("*").eq("user_id", current_user.id).execute()
    return tasks.data
```

### Type-Safe Component
```typescript
interface Task {
  id: string
  user_id: string
  title: string
  description: string | null
  status: string
  created_at: string
  updated_at: string
}

export function TaskCard({ task }: { task: Task }) {
  return <div>{task.title}</div>
}
```

## Next Steps
1. Create Next.js frontend structure
2. Build authentication UI (login, register)
3. Implement protected dashboard layout
4. Create task management interface
5. Add loading states and error handling

## Security Notes
- **NEVER** store passwords in plain text
- **NEVER** return `hashed_password` in API responses
- **ALWAYS** verify JWT tokens before accessing protected routes
- **ALWAYS** filter data by `current_user.id` in queries
- JWT tokens in localStorage (production would use httpOnly cookies)

## Environment Variables
```env
# backend/.env
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your-key
SECRET_KEY=your-secret-key-256-bits
```

## Copilot Instructions
- Prioritize TypeScript strict types
- Use functional React components with hooks
- Follow existing patterns from backend (error handling, validation)
- Add comments for complex logic
- Suggest type-safe solutions
- Reference this context for project decisions
