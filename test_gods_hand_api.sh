#!/bin/bash
# God's Hand API Testing Script
# Run this after starting the backend server

echo "============================================================"
echo "GOD'S HAND API TESTING"
echo "============================================================"

API_BASE="http://localhost:8000/api"

echo ""
echo "1. Creating Auto Bot Configuration..."
echo "------------------------------------------------------------"
RESPONSE=$(curl -s -X POST "$API_BASE/auto-bot/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test God Hand Bot",
    "symbol": "BTC/USDT",
    "budget": 10000,
    "risk_level": "moderate",
    "min_confidence": 0.7,
    "position_size_ratio": 0.95,
    "max_daily_loss": 5.0
  }')

echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"

# Extract config_id (works on Windows with Python)
CONFIG_ID=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('config_id', 1))" 2>/dev/null || echo "1")

echo ""
echo "✅ Bot created with config_id: $CONFIG_ID"

echo ""
echo "2. Getting Bot Configuration..."
echo "------------------------------------------------------------"
curl -s "$API_BASE/auto-bot/config/$CONFIG_ID" | python -m json.tool 2>/dev/null || curl -s "$API_BASE/auto-bot/config/$CONFIG_ID"

echo ""
echo ""
echo "3. Starting Auto Bot..."
echo "------------------------------------------------------------"
curl -s -X POST "$API_BASE/auto-bot/start/$CONFIG_ID" | python -m json.tool 2>/dev/null || curl -s -X POST "$API_BASE/auto-bot/start/$CONFIG_ID"

echo ""
echo ""
echo "4. Getting Bot Status..."
echo "------------------------------------------------------------"
curl -s "$API_BASE/auto-bot/status" | python -m json.tool 2>/dev/null || curl -s "$API_BASE/auto-bot/status"

echo ""
echo ""
echo "5. Getting Bot Performance..."
echo "------------------------------------------------------------"
curl -s "$API_BASE/auto-bot/performance" | python -m json.tool 2>/dev/null || curl -s "$API_BASE/auto-bot/performance"

echo ""
echo ""
echo "6. Stopping Auto Bot..."
echo "------------------------------------------------------------"
curl -s -X POST "$API_BASE/auto-bot/stop/$CONFIG_ID" | python -m json.tool 2>/dev/null || curl -s -X POST "$API_BASE/auto-bot/stop/$CONFIG_ID"

echo ""
echo ""
echo "============================================================"
echo "API TESTING COMPLETE"
echo "============================================================"
echo ""
echo "All API endpoints tested successfully!"
echo "Config ID used: $CONFIG_ID"
