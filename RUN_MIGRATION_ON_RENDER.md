# Run Database Migration on Render

## The Problem
Backend deployed successfully ✅  
But database column `paper_trading` doesn't exist ❌

Error:
```
column bot_configs.paper_trading does not exist
```

## Solution: Run Migration on Render

### Option 1: Via Render Shell (Recommended)

1. Go to: https://dashboard.render.com
2. Find your service: `g-ai-trade-backend`
3. Click "Shell" tab (in the left sidebar)
4. Wait for shell to connect
5. Run:
   ```bash
   python add_paper_trading_column.py
   ```
6. You should see:
   ```
   ============================================================
   DATABASE MIGRATION: Add Paper Trading Support
   ============================================================
   
   Adding 'paper_trading' column to bot_configs table...
   ✅ Successfully added paper_trading column
   ⚠️  All existing configs set to PAPER TRADING mode (safe default)
   
   ============================================================
   Migration complete!
   ============================================================
   ```

### Option 2: Via Render One-Off Job

If Shell tab isn't available:

1. In Render dashboard → Your service
2. Go to "Jobs" tab
3. Click "Create Job"
4. Enter command: `python add_paper_trading_column.py`
5. Click "Run"

### Option 3: Add to Render Build Command

To run migrations automatically on every deploy:

1. Render dashboard → Your service → Settings
2. Find "Build Command" section
3. Change to:
   ```bash
   pip install -r requirements.txt && python add_paper_trading_column.py
   ```
4. Click "Save Changes"
5. Next deploy will auto-run migration

**Note:** Migration script is safe to run multiple times - it checks if column exists first.

## Verify Migration Worked

After running migration, check your app logs:

1. Render dashboard → Your service → Logs
2. Refresh your app in browser
3. Should see successful status poll instead of 500 error
4. Console should show `paper_trading: true` in config object

## If You Get Database Connection Error

Make sure `DATABASE_URL` environment variable is set in Render:

1. Render dashboard → Your service → Environment
2. Should see: `DATABASE_URL = postgresql://...`
3. If missing, add it from your PostgreSQL service

## After Migration Succeeds

Your app should now:
- ✅ Return correct config (ID 28 instead of 22)
- ✅ Include `paper_trading: true` in API responses
- ✅ Display "📝 Paper (Simulated)" in UI
- ✅ No more 500 errors on status endpoint
