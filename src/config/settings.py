"""
Configuration settings for Zoho Sprints MCP Server.
"""

import os
from typing import Optional


class Settings:
    """Application settings."""
    
    # Zoho Sprints API Configuration
    ZOHO_CLIENT_ID: str = os.getenv("ZOHO_CLIENT_ID", "")
    ZOHO_CLIENT_SECRET: str = os.getenv("ZOHO_CLIENT_SECRET", "")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Zoho API URLs
    ZOHO_AUTH_URL: str = "https://accounts.zoho.com/oauth/v2/token"
    ZOHO_SPRINTS_BASE_URL: str = "https://sprintsapi.zoho.com/zsapi/team/870567727"
    
    # OAuth Scopes - trying Zoho Sprints specific scope
    ZOHO_SCOPES: str = "ZohoSprints.teams.READ,ZohoSprints.projects.READ,ZohoSprints.sprints.READ,ZohoSprints.items.READ,ZohoSprints.epic.READ"  # Using ZohoProjects scope which might work for Sprints
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required settings."""
        if not cls.ZOHO_CLIENT_ID:
            raise ValueError("ZOHO_CLIENT_ID environment variable is required")
        if not cls.ZOHO_CLIENT_SECRET:
            raise ValueError("ZOHO_CLIENT_SECRET environment variable is required")
        return True


# Global settings instance
settings = Settings()
