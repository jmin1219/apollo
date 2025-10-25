"""
Test the streaming endpoint directly (bypasses auth for testing).
Run: python -m app.agents.tests.test_streaming_endpoint
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_endpoint():
    """Test streaming endpoint with real HTTP request."""

    # First login to get JWT
    async with httpx.AsyncClient() as client:
        print("🔐 Logging in...")
        login_response = await client.post(
            "http://localhost:8000/auth/login",
            data={
                "username": "admin@me.com",  # Replace with your email
                "password": "admin123"  # Replace with your password
            }
        )

        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return

        token = login_response.json()["access_token"]
        print(f"✅ Got token: {token[:20]}...")
        print()

        # Now test streaming
        print("📤 Sending: 'What should I focus on today?'")
        print()
        print("📥 Streaming response:")
        print("-" * 60)

        async with client.stream(
            "POST",
            "http://localhost:8000/chat/stream",
            json={
                "message": "What should I focus on today?",
                "conversation_history": []
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=30.0
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    import json
                    data = json.loads(line[6:])  # Remove "data: " prefix

                    if data["type"] == "chunk":
                        print(data["content"], end="", flush=True)
                    elif data["type"] == "done":
                        print()
                        print("-" * 60)
                        print("✅ Stream complete!")
                    elif data["type"] == "error":
                        print(f"\n❌ Error: {data['content']}")

        print()


if __name__ == "__main__":
    print("Starting FastAPI server test...")
    print("Make sure server is running: uvicorn app.main:app --reload")
    print()

    asyncio.run(test_endpoint())
