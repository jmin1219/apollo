"""DB helper scaffolds for agent data retrieval.

This module provides a simple fetch helper you will implement to read
conversation history from your DB. The scaffold uses the existing
`backend/app/db/supabase_client.py` client. Adjust `TABLE_NAME` and column
names to match your schema.
"""
from typing import List

from backend.app.db.supabase_client import supabase

# TODO: change this to your actual messages/conversations table name
TABLE_NAME = "messages"


async def fetch_last_messages_for_user(user_id: str, limit: int = 200) -> List[str]:
    """Fetch recent messages for a user (oldest-first) and return as List[str].

    Current scaffold uses the Supabase client synchronously under the hood.
    Keep the async signature so `create_agent_context` can await it. You can
    either implement this as sync (and keep it fast) or offload to a thread
    executor if the client blocks.

    TODOs for you:
    - Update TABLE_NAME to the actual table name.
    - Update `.select()` columns and order key to match your schema.
    - Optionally convert message rows to a richer message object.
    """
    # NOTE: supabase-py is synchronous in many versions. This simple scaffold
    # calls it directly; if it blocks in your runtime, convert with a thread
    # pool (e.g., anyio.to_thread.run_sync or asyncio.to_thread).

    # Example: expects table with columns: user_id, content, created_at
    resp = (
        supabase.table(TABLE_NAME)
        .select("content, created_at")
        .eq("user_id", user_id)
        .order("created_at", count="asc")
        .limit(limit)
        .execute()
    )

    data = resp.data if hasattr(resp, "data") else resp
    if not data:
        return []

    # Convert rows to plain strings (oldest-first). Adjust key if different.
    messages = [row.get("content") or "" for row in data]
    return messages
