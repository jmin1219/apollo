#!/bin/bash

# Clean up test data from APOLLO database

echo "============================================"
echo "APOLLO Database Cleanup - Test Data"
echo "============================================"
echo ""

EMAIL="admin@me.com"
PASSWORD="admin123"

echo "Authenticating..."
LOGIN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=$PASSWORD")

TOKEN=$(echo "$LOGIN" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to authenticate"
    exit 1
fi
echo "✅ Authenticated"
echo ""

# Clean milestones
echo "Cleaning test milestones..."
MILESTONES=$(curl -s -X GET "http://localhost:8000/milestones" \
  -H "Authorization: Bearer $TOKEN")

echo "$MILESTONES" | jq -r '.[] | select(.title | test("Test|Another|Final|Streaming")) | .id' 2>/dev/null | while read -r id; do
    if [ ! -z "$id" ]; then
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "http://localhost:8000/milestones/$id" \
          -H "Authorization: Bearer $TOKEN")
        echo "  ✅ Deleted milestone $id (HTTP $STATUS)"
    fi
done

echo ""
echo "Cleaning test goals..."
GOALS=$(curl -s -X GET "http://localhost:8000/goals" \
  -H "Authorization: Bearer $TOKEN")

echo "$GOALS" | jq -r '.[] | select(.title | test("Test|six pack|Empty|Updated")) | .id' 2>/dev/null | while read -r id; do
    if [ ! -z "$id" ]; then
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "http://localhost:8000/goals/$id" \
          -H "Authorization: Bearer $TOKEN")
        echo "  ✅ Deleted goal $id (HTTP $STATUS)"
    fi
done

echo ""
echo "✅ Cleanup complete!"
echo "Refresh browser to see updated data"
