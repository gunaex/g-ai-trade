# God's Hand Configuration Persistence Fix

## Problem Description

User reported 3 issues with God's Hand configuration:

1. ✅ **Save shows success message** - This was working
2. ❌ **Configuration not displayed** in "Current Configuration" card
3. ❌ **Config modal resets to initial values** when reopened after save

## Root Cause Analysis

### Issue 1: Config Not Displaying

**Problem:**
```
1. User saves config → Shows success toast ✅
2. Backend saves config to database ✅
3. Frontend fetches saved config and displays it ✅
4. After 2 seconds, polling calls fetchBotStatus() ❌
5. Backend returns config: null (because bot not running) ❌
6. Frontend overwrites saved config with null ❌
7. Config card disappears ❌
```

**Why backend returned null:**
```python
# OLD CODE (app/main.py):
if not auto_trader_instance:
    return {
        "config": None,  # ❌ No config returned!
        # ... other fields
    }
```

The status endpoint only returned config when:
- Bot was running (`auto_trader_instance` exists)
- AND the bot instance had a config loaded

**But when you just save a config:**
- Bot is NOT running yet
- `auto_trader_instance` is `None`
- Status returns `config: null`
- Polling overwrites the saved config in UI state

### Issue 2: Config Modal Resets

**Problem:**
```tsx
// OLD CODE (GodsHand.tsx):
initialConfig={botStatus?.config ? {
  name: (botStatus.config as any).name,
  // ... extract values from botStatus.config
} : undefined}
```

When `botStatus.config` is `null` (after polling overwrites it):
- `initialConfig` becomes `undefined`
- Modal uses default hardcoded values
- User's saved settings are not shown

## Solutions Implemented

### Backend Fix 1: Always Return User's Latest Config

**File:** `app/main.py`

**Change:**
```python
# NEW CODE:
try:
    # ✅ Always try to load user's most recent config
    latest_config = db.query(BotConfig).filter(
        BotConfig.user_id == current_user["user_id"]
    ).order_by(BotConfig.created_at.desc()).first()
    
    if not auto_trader_instance:
        # No instance, but return user's saved config if exists
        return {
            "config": latest_config.to_dict() if latest_config else None,
            # ✅ Now returns saved config even when bot not running!
            # ...
        }
```

**What this does:**
- Queries database for user's most recent `BotConfig`
- Returns it even when bot is not running
- User always sees their latest saved configuration

### Backend Fix 2: Fallback to Latest Config When Bot Stopped

```python
if not auto_trader_instance.is_running:
    # ✅ Use bot's config if available, otherwise user's latest saved config
    config = auto_trader_instance.config.to_dict() if auto_trader_instance.config else (latest_config.to_dict() if latest_config else None)
    return {
        "config": config,
        # ...
    }
```

**What this does:**
- If bot was running and stopped, show the bot's config
- If no bot config, fallback to user's latest saved config
- Ensures config is never `null` when user has saved configs

### Frontend Fix: Preserve Config in State

**File:** `ui/src/pages/GodsHand.tsx`

**Change:**
```tsx
const fetchBotStatus = async () => {
  const response = await apiClient.getAutoBotStatus()
  const newConfig = response.data.config
  
  setBotStatus(prev => ({
    ...response.data,
    // ✅ Keep existing config if new one is null and we already have one
    config: newConfig || prev?.config || null,
  }))
}
```

**What this does:**
- If API returns `config: null`, don't overwrite existing config
- Preserves user's saved config across polling cycles
- Only updates config when API actually returns a new one

## Flow After Fix

### Successful Save Flow:

```
1. User fills config form and clicks "Save Configuration"
   ↓
2. POST /api/auto-bot/create → Creates config in database ✅
   Response: { config_id: 5 }
   ↓
3. Frontend fetches saved config: GET /api/auto-bot/config/5 ✅
   Response: { id: 5, name: "God's Hand Bot", budget: 10000, ... }
   ↓
4. Frontend updates botStatus.config ✅
   ↓
5. Config card appears with saved values ✅
   ↓
6. Polling calls /api/auto-bot/status (every 2 seconds) ✅
   Backend returns: { config: { id: 5, name: "God's Hand Bot", ... } } ✅
   ↓
7. Frontend preserves config (doesn't overwrite) ✅
   ↓
8. Config card remains visible ✅
```

### Reopening Config Modal:

```
1. User clicks "Configure" button
   ↓
2. Modal opens with initialConfig from botStatus.config ✅
   ↓
3. All saved values are pre-filled ✅
   (name, symbol, budget, risk_level, min_confidence, etc.)
   ↓
4. User can edit and save again ✅
```

## Testing Steps

### Test 1: Save Config and Verify Display

1. **Open God's Hand page**
2. **Click "Configure" button**
3. **Fill in custom values:**
   - Name: "My Custom Bot"
   - Symbol: ETH/USDT
   - Budget: 5000
   - Risk Level: Aggressive
   - Min Confidence: 80%
   - Position Size: 90%
   - Max Daily Loss: 3%
4. **Click "Save Configuration"**
5. **Expected Results:**
   - ✅ Toast shows "Configuration saved (ID #X)"
   - ✅ Modal closes
   - ✅ "Current Configuration" card appears
   - ✅ Shows: ETH/USDT, $5,000, Aggressive, 80%, etc.
   - ✅ Card stays visible (doesn't disappear after 2 seconds)

### Test 2: Reopen Config Modal

1. **After saving config (from Test 1)**
2. **Click "Configure" button again**
3. **Expected Results:**
   - ✅ Modal shows "My Custom Bot"
   - ✅ Symbol: ETH/USDT
   - ✅ Budget: 5000
   - ✅ Risk: Aggressive selected
   - ✅ All sliders at saved positions
   - ✅ NOT showing default values

### Test 3: Multiple Saves

1. **Save config #1** (BTC/USDT, $10,000)
2. **Verify it displays** ✅
3. **Save config #2** (ETH/USDT, $5,000)
4. **Expected Results:**
   - ✅ Shows latest config (ETH/USDT, $5,000)
   - ✅ Both configs exist in database
   - ✅ Status endpoint returns most recent

### Test 4: Refresh Page

1. **Save a config**
2. **Refresh browser (F5)**
3. **Expected Results:**
   - ✅ Config card reappears after page load
   - ✅ Shows saved values
   - ✅ Clicking Configure shows saved values

## Database Schema

No changes needed. Existing schema already supports this:

```sql
CREATE TABLE bot_configs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,           -- ✅ Filter by user
    name VARCHAR,
    symbol VARCHAR,
    budget FLOAT,
    risk_level VARCHAR,
    min_confidence FLOAT,
    position_size_ratio FLOAT,
    max_daily_loss FLOAT,
    is_active BOOLEAN,
    created_at TIMESTAMP,      -- ✅ Order by this to get latest
    updated_at TIMESTAMP
);
```

## API Changes Summary

### GET /api/auto-bot/status

**Before:**
```json
// When bot not running:
{
  "is_running": false,
  "config": null  // ❌ Always null
}
```

**After:**
```json
// When bot not running but user has saved config:
{
  "is_running": false,
  "config": {
    "id": 5,
    "name": "God's Hand Bot",
    "symbol": "ETH/USDT",
    "budget": 5000,
    // ... all saved values ✅
  }
}
```

## Files Changed

1. **app/main.py** (Backend)
   - Modified `get_auto_bot_status()` endpoint
   - Added query for user's latest config
   - Returns config even when bot not running

2. **ui/src/pages/GodsHand.tsx** (Frontend)
   - Modified `fetchBotStatus()` to preserve config
   - Prevents config from being overwritten by null

## Commit

```
fix(gods-hand): persist saved config in UI and show user's latest config

Backend changes:
- GET /api/auto-bot/status now returns user's latest saved config even when bot not running
- Queries BotConfig by user_id ordered by created_at desc
- Ensures saved configs are always visible to users

Frontend changes:
- fetchBotStatus preserves existing config if API returns null
- Prevents config from being overwritten by polling
- Config modal now shows saved values when reopened
- Current Configuration card displays immediately after save

Fixes issue where:
- Saved config disappeared after polling
- Config modal showed default values instead of saved values
- Current Configuration card was not visible after save
```

## Next Steps

After deploying this fix:

1. **Test in production** that configs persist
2. **Verify modal shows saved values** when reopened
3. **Consider adding** a "Load Config" dropdown to select from multiple saved configs
4. **Consider adding** a "Delete Config" button for unwanted configs

## Related Issues

This fix also resolves:
- Config card disappearing after page refresh
- Multiple users each seeing their own configs (due to `user_id` filter)
- Config persistence across bot start/stop cycles
