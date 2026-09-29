from datetime import timedelta

from jose import jwt

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password


def test_password_hashing() -> None:
    password = "supersecretpassword123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_create_access_token() -> None:
    subject = "user123"
    token = create_access_token(subject=subject)

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == subject
    assert "exp" in payload


def test_create_access_token_with_expiry() -> None:
    subject = "user123"
    expires = timedelta(minutes=5)
    token = create_access_token(subject=subject, expires_delta=expires)

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == subject
    assert "exp" in payload
