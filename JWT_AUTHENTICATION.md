# JWT Authentication Guide

## Overview

The G-AI-TRADE platform now uses JWT (JSON Web Token) authentication to secure all trading and bot management endpoints. This provides:

- **Secure access control**: Only authenticated users can execute trades
- **Token-based authentication**: No need to send credentials with every request
- **Automatic token refresh**: Seamless user experience with auto-renewal
- **Session management**: Secure login/logout functionality

## Architecture

### Backend (FastAPI)

**Authentication Module**: `app/security/auth.py`
- Password hashing using bcrypt
- JWT token creation and verification
- Token refresh mechanism
- User authentication dependencies

**User Model**: `app/models.py`
- User table with username, email, hashed_password
- is_active and is_admin flags
- Login tracking (last_login timestamp)

**Protected Endpoints**:
- POST `/api/trade` - Execute trades
- POST `/api/grid-bot/{symbol}` - Start grid bot
- POST `/api/dca-bot/{symbol}` - Start DCA bot
- POST `/api/auto-bot/*` - Auto bot management

### Frontend (React + TypeScript)

**Authentication Pages**: `ui/src/pages/Login.tsx`
- Combined login/register form
- Token storage in localStorage
- Automatic redirect after authentication

**API Client**: `ui/src/lib/api.ts`
- Axios interceptors for automatic token injection
- Token refresh on 401 responses
- Automatic logout on refresh failure

**Protected Routes**: `ui/src/App.tsx`
- ProtectedRoute component wrapper
- Redirect to /login if not authenticated

## API Endpoints

### 1. Register User
```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "trader123",
  "email": "trader@example.com",
  "password": "securePassword123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "trader123",
    "email": "trader@example.com",
    "is_active": true,
    "is_admin": false
  }
}
```

### 2. Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "trader123",
  "password": "securePassword123"
}

Response: (same as register)
```

### 3. Refresh Token
```bash
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {...}
}
```

### 4. Get Current User
```bash
GET /api/auth/me
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

Response:
{
  "id": 1,
  "username": "trader123",
  "email": "trader@example.com",
  "is_active": true,
  "is_admin": false,
  "created_at": "2025-11-03T10:30:00",
  "last_login": "2025-11-03T12:45:00"
}
```

### 5. Protected Endpoint Example
```bash
POST /api/trade
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "symbol": "BTC/USDT",
  "side": "BUY",
  "amount": 0.01,
  "price": 65000
}
```

## Environment Variables

### Backend (.env)
```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
# Default: "your-secret-key-change-this-in-production"

# Token Expiration (configured in app/security/auth.py)
# ACCESS_TOKEN_EXPIRE_MINUTES=30
# REFRESH_TOKEN_EXPIRE_DAYS=7
```

**IMPORTANT**: Change `JWT_SECRET_KEY` in production! Use a long, random string:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Token Flow

### Initial Login
1. User submits username/password
2. Backend validates credentials
3. Backend creates access_token (30 min) and refresh_token (7 days)
4. Frontend stores both tokens in localStorage
5. Frontend includes access_token in Authorization header for all requests

### Token Refresh
1. Access token expires (30 minutes)
2. API returns 401 Unauthorized
3. Frontend interceptor catches 401
4. Frontend automatically calls /auth/refresh with refresh_token
5. Backend validates refresh_token and issues new tokens
6. Frontend retries original request with new access_token

### Logout
1. User clicks logout
2. Frontend clears localStorage (access_token, refresh_token, user)
3. Frontend redirects to /login

## Security Best Practices

### Backend
1. **Use strong SECRET_KEY**: Generate with `secrets.token_urlsafe(32)`
2. **HTTPS Only**: Never use JWT over HTTP in production
3. **Short access token lifetime**: 30 minutes (configurable)
4. **Longer refresh token lifetime**: 7 days (configurable)
5. **Password hashing**: bcrypt with automatic salt
6. **Token type validation**: Ensure access/refresh tokens aren't mixed
7. **User activation**: Check `is_active` flag before allowing login

### Frontend
1. **Store tokens in localStorage**: Easy but vulnerable to XSS
   - Alternative: httpOnly cookies (requires backend changes)
2. **Clear tokens on logout**: Prevent reuse
3. **Handle token expiration**: Automatic refresh on 401
4. **Redirect on auth failure**: Clear UX for expired sessions

### CORS
Update backend ALLOWED_ORIGINS to include your Vercel URL:
```python
# app/main.py
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://your-app.vercel.app").split(",")
```

## Migration Guide

### Existing Installations

1. **Install new dependencies**:
```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

2. **Run database migration** (create users table):
```bash
# The users table will be auto-created on app startup
python -m app.main
```

3. **Create first user** (via API or database):
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"admin123"}'
```

4. **Update .env** with JWT_SECRET_KEY:
```bash
echo "JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env
```

5. **Update frontend** to handle login flow

## Testing

### Manual Testing

1. **Register a new user**:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"test123"}'
```

2. **Login**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
```

3. **Access protected endpoint**:
```bash
curl -X POST http://localhost:8000/api/trade \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTC/USDT","side":"BUY","amount":0.01}'
```

4. **Refresh token**:
```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"YOUR_REFRESH_TOKEN"}'
```

## Troubleshooting

### "Could not validate credentials"
- Access token expired → Frontend should auto-refresh
- Invalid token format → Check Authorization header format
- Wrong SECRET_KEY → Tokens created with different key

### "User not found or inactive"
- User deleted from database
- User `is_active` set to False
- User ID mismatch

### Frontend shows login page on every refresh
- Tokens not stored in localStorage
- Check browser console for errors
- Verify API_BASE URL is correct

### 401 errors after deployment
- Update ALLOWED_ORIGINS in backend .env
- Check CORS configuration
- Verify JWT_SECRET_KEY is set in production

## Future Enhancements

- [ ] Add email verification
- [ ] Implement password reset flow
- [ ] Add 2FA (two-factor authentication)
- [ ] Rate limiting on login endpoint
- [ ] Token blacklist for logout
- [ ] Role-based access control (RBAC)
- [ ] Session management dashboard
- [ ] API key authentication for bots
