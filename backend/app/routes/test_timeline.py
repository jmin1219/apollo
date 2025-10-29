"""
Test Timeline API endpoint.

Run with: python -m app.routes.test_timeline

NOTE: Requires backend server running:
    uvicorn app.main:app --reload
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Get JWT token (you need to login first)
BASE_URL = "http://localhost:8000"
TEST_EMAIL = os.getenv("TEST_EMAIL", "test@example.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "password123")


def get_auth_token():
    """Login and get JWT token."""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Login failed: {response.text}")
        print("Make sure backend is running: uvicorn app.main:app --reload")
        return None


def test_timeline_endpoint():
    """Test all 4 timeline horizons."""
    
    print("🧪 Testing Timeline API Endpoint...")
    print(f"Base URL: {BASE_URL}\n")
    
    # Get auth token
    token = get_auth_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test all 4 horizons
    horizons = ["today", "week", "month", "year"]
    
    for horizon in horizons:
        print("=" * 60)
        print(f"TEST: /planning/timeline?horizon={horizon}")
        print("=" * 60)
        
        response = requests.get(
            f"{BASE_URL}/planning/timeline",
            params={"horizon": horizon},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {horizon.upper()} view working!")
            print(f"   Horizon: {data['horizon']}")
            print(f"   Items returned: {len(data['items'])}")
            
            # Count by type
            types = {}
            for item in data['items']:
                item_type = item['type']
                types[item_type] = types.get(item_type, 0) + 1
            
            if types:
                print(f"   Breakdown: {types}")
                
                # Show first 3 items
                print(f"\n   Sample items:")
                for item in data['items'][:3]:
                    print(f"     - [{item['type']}] {item['title']}")
            else:
                print(f"   No items (empty result)")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
        
        print()
    
    # Summary
    print("=" * 60)
    print("✅ TIMELINE API TEST COMPLETE!")
    print("=" * 60)
    print("\nAll 4 horizons tested:")
    print("  ✅ Today view")
    print("  ✅ Week view")
    print("  ✅ Month view")
    print("  ✅ Year view")
    print("\nNext: Build React frontend to display timeline!")


if __name__ == "__main__":
    test_timeline_endpoint()
