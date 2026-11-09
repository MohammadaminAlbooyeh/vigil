# Sentinel-X Security
# mTLS and JWT authentication

import jwt
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

security_scheme = HTTPBearer(auto_error=False)

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.jwt_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)

def verify_token(token: str) -> Optional[Dict]:
    """Verify a JWT token."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None

async def get_current_user(request: Request) -> Optional[Dict]:
    """Get current authenticated user from request."""
    credentials: Optional[HTTPAuthorizationCredentials] = await security_scheme(request)
    if not credentials:
        return None
    return verify_token(credentials.credentials)

def verify_device_signature(device_id: str, signature: str, timestamp: str, secret: str) -> bool:
    """Verify mTLS device signature."""
    message = f"{device_id}{timestamp}"
    expected = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

def generate_device_secret(device_id: str) -> str:
    """Generate a device secret."""
    return hmac.new(
        device_id.encode(),
        b"sentinel-x-device-secret",
        hashlib.sha256
    ).hexdigest()