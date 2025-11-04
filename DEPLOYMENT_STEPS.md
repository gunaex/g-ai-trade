# Deployment Steps to Fix Config & Paper Trading Issues

## Problem Summary
- Backend returns Config ID 22 instead of ID 28 (latest)
- `paper_trading` field not visible in UI
- Root cause: Render hasn't deployed latest code OR database migration not run

## Fix Steps

### 1. Verify Render Deployment

1. Go to: https://dashboard.render.com
2. Find your backend service: `g-ai-trade-backend`
3. Check "Events" or "Deploys" tab
4. **Current commit should be**: `f998492` or later
5. If it shows older commit:
   - Click "Manual Deploy" → "Deploy latest commit"
   - Wait for deployment to complete (5-10 min)

### 2. Run Database Migration on Render

**Option A: Via Render Shell**
1. In Render dashboard → Your service → "Shell" tab
2. Run:
   ```bash
   python add_paper_trading_column.py
   ```
3. Should see:
   ```
   ✅ Successfully added paper_trading column
   ⚠️  All existing configs set to PAPER TRADING mode
   ```

**Option B: Via Local Connection**
If you have production database URL:
```bash
# Set DATABASE_URL environment variable
set DATABASE_URL=postgresql://user:pass@host/db

# Run migration
python add_paper_trading_column.py
```

### 3. Verify Fixes

**Test Backend Directly:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://g-ai-trade-backend.onrender.com/api/auto-bot/status
```

Should return:
```json
{
  "config": {
    "id": 28,
    "symbol": "ETH/USDT",
    "budget": 10000,
    "paper_trading": true,  ← Should be present
    ...
  }
}
```

**Test in UI:**
1. Save a new config (ETH/USDT, budget 10000, paper trading ON)
2. Note the config ID in console
3. Wait 10 seconds (let guard expire)
4. Check console - should still show same config ID
5. ConfigDisplay should show "📝 Paper (Simulated)" in Advanced Settings

### 4. If Issues Persist

**Check Database Column:**
```sql
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'bot_configs'
ORDER BY ordinal_position;
```

Should include:
```
paper_trading | boolean | true
```

**Check Latest Config:**
```sql
SELECT id, symbol, budget, paper_trading, created_at
FROM bot_configs
WHERE user_id = YOUR_USER_ID
ORDER BY id DESC
LIMIT 5;
```

Should show Config 28 at top with `paper_trading = true`.

## Expected Results

✅ Backend returns highest config ID (28, not 22)  
✅ Console logs show `paper_trading: true` in config object  
✅ UI displays "📝 Paper (Simulated)" in Advanced Settings  
✅ Guard no longer needed (backend returns correct config)  
✅ Saved configs persist across page refreshes  

## Rollback (if needed)

If deployment breaks something:

1. Render Dashboard → Deploys → Find previous working deploy
2. Click "Redeploy" on that older version
3. Report issues in conversation for debugging

## Next Steps After Deployment

1. **Extend guard duration**: Change from 5s to 30s or make permanent while modal open
2. **Add prominent indicator**: Show paper/live mode in header banner
3. **Implement UPDATE endpoint**: PUT /api/auto-bot/config/{id} to avoid ID proliferation
4. **Remove debug logging**: Clean up console.log statements after verification
