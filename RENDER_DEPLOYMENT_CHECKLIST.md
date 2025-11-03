# Render Deployment Verification Checklist

## 📋 Step-by-Step Verification

### Step 1: Check Render Deployment Status

1. **Go to Render Dashboard**:
   - Visit: https://dashboard.render.com
   - Navigate to your `g-ai-trade-backend` service

2. **Check Latest Deploy**:
   - Look for the latest commit: "feat: Add JWT authentication system"
   - Status should show: "Live" (green)
   - If still deploying: Wait for it to complete (usually 3-5 minutes)

3. **Check Deploy Logs**:
   - Click on "Logs" tab
   - Look for successful installation messages:
     ```
     Installing python-jose[cryptography]==3.3.0
     Installing passlib[bcrypt]==1.7.4
     Installing bcrypt==4.0.1
     Installing email-validator==2.3.0
     Successfully installed ...
     ```

### Step 2: Add/Verify Environment Variables

**Required Environment Variables:**

1. Go to: **Dashboard → Your Service → Environment**

2. **Add/Verify these variables**:

   ```bash
   # JWT Authentication (NEW - CRITICAL!)
   JWT_SECRET_KEY=7LD_8grlnUAd_ikDBAh48F71c4sZlEz6ebwoisKSFec
   
   # Existing variables (verify these exist)
   BINANCE_API_KEY=your_binance_api_key
   BINANCE_SECRET=your_binance_secret
   DATABASE_URL=your_postgresql_url
   ENVIRONMENT=production
   
   # CORS (UPDATE THIS!)
   ALLOWED_ORIGINS=https://g-ai-trade.vercel.app
   ```

3. **After adding JWT_SECRET_KEY**:
   - Click "Save Changes"
   - Render will automatically redeploy
   - Wait 2-3 minutes for redeployment

### Step 3: Test Backend Endpoints

**Test 1: Health Check** (No auth required)
```bash
curl https://g-ai-trade-backend.onrender.com/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-03T...",
  "version": "1.0.0"
}
```

---

**Test 2: Register Endpoint** (New - requires JWT setup)
```bash
curl -X POST https://g-ai-trade-backend.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser\",\"email\":\"test@example.com\",\"password\":\"test123\"}"
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "is_active": true,
    "is_admin": false
  }
}
```

**Error Response (if JWT_SECRET_KEY missing):**
```json
{
  "detail": "Internal server error"
}
```

---

**Test 3: Login Endpoint**
```bash
curl -X POST https://g-ai-trade-backend.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser\",\"password\":\"test123\"}"
```

---

**Test 4: Get Current User** (Protected - requires token)
```bash
# First get token from login/register, then:
curl https://g-ai-trade-backend.onrender.com/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### Step 4: Check Database

1. **Verify Users Table Created**:
   - Go to Render Dashboard → Database
   - Connect to PostgreSQL
   - Run: `\dt` to list tables
   - Should see: `users` table

2. **Check Table Schema**:
   ```sql
   \d users
   ```
   
   Should show columns:
   - id (primary key)
   - username (unique)
   - email (unique)
   - hashed_password
   - is_active
   - is_admin
   - created_at
   - last_login

### Step 5: Common Issues & Solutions

#### Issue 1: "Module 'jose' not found"
**Solution**: 
- Dependencies not installed
- Check deploy logs for errors
- Verify `requirements-prod.txt` was pushed

#### Issue 2: "Could not validate credentials"
**Solution**:
- `JWT_SECRET_KEY` not set in environment variables
- Add it in Render dashboard → Environment

#### Issue 3: "404 Not Found" on /api/auth/register
**Solution**:
- Code not deployed yet
- Check Render deploy status
- Check for deploy errors in logs

#### Issue 4: "email-validator not installed"
**Solution**:
- Already fixed in requirements-prod.txt
- Redeploy should install it automatically

#### Issue 5: Database connection errors
**Solution**:
- Verify `DATABASE_URL` is set correctly
- Check PostgreSQL service is running
- Verify database credentials

### Step 6: Frontend Configuration

1. **Verify API URL in Frontend**:
   ```typescript
   // ui/src/lib/api.ts
   const API_BASE = 'https://g-ai-trade-backend.onrender.com/api'
   ```

2. **Update Vercel Environment Variables** (if needed):
   ```bash
   VITE_API_URL=https://g-ai-trade-backend.onrender.com/api
   ```

3. **Redeploy Frontend**:
   - Vercel auto-deploys on git push
   - Or manually: Dashboard → Deployments → Redeploy

### Step 7: End-to-End Test

1. **Open Frontend**: https://g-ai-trade.vercel.app/login
2. **Register**: Create a new account
3. **Login**: Login with credentials
4. **Navigate**: Go to /trade page
5. **Verify**: Should not redirect to login

---

## ✅ Success Criteria

- [ ] Render shows "Live" status
- [ ] Health check returns 200
- [ ] Register endpoint returns tokens
- [ ] Login endpoint returns tokens
- [ ] Protected endpoints require auth
- [ ] Frontend login/register works
- [ ] Users table exists in database
- [ ] No errors in Render logs

---

## 🔧 Quick Commands for Testing

**Windows (PowerShell):**
```powershell
# Health check
Invoke-WebRequest -Uri "https://g-ai-trade-backend.onrender.com/api/health"

# Register
$body = @{username="admin";email="admin@example.com";password="admin123"} | ConvertTo-Json
Invoke-WebRequest -Uri "https://g-ai-trade-backend.onrender.com/api/auth/register" -Method POST -Body $body -ContentType "application/json"
```

**Windows (curl):**
```bash
curl https://g-ai-trade-backend.onrender.com/api/health

curl -X POST https://g-ai-trade-backend.onrender.com/api/auth/register -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"email\":\"admin@example.com\",\"password\":\"admin123\"}"
```

---

## 📞 Need Help?

If you encounter issues:

1. **Share Render Deploy Logs**: Copy the last 50 lines from Render logs
2. **Share Error Response**: Copy the exact error message
3. **Check Environment Variables**: Verify all required vars are set

**Next Steps After Verification:**
1. ✅ Verify deployment is live
2. ✅ Add JWT_SECRET_KEY to Render
3. ✅ Test all endpoints
4. ✅ Create first admin user
5. ✅ Update frontend CORS
6. ✅ Test end-to-end flow
