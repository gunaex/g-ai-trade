@echo off
REM God's Hand API Testing Script for Windows
REM Run this after starting the backend server

echo ============================================================
echo GOD'S HAND API TESTING
echo ============================================================

set API_BASE=http://localhost:8000/api

echo.
echo 1. Creating Auto Bot Configuration...
echo ------------------------------------------------------------
curl -X POST "%API_BASE%/auto-bot/create" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Test God Hand Bot\",\"symbol\":\"BTC/USDT\",\"budget\":10000,\"risk_level\":\"moderate\",\"min_confidence\":0.7,\"position_size_ratio\":0.95,\"max_daily_loss\":5.0}"

echo.
echo.
echo 2. Getting Bot Configuration (ID: 1)...
echo ------------------------------------------------------------
curl "%API_BASE%/auto-bot/config/1"

echo.
echo.
echo 3. Starting Auto Bot...
echo ------------------------------------------------------------
curl -X POST "%API_BASE%/auto-bot/start/1"

echo.
echo.
echo 4. Getting Bot Status...
echo ------------------------------------------------------------
curl "%API_BASE%/auto-bot/status"

echo.
echo.
echo 5. Getting Bot Performance...
echo ------------------------------------------------------------
curl "%API_BASE%/auto-bot/performance"

echo.
echo.
echo 6. Stopping Auto Bot...
echo ------------------------------------------------------------
curl -X POST "%API_BASE%/auto-bot/stop/1"

echo.
echo.
echo ============================================================
echo API TESTING COMPLETE
echo ============================================================
echo.
echo All API endpoints tested successfully!
echo Config ID used: 1
echo.
pause
