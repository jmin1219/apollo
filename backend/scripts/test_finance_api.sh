#!/bin/bash
#
# Test script for Finance Module API endpoints
# 
# Usage: ./scripts/test_finance_api.sh

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API base URL
BASE_URL="http://localhost:8000"

# Test credentials
EMAIL="admin@me.com"
PASSWORD="admin123"

echo "============================================================"
echo "APOLLO Finance Module - API Testing"
echo "============================================================"
echo ""

# Step 1: Login to get access token
echo -e "${BLUE}[1/7]${NC} Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=$PASSWORD")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Login failed${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✅ Login successful${NC}"
echo ""

# Step 2: Health check
echo -e "${BLUE}[2/7]${NC} Testing finance health endpoint..."
HEALTH=$(curl -s "$BASE_URL/finance/health")
echo "Response: $HEALTH"
echo ""

# Step 3: Get accounts
echo -e "${BLUE}[3/7]${NC} Fetching accounts..."
ACCOUNTS=$(curl -s "$BASE_URL/finance/accounts" \
  -H "Authorization: Bearer $TOKEN")
echo "Accounts: $ACCOUNTS" | python -m json.tool 2>/dev/null || echo "$ACCOUNTS"
echo ""

# Step 4: Get categories
echo -e "${BLUE}[4/7]${NC} Fetching categories..."
CATEGORIES=$(curl -s "$BASE_URL/finance/categories" \
  -H "Authorization: Bearer $TOKEN")
echo "Categories (first 5):" 
echo "$CATEGORIES" | python -m json.tool 2>/dev/null | head -n 30 || echo "$CATEGORIES"
echo ""

# Step 5: Get transactions
echo -e "${BLUE}[5/7]${NC} Fetching transactions (last 10)..."
TRANSACTIONS=$(curl -s "$BASE_URL/finance/transactions?limit=10" \
  -H "Authorization: Bearer $TOKEN")
echo "Transactions:" 
echo "$TRANSACTIONS" | python -m json.tool 2>/dev/null | head -n 50 || echo "$TRANSACTIONS"
echo ""

# Step 6: Get financial summary
echo -e "${BLUE}[6/7]${NC} Fetching financial summary..."
SUMMARY=$(curl -s "$BASE_URL/finance/analytics/summary" \
  -H "Authorization: Bearer $TOKEN")
echo "Summary:"
echo "$SUMMARY" | python -m json.tool 2>/dev/null || echo "$SUMMARY"
echo ""

# Step 7: Get monthly burn rate
echo -e "${BLUE}[7/7]${NC} Calculating monthly burn rate (Oct 2025)..."
BURN=$(curl -s "$BASE_URL/finance/analytics/monthly-burn?year=2025&month=10" \
  -H "Authorization: Bearer $TOKEN")
echo "Burn Rate:"
echo "$BURN" | python -m json.tool 2>/dev/null || echo "$BURN"
echo ""

echo "============================================================"
echo -e "${GREEN}✅ All tests complete!${NC}"
echo "============================================================"
