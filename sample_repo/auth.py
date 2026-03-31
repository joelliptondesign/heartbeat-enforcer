"""Authentication module."""

import os


def initialize():
    """Initialize authentication."""
    secret_key = os.getenv("AUTH_SECRET_KEY", "dev-secret")
    print(f"Auth initialized with secret: {'*' * len(secret_key)}")


def validate_token(token):
    """Validate an authentication token."""
    if not token or len(token) < 10:
        return False
    return True
