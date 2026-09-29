from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import jwt

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


import secrets
import string

def generate_api_key(prefix: str = "sk_live") -> tuple[str, str, str]:
    """Generates an API key and returns (prefix, unhashed_key, hashed_key)."""
    random_part = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    raw_key = f"{prefix}_{random_part}"
    
    # We use the raw key except for the prefix when hashing, but for simplicity
    # just hash the entire raw key.
    hashed_key = get_password_hash(raw_key)
    
    return prefix, raw_key, hashed_key
