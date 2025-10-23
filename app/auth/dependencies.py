from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.jwt import verify_access_token
from app.db.supabase_client import supabase
from app.models.user import User

# OAuth2 scheme - extracts token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# FastAPI dependency to get current user from JWT token
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    FastAPI dependency that validates JWT and returns current user.

    Args:
        token: JWT token extracted from Authorization header

    Returns:
        User object if authentication successful

    Raises:
        HTTPException 401 if token invalid or user not found
    """
    # Generic error for ANY authentication failure
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify token and extract user_id
    user_id = verify_access_token(token)
    if user_id is None:
        raise credentials_exception

    # Query user from database
    try:
        response = supabase.table("users").select("*").eq("id", user_id).execute()

        if not response.data or len(response.data) == 0:  # type: ignore
            raise credentials_exception

        user_data = response.data[0]  # type: ignore

        # Create User object
        user = User(**user_data)  # type: ignore
        return user

    except HTTPException:
        # Re-raise our own exceptions
        raise
    except Exception as e:
        # Catch any other errors (DB errors, etc.)
        raise credentials_exception from e
