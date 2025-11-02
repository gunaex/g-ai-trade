# 🧪 God's Hand Testing Guide

Complete testing guide for the God's Hand Auto Trading Bot feature.

---

## 📋 Pre-Testing Checklist

- [x] Database initialized (`python -m app.init_db`)
- [x] All dependencies installed (`pip install -r requirements.txt`)
- [x] Frontend dependencies installed (`cd ui && npm install`)
- [ ] Backend server running
- [ ] Frontend dev server running
- [ ] Database file exists (`trading.db`)

---

## 🚀 Step 1: Start Backend Server

### Option A: Using start.bat (Recommended)
```bash
cd D:\git\g-ai-trade
start.bat
```

### Option B: Manual Start
```bash
cd D:\git\g-ai-trade
.venv311\Scripts\python.exe -m uvicorn app.main:app --reload --log-level debug
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 🎨 Step 2: Start Frontend Dev Server

```bash
cd D:\git\g-ai-trade\ui
npm run dev
```

**Expected Output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

## 🗄️ Step 3: Initialize Database (First Time Only)

```bash
cd D:\git\g-ai-trade
.venv311\Scripts\python.exe -m app.init_db
```

**Expected Output:**
```
============================================================
DATABASE INITIALIZATION
============================================================

Creating database tables...
Tables to create:
  - trades
  - grid_bots
  - dca_bots
  - audit_logs
  - bot_configs

✅ Database tables created successfully!

Created tables:
  ✓ audit_logs
  ✓ bot_configs
  ✓ dca_bots
  ✓ grid_bots
  ✓ trades
```

---

## 🌐 Step 4: Test Frontend Navigation

1. **Open Browser**
   - Navigate to: `http://localhost:5173`

2. **Check Navbar**
   - Verify "God's Hand" link appears with Brain icon (🧠)
   - Should be between "Backtest" and "Settings"

3. **Click God's Hand**
   - URL should change to: `http://localhost:5173/gods-hand`
   - Page should load without errors

4. **Verify Special Effects**
   - Hover over "God's Hand" link → Should show gradient background
   - Active state → Should have glow effect + brain pulse animation

---

## 🤖 Step 5: Test Auto Bot Configuration

### 5.1 Open Configuration Modal

1. Click **"Activate God's Hand"** button
2. Configuration modal should open

### 5.2 Fill Configuration Form

```
Bot Name: Test God Hand Bot
Symbol: BTC/USDT
Budget: 10000
Risk Level: Moderate (select radio button)
Min Confidence: 70% (adjust slider)
Position Size: 95% (adjust slider)
Max Daily Loss: 5% (input field)
```

### 5.3 Save Configuration

1. Click **"Save Configuration"** button
2. Check browser console for success message
3. Modal should close
4. Config ID should be displayed

**Browser Console Expected:**
```javascript
Config created with ID: 1
```

---

## ▶️ Step 6: Test Bot Start/Stop

### 6.1 Start Bot

1. Click **"Start God's Hand"** button
2. Button should change to loading state
3. After success:
   - AI Module status bars should appear
   - Real-time health percentages should display
   - Status should show "Running"

**Expected AI Modules Display:**
```
🧠 Brain       ████████░  98%
🎯 Decision    ███████░░  95%
🤖 ML          ██████░░░  92%
🌐 Network     █████░░░░  88%
💬 NLP         ████░░░░░  85%
👁️ Perception  ██████░░░  90%
📚 Learning    █████░░░░  87%
```

### 6.2 Monitor Real-time Updates

- AI module percentages should update every 5 seconds
- Watch for smooth transitions
- Check console for polling requests

**Browser Console Expected:**
```javascript
// Every 5 seconds:
GET http://localhost:8000/api/auto-bot/status
Status: 200 OK
```

### 6.3 Stop Bot

1. Click **"Stop God's Hand"** button
2. Confirmation should appear
3. After confirmation:
   - AI modules should reset to 0%
   - Status should change to "Stopped"

---

## 📊 Step 7: Test Performance Metrics

### Check Performance Display

Should show:
- **Total PnL**: Dollar amount (e.g., $125.50)
- **Total Trades**: Number count (e.g., 10)
- **Recent Trades**: Table with latest trades

**Example Display:**
```
Performance
-----------
Total PnL: $125.50
Total Trades: 10

Recent Trades:
Timestamp          | Symbol    | Side | Price     | Amount
2025-11-02 13:25  | BTC/USDT  | BUY  | 43,250.00 | 0.1
2025-11-02 13:20  | BTC/USDT  | SELL | 43,300.00 | 0.1
```

---

## 🔌 Step 8: Test API Endpoints (Advanced)

### Option A: Using Test Script (Windows)

```bash
cd D:\git\g-ai-trade
test_gods_hand_api.bat
```

### Option B: Using PowerShell

```powershell
# Create Config
$body = @{
    name = "Test Bot"
    symbol = "BTC/USDT"
    budget = 10000
    risk_level = "moderate"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/auto-bot/create" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"

# Get Status
Invoke-RestMethod -Uri "http://localhost:8000/api/auto-bot/status"

# Start Bot (replace 1 with actual config_id)
Invoke-RestMethod -Uri "http://localhost:8000/api/auto-bot/start/1" `
  -Method Post

# Stop Bot
Invoke-RestMethod -Uri "http://localhost:8000/api/auto-bot/stop/1" `
  -Method Post
```

### Option C: Using cURL

```bash
# Create Config
curl -X POST http://localhost:8000/api/auto-bot/create \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Bot","symbol":"BTC/USDT","budget":10000,"risk_level":"moderate"}'

# Get Config
curl http://localhost:8000/api/auto-bot/config/1

# Start Bot
curl -X POST http://localhost:8000/api/auto-bot/start/1

# Get Status
curl http://localhost:8000/api/auto-bot/status

# Get Performance
curl http://localhost:8000/api/auto-bot/performance

# Stop Bot
curl -X POST http://localhost:8000/api/auto-bot/stop/1
```

---

## 🐛 Troubleshooting

### Issue: Navbar link not showing

**Check:**
- `ui/src/components/Navbar.tsx` has Brain icon import
- Route exists in `ui/src/App.tsx`
- Frontend dev server restarted

### Issue: No glow effect on God's Hand link

**Check:**
- `ui/src/index.css` has brainPulse animation
- Browser console for CSS errors
- Hard refresh browser (Ctrl + F5)

### Issue: AI modules showing 0%

**Check:**
- Bot is actually started (check status endpoint)
- Backend server is running
- No CORS errors in browser console
- Network tab shows successful polling requests

### Issue: Configuration not saving

**Check:**
- Backend server is running on port 8000
- Database initialized (`trading.db` exists)
- Browser console for error messages
- Network tab for failed POST requests

### Issue: Backend errors on start

**Check:**
```bash
# Check if AutoTrader import works
.venv311\Scripts\python.exe -c "from app.auto_trader import AutoTrader; print('OK')"

# Check if database is initialized
.venv311\Scripts\python.exe -c "from app.db import engine; from sqlalchemy import inspect; print(inspect(engine).get_table_names())"
```

---

## ✅ Success Criteria

All these should work without errors:

- [ ] Backend starts without errors
- [ ] Frontend loads at http://localhost:5173
- [ ] God's Hand link visible in navbar
- [ ] Brain icon pulses when active
- [ ] Configuration modal opens
- [ ] Configuration saves successfully
- [ ] Bot starts and shows AI modules
- [ ] AI modules update every 5 seconds
- [ ] Performance metrics display
- [ ] Bot stops successfully
- [ ] No console errors
- [ ] No network errors
- [ ] Database persists configurations

---

## 📸 Expected Screenshots

### 1. Navbar with God's Hand Link
```
[Trade] [Monitor] [Backtest] [🧠 God's Hand] [Settings]
                              ^^^^^^^^^^^^^^^^
                              (with glow effect when active)
```

### 2. God's Hand Page
```
┌─────────────────────────────────────────────┐
│  God's Hand - Auto Trading Bot              │
├─────────────────────────────────────────────┤
│                                              │
│  [Activate God's Hand]  [Stop God's Hand]   │
│                                              │
│  AI Module Status:                          │
│  🧠 Brain       ████████░  98%              │
│  🎯 Decision    ███████░░  95%              │
│  🤖 ML          ██████░░░  92%              │
│  ...                                        │
│                                              │
│  Performance:                                │
│  Total PnL: $125.50                         │
│  Total Trades: 10                           │
└─────────────────────────────────────────────┘
```

### 3. Configuration Modal
```
┌─────────────────────────────────────────────┐
│  ⚙️ Bot Configuration              [X]      │
├─────────────────────────────────────────────┤
│  Bot Name: [Test God Hand Bot          ]    │
│  Symbol:   [BTC/USDT ▼]                     │
│  Budget:   [10000                      ]    │
│  Risk:     ○ Conservative ● Moderate        │
│  Confidence: [━━━━━━━━━━] 70%              │
│                                              │
│  [Cancel]              [Save Configuration] │
└─────────────────────────────────────────────┘
```

---

## 🔄 Continuous Testing Loop

For ongoing development:

```bash
# Terminal 1: Backend (auto-reload)
.venv311\Scripts\python.exe -m uvicorn app.main:app --reload

# Terminal 2: Frontend (auto-reload)
cd ui && npm run dev

# Terminal 3: Watch logs
tail -f trading.log  # or check console output
```

**Workflow:**
1. Make changes to code
2. Save file
3. Server auto-reloads
4. Refresh browser
5. Test changes
6. Repeat

---

## 📝 Test Results Template

```
Date: ___________
Tester: _________

Backend Server:        [ ] Pass  [ ] Fail
Frontend Server:       [ ] Pass  [ ] Fail
Database Init:         [ ] Pass  [ ] Fail
Navigation:            [ ] Pass  [ ] Fail
Navbar Effects:        [ ] Pass  [ ] Fail
Config Modal:          [ ] Pass  [ ] Fail
Save Config:           [ ] Pass  [ ] Fail
Start Bot:             [ ] Pass  [ ] Fail
AI Modules Display:    [ ] Pass  [ ] Fail
Real-time Updates:     [ ] Pass  [ ] Fail
Stop Bot:              [ ] Pass  [ ] Fail
Performance Display:   [ ] Pass  [ ] Fail
API Endpoints:         [ ] Pass  [ ] Fail

Notes:
_____________________________________________
_____________________________________________
_____________________________________________
```

---

## 🎯 Next Steps After Testing

1. **If all tests pass:**
   - Deploy to staging environment
   - Conduct user acceptance testing
   - Monitor performance metrics

2. **If tests fail:**
   - Check error messages
   - Review troubleshooting section
   - Check browser/server console logs
   - Verify all files are saved
   - Restart servers

3. **Performance optimization:**
   - Monitor API response times
   - Check database query performance
   - Optimize frontend rendering
   - Consider WebSocket for real-time updates

---

## 📞 Support

If you encounter issues:

1. Check browser console (F12)
2. Check backend logs
3. Verify database state
4. Review recent code changes
5. Test with fresh database

---

**Happy Testing! 🚀**
