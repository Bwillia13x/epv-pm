"""
Authentication backend
"""
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)

from .manager import get_user_manager
import os
import secrets

# JWT signing secret – must be provided in production via environment variable
# If not supplied, a random value is generated (suitable for local development only).
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))

cookie_transport = CookieTransport(cookie_name="bonds", cookie_max_age=3600)

def get_jwt_strategy() -> JWTStrategy:
    """Return JWT strategy configured with the runtime secret key."""
    return JWTStrategy(secret=JWT_SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
