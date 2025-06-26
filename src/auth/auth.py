"""
Authentication backend
"""
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)
import os

from .manager import get_user_manager

# Secret key for JWT signing – set via environment variable in production
SECRET = os.getenv("JWT_SECRET", "CHANGE_ME_SECRET")

cookie_transport = CookieTransport(cookie_name="bonds", cookie_max_age=3600)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
