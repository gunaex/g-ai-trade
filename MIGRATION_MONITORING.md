# Migration Deployment - Monitor Progress

## What Just Happened

Pushed code that will **automatically run the database migration** when Render deploys.

The migration adds the `paper_trading` column to your production database.

## Monitor Deployment Progress

### 1. Watch Render Deploy
Go to: https://dashboard.render.com

You should see:
- 🟡 **Deploying** - Building new version
- ⏳ Takes ~5-10 minutes
- 🟢 **Live** - Deployment successful

### 2. Check Logs for Migration Success

In Render dashboard → Your service → Logs

Look for these messages:
```
INFO:app.main:Initializing database...
INFO:app.main:Database initialized successfully
INFO:app.migrations:Running database migrations...
INFO:app.migrations:Adding 'paper_trading' column to bot_configs table...
INFO:app.migrations:✅ Successfully added paper_trading column
INFO:app.migrations:⚠️  All existing configs set to PAPER TRADING mode (safe default)
INFO:app.migrations:✅ All migrations completed successfully
```

### 3. Test Your App

After seeing "✅ All migrations completed successfully" in logs:

1. **Refresh your app** in browser
2. **Check console** - should see `paper_trading: true` in config
3. **No more 500 errors** on status endpoint
4. **Config persists** - save Config 28, it stays as 28 (not reverting to 22)

### 4. Verify Paper Trading UI

Open God's Hand modal → Advanced Settings

Should see:
```
📝 Paper (Simulated) - Risk-free testing with simulated orders
```

## If Something Goes Wrong

### Migration Already Exists
If you see:
```
✅ Column 'paper_trading' already exists - skipping
```
**This is fine!** It means the column is already there.

### Database Error
If you see:
```
❌ Migration failed: ...
```

Check:
1. DATABASE_URL is set correctly in Render environment variables
2. Database service is running
3. App still starts (migration errors don't crash the app)

### Still Getting 500 Errors

1. Wait 2-3 minutes after deploy completes
2. Hard refresh browser (Ctrl + Shift + R)
3. Check Render logs for specific error
4. Let me know what error you see

## Expected Timeline

- **Now**: Code pushed to GitHub ✅
- **~2 min**: Render detects new commit and starts build
- **~5 min**: Build completes, starts deployment
- **~7 min**: Migration runs during startup
- **~8 min**: App is live with paper_trading column ✅

## Success Indicators

✅ Render shows "Live" status  
✅ Logs show migration success messages  
✅ No 500 errors in app  
✅ Console shows `paper_trading: true`  
✅ UI displays paper trading mode  
✅ Config ID 28 persists (doesn't revert to 22)  

## Next Steps After Success

1. Test saving new config
2. Verify paper trading toggle works
3. Confirm config doesn't revert after 5 seconds
4. Consider extending guard to 30s or making permanent while modal open
