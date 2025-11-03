"""
JWT Authentication and Password Hashing Utilities
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from cryptography.fernet import Fernet
import os
import base64
import hashlib
import logging

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Encryption for API keys
logger = logging.getLogger("app.security.auth")

def _derive_fernet_key_from_secret(secret: str) -> bytes:
    """Derive a Fernet key from an arbitrary secret using SHA-256.
    This ensures a deterministic, 32-byte key suitable for Fernet.
    """
    digest = hashlib.sha256(secret.encode("utf-8")).digest()  # 32 bytes
    return base64.urlsafe_b64encode(digest)

# Prefer a fully-formed Fernet key if provided
_fernet_key_env = os.getenv("ENCRYPTION_KEY_FERNET")
if _fernet_key_env:
    try:
        cipher_suite = Fernet(_fernet_key_env.encode("utf-8"))
    except Exception:
        logger.error("Invalid ENCRYPTION_KEY_FERNET provided; falling back to derived key")
        _fernet_key_env = None

if not _fernet_key_env:
    # Derive from SECRET_KEY if available, else from JWT_SECRET_KEY
    base_secret = os.getenv("SECRET_KEY") or os.getenv("JWT_SECRET_KEY")
    if not base_secret:
        # As a last resort, generate a key (acceptable in dev, risky in prod)
        logger.warning("No SECRET_KEY/JWT_SECRET_KEY set; generating ephemeral encryption key. Keys will not be decryptable across restarts!")
        cipher_suite = Fernet(Fernet.generate_key())
    else:
        derived_key = _derive_fernet_key_from_secret(base_secret)
        cipher_suite = Fernet(derived_key)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()


def encrypt_api_key(api_key: str) -> str:
    """Encrypt API key for secure storage"""
    if not api_key:
        return ""
    try:
        encrypted = cipher_suite.encrypt(api_key.encode())
        return encrypted.decode()
    except Exception as e:
        raise ValueError(f"Failed to encrypt API key: {e}")


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt API key from storage"""
    if not encrypted_key:
        return ""
    try:
        decrypted = cipher_suite.decrypt(encrypted_key.encode())
        return decrypted.decode()
    except Exception as e:
        # Normalize error to avoid leaking internals
        raise ValueError("Failed to decrypt API key. Please re-save your API keys.")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token with longer expiration"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> dict:
    """
    Verify and decode a JWT token
    
    Args:
        token: The JWT token to verify
        token_type: Expected token type ("access" or "refresh")
    
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check token type
        if payload.get("type") != token_type:
            raise credentials_exception
        
        # Check if token has expired
        exp = payload.get("exp")
        if exp is None or datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except JWTError:
        raise credentials_exception


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to get the current authenticated user from JWT token
    
    Usage:
        @app.get("/protected")
        async def protected_route(current_user: dict = Depends(get_current_user)):
            return {"user": current_user}
    """
    token = credentials.credentials
    payload = verify_token(token, token_type="access")
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"username": username, "user_id": payload.get("user_id")}


async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to get current active user (can be extended to check if user is disabled)
    """
    # You can add additional checks here (e.g., check if user is active in database)
    return current_user
