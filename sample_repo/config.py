"""Configuration module."""

import os


def get_settings():
    """Get application settings."""
    return {
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "port": int(os.getenv("PORT", "8000")),
        "environment": os.getenv("ENVIRONMENT", "development"),
    }
