import os
from typing import Optional, cast

from dotenv import load_dotenv
from supabase import Client, create_client

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials
supabase_url: Optional[str] = os.getenv("SUPABASE_URL")
supabase_key: Optional[str] = os.getenv("SUPABASE_KEY")

# Validate credentials exist
if not supabase_url or not supabase_key:
    raise ValueError("Supabase credentials not found in environment variables")

# Create Supabase client (cast to str since we validated above)
supabase: Client = create_client(cast(str, supabase_url), cast(str, supabase_key))
