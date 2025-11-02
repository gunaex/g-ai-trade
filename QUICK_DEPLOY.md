# 🚀 Quick Deployment Guide

## Before You Start (5 minutes)

### 1. Generate SECRET_KEY
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Copy the output and update `.env`:
```properties
SECRET_KEY=<paste_generated_key_here>
```

### 2. Configure Environment
Edit `.env`:
```properties
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
BINANCE_API_KEY=<your_production_api_key>
BINANCE_SECRET=<your_production_secret>
```

### 3. Build Frontend
```bash
cd ui
npm install
npm run build
cd ..
```

---

## Deploy (3 commands)

### Windows
```batch
start_production.bat
```

### Linux/Mac
```bash
chmod +x start_production.sh
./start_production.sh
```

### Manual
```bash
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app/init_db.py
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Verify (3 checks)

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```
Expected: `{"status": "healthy", ...}`

### 2. Server Info
```bash
curl http://localhost:8000/api/server-info
```
Expected: `{"server_time": ..., "timezone": ...}`

### 3. Open Browser
Visit: `http://localhost:8000`

---

## Security Checklist

- [ ] SECRET_KEY is NOT `generate-random-64-char-secret-key-here`
- [ ] ENVIRONMENT is `production`
- [ ] ALLOWED_ORIGINS matches your domain
- [ ] `.env` file is NOT in git
- [ ] Binance API has IP whitelist enabled

---

## Emergency Stop

```bash
# Press Ctrl+C in the terminal

# Or find and kill the process:
# Windows
taskkill /F /IM python.exe

# Linux/Mac
pkill -f uvicorn
```

---

## Monitoring

### Logs
- Watch logs: `tail -f /path/to/app.log`
- Error count: `grep ERROR app.log | wc -l`

### Performance
- Health: `GET /api/health`
- Status: `GET /api/auto-bot/status`
- Performance: `GET /api/performance/today`

---

## Troubleshooting

### "Port already in use"
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Database error"
```bash
python app/init_db.py
```

### "CORS error"
Update `ALLOWED_ORIGINS` in `.env` to include your domain

---

## Production Setup (Recommended)

### 1. Use Gunicorn (Linux/Mac)
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 2. Use PM2 (All platforms)
```bash
npm install -g pm2
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name g-ai-trade
pm2 save
pm2 startup
```

### 3. Use Systemd (Linux)
Create `/etc/systemd/system/g-ai-trade.service`:
```ini
[Unit]
Description=G-AI-TRADE Service
After=network.target

[Service]
Type=notify
User=youruser
WorkingDirectory=/path/to/g-ai-trade
Environment="PATH=/path/to/g-ai-trade/.venv/bin"
ExecStart=/path/to/g-ai-trade/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable g-ai-trade
sudo systemctl start g-ai-trade
sudo systemctl status g-ai-trade
```

---

## Backup Strategy

### Database Backup (Daily)
```bash
# Linux/Mac cron
0 2 * * * cp /path/to/g_ai_trade.db /path/to/backups/g_ai_trade_$(date +\%Y\%m\%d).db

# Windows Task Scheduler
xcopy g_ai_trade.db backups\g_ai_trade_%date%.db
```

### Restore
```bash
cp backups/g_ai_trade_YYYYMMDD.db g_ai_trade.db
```

---

## Need Help?

- Full Guide: See `DEPLOYMENT_CHECKLIST.md`
- Cleanup Details: See `CLEANUP_SUMMARY.md`
- Code Changes: See `CHANGELOG.md`
- Timezone Info: See `TIMEZONE_INFO.md`

---

**You're ready to deploy! 🎉**

Last updated: 2025-11-03
