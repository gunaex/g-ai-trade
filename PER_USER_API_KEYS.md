# Per-User API Key Management

## Overview

The trading platform now supports per-user Binance API key management. Each user can securely store and manage their own API credentials, providing better security, isolation, and compliance.

## Features

### ✅ Security
- **Fernet Encryption**: All API keys are encrypted using Fernet symmetric encryption before storage
- **User Isolation**: Each user manages their own credentials independently
- **Secure Storage**: Encrypted keys stored in the database, never exposed in responses
- **Token-Based Access**: API key operations require JWT authentication

### ✅ User Experience
- **Settings Page**: Dedicated UI for managing API keys in Settings
- **Key Preview**: Shows masked API key preview (first 8 + last 4 characters)
- **Status Indicator**: Visual feedback showing if API keys are configured
- **Easy Updates**: Users can update or delete their API keys anytime

## Backend Implementation

### Database Schema

```python
# app/models.py - User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Per-user encrypted API keys
    binance_api_key = Column(String, nullable=True)      # Encrypted
    binance_api_secret = Column(String, nullable=True)   # Encrypted
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
```

### Encryption Utilities

```python
# app/security/auth.py
from cryptography.fernet import Fernet
import os
import base64

# Initialize Fernet cipher with SECRET_KEY from environment
ENCRYPTION_KEY = os.getenv("SECRET_KEY", Fernet.generate_key().decode())
if len(ENCRYPTION_KEY) < 32:
    ENCRYPTION_KEY = base64.urlsafe_b64encode(ENCRYPTION_KEY.ljust(32)[:32].encode()).decode()
cipher_suite = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)

def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key using Fernet symmetric encryption"""
    return cipher_suite.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key"""
    return cipher_suite.decrypt(encrypted_key.encode()).decode()
```

### API Endpoints

#### 1. Save API Keys (Encrypted)

```http
POST /api/auth/api-keys
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "binance_api_key": "your-api-key",
  "binance_api_secret": "your-api-secret"
}
```

**Response:**
```json
{
  "success": true,
  "message": "API keys saved and encrypted successfully",
  "has_api_keys": true
}
```

#### 2. Get API Keys Status

```http
GET /api/auth/api-keys/status
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "has_api_keys": true,
  "api_key_preview": "5D0B2936...C28E"
}
```

#### 3. Delete API Keys

```http
DELETE /api/auth/api-keys
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "message": "API keys deleted successfully"
}
```

## Frontend Implementation

### Settings Page Integration

```typescript
// ui/src/pages/Settings.tsx
import { useState, useEffect } from 'react'
import api from '../lib/api'

export default function Settings() {
  const [apiKey, setApiKey] = useState('')
  const [apiSecret, setApiSecret] = useState('')
  const [hasApiKeys, setHasApiKeys] = useState(false)
  const [apiKeyPreview, setApiKeyPreview] = useState('')

  // Load API key status on mount
  useEffect(() => {
    loadApiKeyStatus()
  }, [])

  const loadApiKeyStatus = async () => {
    const { data } = await api.getApiKeysStatus()
    setHasApiKeys(data.has_api_keys)
    setApiKeyPreview(data.api_key_preview || '')
  }

  const handleSaveApiKeys = async () => {
    await api.saveApiKeys(apiKey, apiSecret)
    setApiKey('')
    setApiSecret('')
    await loadApiKeyStatus()
  }

  const handleDeleteApiKeys = async () => {
    await api.deleteApiKeys()
    setHasApiKeys(false)
    setApiKeyPreview('')
  }
}
```

### API Client Methods

```typescript
// ui/src/lib/api.ts
export const apiClient = {
  // API Key Management
  saveApiKeys: (binanceApiKey: string, binanceApiSecret: string) =>
    api.post('/auth/api-keys', { 
      binance_api_key: binanceApiKey, 
      binance_api_secret: binanceApiSecret 
    }),

  getApiKeysStatus: () =>
    api.get<{ has_api_keys: boolean; api_key_preview: string | null }>(
      '/auth/api-keys/status'
    ),

  deleteApiKeys: () =>
    api.delete('/auth/api-keys'),
}
```

## Usage Flow

### 1. User Registration/Login
1. User creates account or logs in
2. Receives JWT access token
3. Token stored in localStorage

### 2. Configure API Keys
1. Navigate to Settings page
2. Enter Binance API key and secret
3. Click "Save & Encrypt API Keys"
4. Backend encrypts and stores keys
5. UI shows success message and key preview

### 3. View API Key Status
1. Settings page loads automatically
2. Shows if API keys are configured
3. Displays masked key preview: `5D0B2936...C28E`

### 4. Update API Keys
1. User enters new API keys in Settings
2. Click "Update API Keys"
3. Backend encrypts and replaces old keys

### 5. Delete API Keys
1. Click "Delete API Keys" button
2. Confirm deletion in dialog
3. Backend removes encrypted keys
4. UI updates to show no keys configured

## Security Considerations

### ✅ Encryption at Rest
- API keys encrypted with Fernet before database storage
- Encryption key (`SECRET_KEY`) stored in environment variables
- Never expose decrypted keys in API responses

### ✅ Authentication Required
- All API key endpoints require JWT authentication
- Users can only access their own API keys
- Token verification on every request

### ✅ HTTPS Enforcement
- All API requests use HTTPS in production
- Prevents man-in-the-middle attacks
- Secure transmission of sensitive data

### ✅ Key Preview Masking
- Only show first 8 and last 4 characters
- Full key never returned to frontend
- Status check doesn't expose secrets

## Environment Variables

### Backend (.env)

```bash
# Required for API key encryption
SECRET_KEY=fyiDKF3rFVqnIPif-UqZRa4ILzdVcH4_8ReJkK_poVo=

# Required for JWT authentication
JWT_SECRET_KEY=7LD_8grlnUAd_ikDBAh48F71c4sZlEz6ebwoisKSFec

# Database
DATABASE_URL=sqlite:///./g_ai_trade.db

# Global fallback keys (deprecated, use per-user keys instead)
# BINANCE_API_KEY=...
# BINANCE_SECRET=...
```

### Frontend (.env)

```bash
# Local development
VITE_API_URL=http://localhost:8000/api

# Production (Vercel)
# VITE_API_URL=https://g-ai-trade-backend.onrender.com/api
```

## Migration Path

### From Global Keys to Per-User Keys

1. **User Signs Up**: New users configure their own API keys immediately
2. **Existing Users**: Migrate global keys to user-specific storage
3. **Gradual Transition**: Support both methods during migration
4. **Final Step**: Remove global BINANCE_API_KEY/SECRET from environment

### Migration Script (Optional)

```python
# migrate_api_keys.py
from app.models import User
from app.security.auth import encrypt_api_key
from app.db import get_db
import os

def migrate_global_keys_to_users():
    """Migrate global API keys to all existing users"""
    global_key = os.getenv("BINANCE_API_KEY")
    global_secret = os.getenv("BINANCE_SECRET")
    
    if not global_key or not global_secret:
        print("No global keys found")
        return
    
    db = next(get_db())
    users = db.query(User).all()
    
    for user in users:
        if not user.binance_api_key:  # Only if user doesn't have keys
            user.binance_api_key = encrypt_api_key(global_key)
            user.binance_api_secret = encrypt_api_key(global_secret)
    
    db.commit()
    print(f"Migrated keys to {len(users)} users")
```

## Testing

### Local Testing

```bash
# 1. Start backend
python app/main.py

# 2. Start frontend
cd ui
npm run dev

# 3. Test flow
# - Register/login
# - Navigate to Settings
# - Save API keys
# - Check status
# - Delete keys
```

### API Testing with curl

```bash
# 1. Login to get token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Response: {"access_token": "eyJ...", "refresh_token": "eyJ..."}

# 2. Save API keys
curl -X POST http://localhost:8000/api/auth/api-keys \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"binance_api_key": "test-key", "binance_api_secret": "test-secret"}'

# 3. Check status
curl -X GET http://localhost:8000/api/auth/api-keys/status \
  -H "Authorization: Bearer eyJ..."

# 4. Delete keys
curl -X DELETE http://localhost:8000/api/auth/api-keys \
  -H "Authorization: Bearer eyJ..."
```

## Next Steps

### ✅ Completed
- [x] Database schema with encrypted API key columns
- [x] Encryption/decryption utilities using Fernet
- [x] Backend API endpoints for CRUD operations
- [x] Frontend Settings page integration
- [x] API client methods for key management
- [x] JWT authentication for all endpoints

### 🔄 Pending
- [ ] Update trading endpoints to use user-specific keys
- [ ] Modify `get_binance_th_client()` to accept user parameter
- [ ] Test end-to-end trading with user keys
- [ ] Deploy to Render with environment variables
- [ ] Document API key best practices for users

## Deployment Checklist

### Render Backend

```bash
# Environment Variables to Add:
SECRET_KEY=fyiDKF3rFVqnIPif-UqZRa4ILzdVcH4_8ReJkK_poVo=
JWT_SECRET_KEY=7LD_8grlnUAd_ikDBAh48F71c4sZlEz6ebwoisKSFec
DATABASE_URL=postgresql://...
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### Vercel Frontend

```bash
# Environment Variables to Add:
VITE_API_URL=https://g-ai-trade-backend.onrender.com/api
```

## Benefits

1. **Security**: Each user controls their own API credentials
2. **Compliance**: Users are responsible for their own API keys
3. **Scalability**: Supports multi-tenant architecture
4. **Isolation**: API rate limits and errors isolated per user
5. **Flexibility**: Users can update keys without affecting others
6. **Transparency**: Clear visibility into API key configuration status

## Support

For issues or questions:
- Check authentication token is valid
- Verify SECRET_KEY is properly configured
- Ensure HTTPS is used in production
- Review error messages in browser console
- Check backend logs for encryption errors
