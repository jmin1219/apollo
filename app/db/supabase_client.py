from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials
supabase_url: str = os.getenv("SUPABASE_URL")
supabase_key: str = os.getenv("SUPABASE_KEY")

# Validate credentials exist
if not supabase_url or not supabase_key:
    raise ValueError("Supabase credentials not found in environment variables")

# Create Supabase client
supabase: Client = create_client(supabase_url, supabase_key)