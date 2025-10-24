# GitHub Copilot Instructions for APOLLO Project

## Project Context
See `.atlas-dev/context.md` for complete project documentation.

## Code Generation Guidelines

### TypeScript/React (Frontend)
1. **Always use TypeScript strict mode** - No `any` types
2. **Functional components with hooks** - No class components
3. **Explicit prop types** - Define interfaces for all props
4. **API error handling** - Always wrap fetch in try-catch
5. **Loading states** - Add loading boolean for async operations
6. **Form validation** - Client-side validation before API calls

### Python/FastAPI (Backend)
1. **Type hints required** - All function params and returns
2. **Pydantic v2 patterns** - Use `@field_validator` + `@classmethod`
3. **Async route handlers** - All endpoints are `async def`
4. **User isolation** - Always filter by `current_user.id`
5. **Error status codes** - 400 client, 401 auth, 404 not found, 500 server

## Naming Conventions
- **Components:** PascalCase (`TaskCard`, `LoginForm`)
- **Files:** kebab-case pages, PascalCase components
- **Functions:** camelCase (`fetchTasks`, `handleSubmit`)
- **Constants:** UPPER_SNAKE_CASE (`API_BASE_URL`)
- **Interfaces:** PascalCase with descriptive names (`Task`, `User`)

## Security Patterns
- Never expose `hashed_password` in responses
- Always inject `current_user` via `Depends(get_current_user)`
- JWT tokens in Authorization header: `Bearer {token}`
- Filter all queries by user ownership
- Return 404 (not 403) for unauthorized resource access

## Common Patterns to Follow

### API Wrapper (Frontend)
```typescript
async function apiFetch(endpoint: string, options?: RequestInit) {
  const token = localStorage.getItem('token')
  return fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options?.headers
    }
  })
}
```

### Protected Route (Backend)
```python
@app.get("/resource")
async def get_resource(current_user: User = Depends(get_current_user)):
    return supabase.table("resource").select("*").eq("user_id", current_user.id).execute()
```

### Form Component (Frontend)
```typescript
export function Form() {
  const [data, setData] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await apiFetch('/endpoint', { method: 'POST', body: JSON.stringify(data) })
    } catch (err) {
      setError('Failed to submit')
    } finally {
      setLoading(false)
    }
  }
}
```

## Tech Stack
- **Backend:** Python 3.13, FastAPI, Supabase, JWT auth
- **Frontend:** Next.js 15, React 19, TypeScript, Tailwind CSS
- **Database:** PostgreSQL (via Supabase)
- **Components:** shadcn/ui
- **State:** React hooks (no Redux yet)

## Current Phase
Building frontend (Module 1.5) - authentication UI and task management interface.

## Teaching Workflow (CRITICAL)
**When helping Jaymin learn, follow the APOLLO Teaching Workflow:**

See `.atlas-dev/teaching-workflow.md` for complete methodology.

**Key principles:**
1. **Problem-first, solution-second** - Show why before how
2. **Ask questions, don't lecture** - Verify understanding at each step
3. **Fill-in-the-blanks > Complete code** - Let them write, guide don't write
4. **Positive-first feedback** - What's right, then how to improve
5. **Concrete examples before abstractions** - Show working code, then explain patterns
6. **Reveal purpose through pain** - Let them experience the problem before showing the solution

**Example: Instead of giving complete function**
```typescript
// ❌ Don't do this:
export async function apiFetch<T>(endpoint: string) { /* complete code */ }

// ✅ Do this:
async function apiFetch(endpoint, options) {
  // TODO: Get JWT token from localStorage
  const token = ???
  // TODO: What headers do we need?
  headers: { ??? }
}
// Now YOU fill in the ??? parts. What would you put there?
```
