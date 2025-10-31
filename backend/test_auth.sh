#!/bin/bash

# Test authentication and chat endpoint

echo "=== Step 1: Login to get token ==="
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=YOUR_EMAIL&password=YOUR_PASSWORD")

echo "$LOGIN_RESPONSE"
echo ""

# Extract token (requires jq)
if command -v jq &> /dev/null; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
    echo "Extracted token: ${TOKEN:0:20}..."
    echo ""
    
    echo "=== Step 2: Test /auth/me endpoint ==="
    curl -s -X GET http://localhost:8000/auth/me \
      -H "Authorization: Bearer $TOKEN" | jq
    echo ""
    
    echo "=== Step 3: Test /chat/stream endpoint ==="
    echo "Testing chat stream..."
    curl -X POST http://localhost:8000/chat/stream \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "message": "create a test milestone with target 2025-12-31"
      }'
    echo ""
else
    echo "Install jq for automatic token extraction: brew install jq"
    echo "Or manually copy the access_token from above"
fi
