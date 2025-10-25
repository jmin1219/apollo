from typing import Any, cast

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.dependencies import get_current_user
from app.auth.jwt import create_access_token
from app.auth.password import hash_password, verify_password
from app.db.supabase_client import supabase
from app.models.task import Task, TaskUpdate
from app.models.user import User, UserCreate, UserPublic
from app.routes import chat

# FastAPI is needed even though also using Next.js for frontend. While Next.js API
# routes can run JavaScript/TypeScript, APOLLO's backend logic and integrations
# are implemented in Python (OpenAI SDK, LangChain, etc.). FastAPI provides a
# robust framework for building APIs, handling requests, and managing data
# processing that complements the frontend capabilities of Next.js.
# 1. APP CREATION - Create Fast API app instance
app = FastAPI(
    title="APOLLO",
    description="Autonomous Productivity & Optimization Life Logic Orchestrator",
    version="0.1.0",
)

# 2. MIDDLEWARE - Configure CORS middleware for frontend access
# Without CORS, the browser will block the Next.js frontend from accessing the
# FastAPI backend because they run on different origins (domains/ports), e.g.
# localhost:3000 vs localhost:8000
app.add_middleware(  # - Adds processing that happens for EVERY request
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production for security
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers (e.g., Authorization, Content-Type)
)

# Router registration
app.include_router(chat.router)

# 3. ROUTES - Define API endpoints
# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint to verify the API is running."""
    return {"status": "healthy", "service": "APOLLO"}


# Root endpoint
@app.get("/")
async def root():
    """Welcome message with basic API info."""
    return {"message": "Welcome to the APOLLO API!", "version": "0.1.0"}


# User creation endpoint
@app.post("/users", response_model=User)
async def create_user(user: User):
    """
    Create a new user

    - **email**: User's email address (validated)
    """
    try:
        response: Any = supabase.table("users").insert({"email": user.email}).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create user")

        created_user: dict = cast(dict, response.data[0])

        return User(**created_user)

    except Exception as e:
        # Handle duplicate email error or other database errors
        error_message = str(e).lower()
        if "duplicate key" in error_message or "unique constraint" in error_message:
            raise HTTPException(status_code=400, detail="Email already exists") from e
        # Generic error handling
        detail = f"Error creating user: {e!s}"
        raise HTTPException(status_code=500, detail=detail) from e


# User retrieval endpoint
@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """
    Get a user by ID

    - **user_id**: UUID of the user
    """
    try:
        response: Any = supabase.table("users").select("*").eq("id", user_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")

        return User(**cast(dict, response.data[0]))

    except HTTPException:
        raise  # Re-raise HTTP exceptions to be handled by FastAPI
    except Exception as e:
        detail = f"Error retrieving user: {e!s}"
        raise HTTPException(status_code=500, detail=detail) from e


@app.post("/tasks", status_code=201)
async def create_task(
    task: Task,
    current_user: User = Depends(get_current_user),
    ):
    """
    Create a new task

    - **user_id**: UUID of the user who owns the task
    - **title**: Title of the task
    - **description**: Detailed description (optional)
    - **status**: Task status (default: "pending")
    """
    try:
        response: Any = (
            supabase.table("tasks")
            .insert(
                {
                    "user_id": current_user.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                }
            )
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create task")

        created_task: dict = cast(dict, response.data[0])
        return Task(**created_task)

    except Exception as e:
        error_msg = str(e)

        # UUID validation error: invalid UUID format
        if "invalid input syntax for type uuid" in error_msg.lower():
            raise HTTPException(
                status_code=400, detail="Invalid user_id: must be a valid UUID"
            ) from e
        # Foreign key violation: user_id doesn't exist
        if (
            "foreign key constraint" in error_msg.lower()
            or "violates foreign key" in error_msg.lower()
        ):
            raise HTTPException(
                status_code=400, detail="Invalid user_id: user does not exist"
            ) from e

        # Any other error is a server error
        detail = f"Error creating task: {error_msg}"
        raise HTTPException(status_code=500, detail=detail) from e


# Task retrieval by task ID endpoint
@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get a task by ID (must belong to current user)

    - **task_id**: UUID of the task
    """
    try:
        response: Any = supabase.table("tasks").select("*").eq("id", task_id).eq("user_id", current_user.id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Task not found")

        return Task(**cast(dict, response.data[0]))

    except HTTPException:
        raise  # Re-raise HTTP exceptions to be handled by FastAPI
    except Exception as e:
        error_msg = str(e)
        # UUID validation error
        if "invalid input syntax for type uuid" in error_msg.lower():
            raise HTTPException(
                status_code=400, detail="Invalid task_id: must be a valid UUID"
            ) from e
        detail = f"Error retrieving task: {error_msg}"
        raise HTTPException(status_code=500, detail=detail) from e


# Task list retrieval by user ID or task status endpoint
@app.get("/tasks", response_model=list[Task])
async def list_tasks(
    current_user: User = Depends(get_current_user),
    status: str | None = None
):
    """
    List tasks of the current user, optionally filtered by status

    - **current_user**: Filter by current authenticated user
    - **status**: Filter by status (optional)
    """
    try:
        query = supabase.table("tasks").select("*").eq("user_id", current_user.id)

        if status:
            query = query.eq("status", status)

        response: Any = query.execute()

        tasks_data = cast(list[dict], response.data)
        return [Task(**task) for task in tasks_data]

    except Exception as e:
        error_msg = str(e)
        detail = f"Error retrieving tasks: {error_msg}"

        # UUID validation error for user_id filter
        if "invalid input syntax for type uuid" in error_msg.lower():
            raise HTTPException(
                status_code=400, detail="Invalid user_id: must be a valid UUID"
            ) from e

        raise HTTPException(status_code=500, detail=detail) from e


# Task update endpoint
@app.patch("/tasks/{task_id}", response_model=Task)
async def update_task(
    task_id: str, task: TaskUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a task (partial update)
    Must belong to current user

    - **task_id**: UUID of the task
    - **title**: Updated title (optional)
    - **description**: Updated description (optional)
    - **status**: Updated status (optional)
    """
    try:
        update_data = {}
        if task.title is not None:
            update_data["title"] = task.title
        if task.description is not None:
            update_data["description"] = task.description
        if task.status is not None:
            update_data["status"] = task.status

        update_data["updated_at"] = "now()"  # Supabase uses SQL NOW()

        response: Any = (
            supabase.table("tasks").update(update_data).eq("id", task_id).eq("user_id", current_user.id).execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Task not found")

        updated_task: dict = cast(dict, response.data[0])
        return Task(**updated_task)

    except HTTPException:
        raise  # Re-raise HTTP exceptions to be handled by FastAPI
    except Exception as e:
        error_msg = str(e)
        # UUID validation error
        if "invalid input syntax for type uuid" in error_msg.lower():
            raise HTTPException(
                status_code=400, detail="Invalid task_id: must be a valid UUID"
            ) from e
        detail = f"Error updating task: {error_msg}"
        raise HTTPException(status_code=500, detail=detail) from e


# Delete task endpoint
@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: str, current_user: User = Depends(get_current_user)):
    """
    Delete a task by ID (must belong to current user)

    - **task_id**: UUID of the task
    """
    try:
        response: Any = supabase.table("tasks").delete().eq("id", task_id).eq("user_id", current_user.id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Task not found")

        return  # 204 No Content

    except HTTPException:
        raise  # Re-raise HTTP exceptions to be handled by FastAPI
    except Exception as e:
        error_msg = str(e)
        # UUID validation error
        if "invalid input syntax for type uuid" in error_msg.lower():
            raise HTTPException(
                status_code=400, detail="Invalid task_id: must be a valid UUID"
            ) from e
        detail = f"Error deleting task: {error_msg}"
        raise HTTPException(status_code=500, detail=detail) from e

# Register user endpoint
@app.post("/auth/register", response_model=UserPublic, status_code=201)
async def register_user(user: UserCreate):
    """
    Register a new user with email and password

    - **email**: User's email address (validated)
    - **password**: Plaintext password (will be hashed before storage)
    """
    try:
        # Check if email already exists
        existing_response: Any = (
            supabase.table("users").select("*").eq("email", user.email).execute()
        )

        if existing_response.data:
            raise HTTPException(status_code=400, detail="Email already exists")

        # Hash the plaintext password
        hashed_password = hash_password(user.password)

        # Insert new user into the database
        response: Any = supabase.table("users").insert(
            {
                "email": user.email,
                "hashed_password": hashed_password,
            }
        ).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create user")

        created_user: dict = cast(dict, response.data[0])

        return UserPublic(
            id=created_user["id"],
            email=created_user["email"],
            created_at=created_user["created_at"],
        )

    except Exception as e:
        # Handle duplicate email error or other database errors
        error_message = str(e).lower()
        if "duplicate key" in error_message or "unique constraint" in error_message:
            raise HTTPException(status_code=400, detail="Email already exists") from e
        # Generic error handling
        detail = f"Error creating user: {e!s}"
        raise HTTPException(status_code=500, detail=detail) from e

# Login user endpoint
@app.post("/auth/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login with email and password, returns JWT access token

    OAuth2 standard uses 'username' field, but we accept email there.
    """
    try:
        # Query user by email (OAuth2 uses 'username' field for email)
        response: Any = (
            supabase.table("users")
            .select("*")
            .eq("email", form_data.username)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )

        user_data: dict = cast(dict, response.data[0])

        # verify password
        if not verify_password(form_data.password, user_data["hashed_password"]):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Generate JWT token (implementation omitted for brevity)
        access_token = create_access_token(data={"sub": user_data["id"]})

        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise  # Re-raise HTTP exceptions to be handled by FastAPI
    except Exception as e:
        detail = f"Error during login: {e!s}"
        raise HTTPException(status_code=500, detail=detail) from e

# Get Me endpoint
@app.get("/auth/me", response_model=UserPublic)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get the currently authenticated user's info

    Requires a valid JWT token in the Authorization header.
    """

    # Assert fields exist (they should from database)
    assert current_user.id is not None
    assert current_user.created_at is not None

    return UserPublic(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at,
    )
