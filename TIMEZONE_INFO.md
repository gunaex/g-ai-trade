# Timezone Configuration

## Summary
All timestamps in the G-AI-Trade application now use **Server Local Time** for consistency.

## Changes Made

### Backend Changes

#### 1. **auto_trader.py** - Activity Logging
**File:** `app/auto_trader.py`

Changed from UTC to Server Local Time:
```python
# BEFORE (UTC)
"timestamp": datetime.utcnow().isoformat()

# AFTER (Server Local Time)
"timestamp": datetime.now().isoformat()
```

#### 2. **main.py** - Server Info Endpoint
**File:** `app/main.py`

Added new endpoint to expose server timezone information:
```python
@app.get("/api/server-info")
async def get_server_info():
    """
    Get server information including timezone
    All timestamps in this application use server local time
    """
    import time
    import platform
    
    now = datetime.now()
    timezone_offset = time.strftime("%z")
    timezone_name = time.tzname[time.daylight] if time.daylight else time.tzname[0]
    
    return {
        "server_time": now.isoformat(),
        "server_time_utc": datetime.utcnow().isoformat(),
        "timezone": timezone_name,
        "timezone_offset": timezone_offset,
        "timestamp_unix": int(now.timestamp()),
        "platform": platform.system(),
        "message": "All timestamps in this application use server local time"
    }
```

### Frontend Changes

#### 1. **ActivityLog.tsx** - Time Display
**File:** `ui/src/components/ActivityLog.tsx`

- Changed time format to 24-hour format
- Added "Server Time" indicator in footer

```typescript
// Time formatting with 24-hour format
const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit',
    hour12: false  // 24-hour format
  })
}

// Footer text
"Showing {activities.length} recent activities (Server Time)"
```

## Server Information

### Current Server Configuration
- **Timezone:** SE Asia Standard Time (GMT+7)
- **Timezone Offset:** +0700
- **Platform:** Windows

### Accessing Server Info
```bash
# Get server timezone information
curl http://localhost:8000/api/server-info

# Response:
{
  "server_time": "2025-11-02T21:17:53.609478",
  "server_time_utc": "2025-11-02T14:17:53.609478",
  "timezone": "SE Asia Standard Time",
  "timezone_offset": "+0700",
  "timestamp_unix": 1762093073,
  "platform": "Windows",
  "message": "All timestamps in this application use server local time"
}
```

## Impact on Application Components

### 1. Activity Log
- All activity timestamps are now in server local time
- Display format: 24-hour format (HH:MM:SS)
- Footer shows "(Server Time)" indicator

### 2. Trade Records
- Trade timestamps stored in database continue to use UTC (SQLAlchemy default)
- Display layer can convert to local time if needed

### 3. Bot Operations
- Start/Stop events logged with server local time
- Trading cycle timestamps use server local time
- Position monitoring uses server local time

## Benefits

1. **Consistency:** All logs and activities show the same timezone
2. **Clarity:** Users see time in the server's timezone context
3. **Transparency:** `/api/server-info` endpoint provides timezone details
4. **Simplicity:** No timezone conversion needed for activity logs

## Notes for Future Development

### If deploying to different timezone:
1. Server info endpoint will automatically reflect new timezone
2. Activity logs will use the new server's local time
3. No code changes needed - all automatic

### If you need to convert to user's local timezone:
Frontend can convert timestamps:
```typescript
const userLocalTime = new Date(serverTimestamp).toLocaleTimeString()
```

## Verification

To verify timezone is working correctly:

```bash
# 1. Check server info
curl http://localhost:8000/api/server-info

# 2. Start bot and check activity log timestamps
curl http://localhost:8000/api/auto-bot/status | python -m json.tool

# 3. Compare activity timestamp with server_time
# They should be in the same timezone
```

## Database Considerations

**Important:** Database timestamps (`Trade.timestamp`, `BotConfig.created_at`, etc.) still use UTC as this is SQLAlchemy's default:

```python
# models.py
timestamp = Column(DateTime, default=datetime.utcnow)
```

This is intentional:
- ✅ **Database:** UTC (universal standard for storage)
- ✅ **Activity Logs:** Server Local Time (for real-time monitoring)
- ✅ **Display:** Can be converted to any timezone as needed

---

**Last Updated:** November 2, 2025  
**Version:** 1.0.0
