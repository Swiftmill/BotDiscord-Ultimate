from __future__ import annotations

import base64
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Tuple

from jose import jwt

from .settings import get_settings

settings = get_settings()
ALGORITHM = "HS512"


def create_signature(value: str) -> str:
    digest = hmac.new(settings.secret_key.encode(), value.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode()


def verify_signature(value: str, signature: str) -> bool:
    expected = create_signature(value)
    return hmac.compare_digest(expected, signature)


def create_access_token(subject: str, expires_delta: int | None = None) -> Tuple[str, datetime]:
    expires = datetime.utcnow() + timedelta(minutes=expires_delta or settings.token_expiration_minutes)
    payload = {"sub": subject, "exp": expires}
    token = jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
    return token, expires


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])


def machine_fingerprint(user_agent: str, hardware_id: str) -> str:
    raw = f"{user_agent}:{hardware_id}:{settings.secret_key}"
    return hashlib.sha256(raw.encode()).hexdigest()
