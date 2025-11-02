# 🚀 Production Deployment Checklist

## ✅ Code Quality - COMPLETED
- [x] No console.log statements in frontend (cleaned)
- [x] Proper logging with logger instead of print() in critical paths
- [x] TypeScript errors resolved
- [x] All components have proper type definitions

## ⚠️ Security - ACTION REQUIRED

### **CRITICAL - Before Deployment:**

1. **Generate New SECRET_KEY** (Currently using placeholder)
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```
   Update `.env` with generated key

2. **Secure API Keys**
   - [x] `.env` file is in `.gitignore` ✓
   - [ ] **VERIFY**: Never commit `.env` to repository
   - [ ] Use environment variables in production server
   - [ ] Rotate Binance API keys if exposed

3. **Environment Configuration**
   - [ ] Change `ENVIRONMENT=production` in production `.env`
   - [ ] Set up proper CORS origins (currently allows `*`)
   - [ ] Configure proper database path for production

## 🗄️ Database

- [x] SQLite database configured
- [ ] **Backup strategy**: Set up daily backups
- [ ] **Migration plan**: Document schema if changes needed
- Database file: `g_ai_trade.db` (gitignored ✓)

## 🔧 Configuration Files

### Backend (`app/main.py`)
- [x] Logging configured properly
- [ ] **Update CORS**: Change from `allow_origins=["*"]` to specific domains
  ```python
  allow_origins=["https://yourdomain.com", "https://www.yourdomain.com"]
  ```

### Frontend Build
- [x] TypeScript configured
- [x] Production build script ready: `npm run build`
- [ ] Test build: `cd ui && npm run build`

## 📦 Dependencies

### Python Requirements
- [x] All dependencies in `requirements.txt`
- [x] `nest-asyncio` included (fixes import error)
- [ ] Run: `pip install -r requirements.txt`

### Node.js Dependencies
- [x] All dependencies in `package.json`
- [ ] Run: `cd ui && npm install`

## 🧪 Pre-Deployment Testing

### Backend Tests
```bash
# Test server startup
python -m uvicorn app.main:app --reload

# Test endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/api/server-info
```

### Frontend Tests
```bash
cd ui
npm run build
npm run preview
```

### Integration Tests
- [ ] Test bot start/stop functionality
- [ ] Verify Activity Log displays correctly
- [ ] Check Performance Dashboard
- [ ] Test timezone display (should show server time)

## 🌐 Deployment Steps

### 1. Prepare Production Environment
```bash
# Clone repository
git clone https://github.com/gunaex/g-ai-trade.git
cd g-ai-trade

# Set up Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install TA-Lib (if needed)
pip install ta_lib-0.6.8-cp311-cp311-win_amd64.whl
```

### 2. Configure Environment
```bash
# Copy and configure .env
cp .env.example .env  # Create this from your current .env
# Edit .env with production values
nano .env
```

**Required `.env` values:**
```properties
BINANCE_API_KEY=<your_production_api_key>
BINANCE_SECRET=<your_production_secret>
DATABASE_URL=sqlite:///./g_ai_trade.db
SECRET_KEY=<generated_64_char_key>
ENVIRONMENT=production
BINANCE_REGION=th
```

### 3. Build Frontend
```bash
cd ui
npm install
npm run build
cd ..
```

### 4. Initialize Database
```bash
python app/init_db.py
```

### 5. Start Application

**Option A: Direct (Development/Testing)**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Option B: Production (with Gunicorn)**
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Option C: Windows Service / Screen / PM2**
```bash
# Using PM2 (recommended)
npm install -g pm2
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name g-ai-trade
pm2 save
pm2 startup
```

### 6. Serve Frontend
- Frontend is served from `/dist` directory automatically by FastAPI
- Static files mounted at `/assets`

### 7. Set Up Reverse Proxy (Optional but Recommended)

**Nginx Configuration Example:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://localhost:8000/api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔒 Security Hardening

### Immediate Actions:
1. **Change CORS policy** in `app/main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],  # Specific domain only
       allow_credentials=True,
       allow_methods=["GET", "POST", "DELETE"],
       allow_headers=["*"],
   )
   ```

2. **Add rate limiting** (recommended):
   ```bash
   pip install slowapi
   ```

3. **Enable HTTPS** (use Let's Encrypt + Nginx)

4. **Firewall rules**:
   - Only allow ports 80, 443 (if using Nginx)
   - Or only 8000 if direct access
   - Block all other inbound traffic

## 📊 Monitoring

### Set Up Logging
- [x] Application logs to console
- [ ] Configure log rotation
- [ ] Set up error alerting (email/Telegram)

### Health Checks
- Endpoint: `GET /api/health`
- Monitor: Every 1-5 minutes
- Alert if: Returns error or > 1 second response time

### Database Backups
```bash
# Daily backup cron job
0 2 * * * cp /path/to/g_ai_trade.db /path/to/backups/g_ai_trade_$(date +\%Y\%m\%d).db
```

## 🐛 Known Issues & Limitations

1. **TODO Comments** (Non-blocking, future features):
   - Telegram notifications (line 456-458 in `auto_trader.py`)
   - Task queue for long backtests (line 663 in `main.py`)
   - Proper PnL tracking in backtesting (line 565 in `backtesting_engine.py`)

2. **Print Statements** (Acceptable for CLI tools):
   - `init_db.py` - Initialization output
   - `backtesting_engine.py` - Tear sheet output
   - `crypto.py` - Demo output (only runs in `__main__`)

3. **API Response Type Safety**:
   - `AUTO_BOT_API_EXAMPLES.tsx` has type unknown (example file, not used in production)

## ✅ Final Verification

Before going live, verify:
- [ ] Build completes without errors: `cd ui && npm run build`
- [ ] Server starts: `uvicorn app.main:app`
- [ ] Health endpoint works: `curl http://localhost:8000/api/health`
- [ ] Database initialized: `python app/init_db.py`
- [ ] Frontend accessible: Visit `http://localhost:8000`
- [ ] Bot can start and stop
- [ ] Activity logs display correctly
- [ ] No sensitive data in logs
- [ ] `.env` file not in git
- [ ] SECRET_KEY is production-ready (not placeholder)
- [ ] CORS configured for production domain

## 🎯 Post-Deployment

1. **Monitor First 24 Hours**
   - Check error logs
   - Monitor API response times
   - Verify bot executes trades correctly
   - Watch for memory leaks

2. **Set Up Alerts**
   - Trading errors
   - API failures
   - Database connection issues
   - Disk space warnings

3. **Document Runbook**
   - How to restart service
   - How to check logs
   - Emergency stop procedure
   - Rollback plan

## 🚨 Emergency Contacts

- Repository: https://github.com/gunaex/g-ai-trade
- Binance Support: [Link to support]
- Server Admin: [Contact info]

---

**Last Updated:** 2025-11-03
**Version:** 1.0.0
**Deployment Ready:** ✅ (after completing security actions)
