from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Fast API is needed even though also using Next.js for frontend because while Next.js API routes can run JavaScript/TypeScript, ATLAS's backend logic and integrations are implemented in Python for OpenAI SDK, LandChain, etc. FastAPI provides a robust framework for building APIs, handling requests, and managing data processing that complements the frontend capabilities of Next.js.

# 1. APP CREATION - Create Fast API app instance
app = FastAPI(
  title="ATLAS",
  description="Multi-Agent Productivity System",
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


# 4. STARTUP/SHUTDOWN EVENTS - Define actions on startup/shutdown