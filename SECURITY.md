# Security Best Practices for G-AI-TRADE

## 🔒 Overview

This document outlines security measures implemented in G-AI-TRADE and best practices for deployment.

## ✅ Implemented Security Features

### 1. JWT Authentication

**What it does**:
- Protects all trading and bot management endpoints
- Uses industry-standard JWT (JSON Web Tokens)
- Implements token refresh mechanism for seamless UX

**How it works**:
- Access tokens expire after 30 minutes (short-lived)
- Refresh tokens expire after 7 days (longer-lived)
- Automatic token refresh on expiration
- Bearer token authentication in HTTP headers

**Configuration**:
```bash
# .env
JWT_SECRET_KEY=your-super-secret-key-here
```

**Protected Endpoints**:
- POST `/api/trade` - Execute trades
- POST `/api/grid-bot/{symbol}` - Grid trading bot
- POST `/api/dca-bot/{symbol}` - DCA bot
- POST `/api/auto-bot/*` - Auto trading bot management

### 2. Password Security

**Hashing Algorithm**: bcrypt
- Industry-standard password hashing
- Automatic salt generation
- Computationally expensive (prevents brute force)
- One-way hashing (cannot be reversed)

**Password Requirements**:
- Minimum length: 6 characters
- Recommended: 12+ characters with mix of uppercase, lowercase, numbers, symbols

**Best Practices**:
```python
# ✅ Good password
"MyTr@d1ngB0t2025!"

# ❌ Bad password
"123456"
"password"
"admin"
```

### 3. CORS (Cross-Origin Resource Sharing)

**Purpose**: Prevent unauthorized websites from accessing your API

**Configuration**:
```python
# Development (allows all origins)
ENVIRONMENT=development

# Production (strict origin control)
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-app.vercel.app,https://www.yourdomain.com
```

**Security**:
- Blocks requests from unauthorized domains
- Prevents CSRF attacks
- Protects user data from malicious sites

### 4. API Key Protection

**Binance API Keys**:
- Stored in `.env` file (NEVER in code)
- `.env` excluded from git via `.gitignore`
- Encrypted at rest (recommended for production)

**Best Practices**:
```bash
# ✅ Correct - in .env file
BINANCE_API_KEY=your_api_key
BINANCE_SECRET=your_api_secret

# ❌ Wrong - hardcoded in code
api_key = "abc123..."  # NEVER DO THIS
```

### 5. Database Security

**User Data**:
- Passwords are NEVER stored in plain text
- All passwords hashed with bcrypt
- User sessions managed via JWT tokens

**SQL Injection Prevention**:
- Using SQLAlchemy ORM (parameterized queries)
- Input validation on all endpoints
- Type checking with Pydantic models

### 6. HTTPS Enforcement

**Production Requirements**:
- All traffic MUST use HTTPS
- JWT tokens sent only over encrypted connections
- Render and Vercel enforce HTTPS by default

**Why it matters**:
```
HTTP  ❌  → JWT visible in plain text → Can be intercepted
HTTPS ✅  → JWT encrypted in transit → Cannot be intercepted
```

## 🚨 Attack Prevention

### 1. Brute Force Attacks

**Current Protection**:
- Password hashing makes brute force computationally expensive
- JWT tokens expire (limits attack window)

**Future Enhancement**:
- Rate limiting on `/api/auth/login`
- Account lockout after failed attempts
- CAPTCHA for suspicious activity

### 2. XSS (Cross-Site Scripting)

**Current Protection**:
- React automatically escapes user input
- API responses validated with Pydantic

**Risk**:
- Tokens stored in localStorage (vulnerable to XSS)

**Future Enhancement**:
- Move tokens to httpOnly cookies
- Implement Content Security Policy (CSP)

### 3. CSRF (Cross-Site Request Forgery)

**Current Protection**:
- JWT tokens in Authorization header (not cookies)
- CORS restrictions prevent unauthorized origins

**Why it's safe**:
- Malicious sites cannot read localStorage
- CORS blocks cross-origin requests

### 4. SQL Injection

**Current Protection**:
- SQLAlchemy ORM (parameterized queries)
- Pydantic input validation
- Type checking on all inputs

**Example**:
```python
# ✅ Safe - parameterized query
user = db.query(User).filter(User.username == username).first()

# ❌ Unsafe - string concatenation (we don't do this)
query = f"SELECT * FROM users WHERE username = '{username}'"
```

### 5. Token Theft

**Risk**: If access_token is stolen, attacker can impersonate user

**Mitigation**:
- Short token lifetime (30 minutes)
- Tokens expire automatically
- User can logout to invalidate session
- HTTPS prevents man-in-the-middle attacks

**Future Enhancement**:
- Token blacklist on logout
- Device fingerprinting
- Suspicious activity detection

### 6. Man-in-the-Middle (MITM)

**Protection**:
- HTTPS encryption (enforced by Render/Vercel)
- Certificate pinning (future)

**Verification**:
- Check for 🔒 padlock in browser
- Verify domain name matches
- Use trusted DNS servers

## 📋 Security Checklist for Deployment

### Before Going Live:

- [ ] Change all default passwords and secret keys
- [ ] Set unique `JWT_SECRET_KEY` in production .env
- [ ] Enable HTTPS (automatic on Render/Vercel)
- [ ] Configure `ALLOWED_ORIGINS` for production
- [ ] Verify `.env` is in `.gitignore`
- [ ] Review all API keys (Binance, etc.)
- [ ] Test authentication flow end-to-end
- [ ] Verify protected endpoints require auth
- [ ] Check CORS settings work correctly
- [ ] Test token refresh mechanism
- [ ] Verify logout clears all tokens

### Ongoing Security:

- [ ] Rotate API keys regularly (every 90 days)
- [ ] Monitor for suspicious login attempts
- [ ] Keep dependencies updated (`pip list --outdated`)
- [ ] Review logs for unusual activity
- [ ] Backup database regularly
- [ ] Test disaster recovery plan

## 🔑 Secret Key Management

### Generating Secure Keys

**JWT Secret Key**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Example output: 8fT9xK2mN4vL7qP1wE6rY3uI5oA0sD9f
```

**Fernet Encryption Key**:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Example output: gAAAAABhk...
```

### Storing Keys Securely

**Local Development**:
- Store in `.env` file
- Add `.env` to `.gitignore`
- NEVER commit to git

**Production (Render)**:
- Use Render environment variables
- Set in dashboard → Settings → Environment
- Never hardcode in code

**Production (Vercel)**:
- Use Vercel environment variables
- Set in dashboard → Settings → Environment Variables
- Separate secrets for preview/production

## 🛡️ User Account Security

### Password Policy

**Minimum Requirements**:
- Length: 6 characters (enforced)
- Recommended: 12+ characters

**Strong Password Examples**:
```
✅ MyTr@d1ngB0t2025!
✅ C0mpl3x&S3cur3Pwd
✅ AI_Trading_2025_Secure

❌ 123456
❌ password
❌ admin123
```

### User Roles

**Current Implementation**:
- `is_active`: Can user login?
- `is_admin`: Future role-based access control

**Future Enhancement**:
- Read-only users (view only, no trading)
- Trading users (can execute trades)
- Admin users (full access + user management)

## 🔍 Monitoring & Auditing

### What to Monitor

1. **Failed Login Attempts**
   - Multiple failures from same IP
   - Unusual login patterns
   - Login from new locations

2. **API Usage**
   - Unusual trading volume
   - Rapid-fire requests
   - Failed API calls

3. **System Health**
   - Database connectivity
   - API key validity
   - Token refresh errors

### Logging Best Practices

**What to Log**:
- ✅ User login/logout events
- ✅ Failed authentication attempts
- ✅ Trade executions
- ✅ Bot start/stop events
- ✅ API errors and exceptions

**What NOT to Log**:
- ❌ Passwords (plain or hashed)
- ❌ API keys or secrets
- ❌ JWT tokens
- ❌ Sensitive user data

### Audit Trail

**Implemented**:
- `AuditLog` model in database
- Tracks actions, IP addresses, timestamps

**Usage**:
```python
# Log security event
audit = AuditLog(
    action="login",
    details=f"User {username} logged in",
    ip_address=request.client.host,
    timestamp=datetime.utcnow()
)
db.add(audit)
db.commit()
```

## 🚀 Production Security Hardening

### Environment Variables

**Required**:
```bash
# Backend (Render)
JWT_SECRET_KEY=your-generated-secret-key
BINANCE_API_KEY=your-binance-api-key
BINANCE_SECRET=your-binance-secret
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-app.vercel.app
DATABASE_URL=postgresql://... (for production DB)
```

### HTTPS Configuration

**Render**:
- Automatic HTTPS
- Free SSL certificates
- HTTP → HTTPS redirect

**Vercel**:
- Automatic HTTPS
- Free SSL certificates
- Edge network security

### Database Security

**PostgreSQL (Production)**:
```bash
# Use strong password
DATABASE_URL=postgresql://user:STRONG_PASSWORD@host:5432/dbname

# Enable SSL
DATABASE_URL=postgresql://user:pass@host:5432/dbname?sslmode=require
```

**Backup Strategy**:
- Daily automated backups
- Keep 30 days of backups
- Test restore procedure

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [React Security](https://reactjs.org/docs/dom-elements.html#dangerouslysetinnerhtml)

## 🆘 Incident Response

### If You Suspect a Breach:

1. **Immediate Actions**:
   - Rotate all API keys (Binance, etc.)
   - Change JWT_SECRET_KEY
   - Force logout all users
   - Review audit logs

2. **Investigation**:
   - Check recent trades
   - Review login history
   - Analyze server logs
   - Check for unauthorized API access

3. **Recovery**:
   - Restore from backup if needed
   - Implement additional security measures
   - Document incident and lessons learned

### Emergency Contacts:

- Binance Support: https://www.binance.th/en/support
- Render Support: https://render.com/support
- Vercel Support: https://vercel.com/support

---

**Remember**: Security is an ongoing process, not a one-time setup. Stay vigilant and keep your systems updated!
