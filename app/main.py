from fastapi import FastAPI, HTTPException
from app.models.user import User
from app.db.supabase_client import supabase
from fastapi.middleware.cors import CORSMiddleware

# Fast API is needed even though also using Next.js for frontend because while Next.js API routes can run JavaScript/TypeScript, ATLAS's backend logic and integrations are implemented in Python for OpenAI SDK, LandChain, etc. FastAPI provides a robust framework for building APIs, handling requests, and managing data processing that complements the frontend capabilities of Next.js.

# 1. APP CREATION - Create Fast API app instance
app = FastAPI(
  title="ATLAS",
  description="Autonomous Tracking & Life Advisory System",
  version="0.1.0"
)

# 2. MIDDLEWARE - Configure CORS middleware for frontend access
# Without CORS, browser will block Next.js frontend from accessing FastAPI backend because they run on different origins (domains/ports), eg. localhost:3000 vs localhost:8000
app.add_middleware(  # - Adds processing that happens for EVERY request
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production for security
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers (e.g., Authorization, Content-Type)
)

# 3. ROUTES - Define API endpoints
# Health check endpoint
@app.get("/health")
async def health_check():
  """Simple health check endpoint to verify the API is running."""
  return {"status": "healthy", "service": "ATLAS"}

# Root endpoint
@app.get("/")
async def root():
  """Welcome message with basic API info."""
  return {"message": "Welcome to the ATLAS API!", "version": "0.1.0"}

# User creation endpoint
@app.post("/users", response_model=User)
async def create_user(user: User):
  """
    Create a new user
    
    - **email**: User's email address (validated)
  """
  try:
    response = supabase.table("users").insert({
      "email": user.email
    }).execute()

    if not response.data:
      raise HTTPException(status_code=500, detail="Failed to create user")

    created_user = response.data[0]

    return User(**created_user)

  except Exception as e:
    # Handle duplicate email error or other database errors
    error_message = str(e).lower()
    if "duplicate key" in error_message or "unique constraint" in error_message:
      raise HTTPException(status_code=400, detail="Email already exists")
    # Generic error handling 
    raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

# User retrieval endpoint
@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
  """
    Get a user by ID
    
    - **user_id**: UUID of the user
  """
  try:
    response = supabase.table("users").select("*").eq("id", user_id).execute()

    if not response.data:
      raise HTTPException(status_code=404, detail="User not found")

    return User(**response.data[0])


  except HTTPException:
    raise  # Re-raise HTTP exceptions to be handled by FastAPI
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")
  

# 4. STARTUP/SHUTDOWN EVENTS - Define actions on startup/shutdown