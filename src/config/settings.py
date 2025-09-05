"""
Configuration settings for Zoho Sprints MCP Server.
"""

import os
from typing import Optional


class Settings:
    """Application settings."""
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# Global settings instance
settings = Settings()
