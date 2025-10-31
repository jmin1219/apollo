#!/bin/bash

# Test APOLLO authentication and milestone creation
# Uses credentials from .env file

echo "============================================"
echo "APOLLO Backend Test - Milestone Creation"
echo "============================================"
echo ""

# Test credentials
EMAIL="admin@me.com"
PASSWORD="admin123"

echo "Step 1: Login and get access token..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=$PASSWORD")

echo "Login response:"
echo "$LOGIN_RESPONSE" | jq '.' 2>/dev/null || echo "$LOGIN_RESPONSE"
echo ""

# Extract token (works with or without jq)
if command -v jq &> /dev/null; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
else
    # Fallback: extract token manually
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
fi

if [ -z "$TOKEN" ] || [ "$TOKEN" == "null" ]; then
    echo "❌ ERROR: Failed to get access token"
    echo "Check that:"
    echo "  1. Backend is running (uvicorn app.main:app --reload --port 8000)"
    echo "  2. User exists in database (email: $EMAIL)"
    echo "  3. Password is correct"
    exit 1
fi

echo "✅ Got access token: ${TOKEN:0:20}..."
echo ""

echo "Step 2: Verify authentication with /auth/me..."
ME_RESPONSE=$(curl -s -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN")

echo "$ME_RESPONSE" | jq '.' 2>/dev/null || echo "$ME_RESPONSE"
echo ""

echo "Step 3: Test milestone creation via /chat/stream..."
echo ""
echo "Sending message: 'create milestone Test Milestone with target date 2025-12-31'"
echo ""

curl -X POST http://localhost:8000/chat/stream \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "create milestone Test Milestone with target date 2025-12-31"
  }'

echo ""
echo ""
echo "============================================"
echo "Check backend logs for:"
echo "  [ROUTING] needs_tools=True"
echo "  [AGENT RESPONSE] Tool calls details"
echo "  [MILESTONE DEBUG] Attempting to create milestone"
echo "  [MILESTONE TOOL] Inserting milestone into database"
echo "============================================"
