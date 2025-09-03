"""
Zoho Sprints API service module.
Handles authentication and API calls to Zoho Sprints.
"""

import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from src.config.settings import settings

logger = logging.getLogger(__name__)


class ZohoSprintsService:
    """Service class for interacting with Zoho Sprints API."""
    
    def __init__(self):
        """Initialize the Zoho Sprints service."""
        # Validate configuration
        settings.validate()
        
        self.client_id = settings.ZOHO_CLIENT_ID
        self.client_secret = settings.ZOHO_CLIENT_SECRET
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.base_url = settings.ZOHO_SPRINTS_BASE_URL
        
    async def authenticate(self) -> bool:
        """Authenticate with Zoho Sprints API using client credentials."""
        try:
            # Zoho uses OAuth 2.0 with client credentials flow
            auth_url = settings.ZOHO_AUTH_URL
            
            auth_data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
                "scope": settings.ZOHO_SCOPES
            }
            
            logger.info(f"Attempting authentication with Zoho...")
            logger.info(f"Auth URL: {auth_url}")
            logger.info(f"Client ID: {self.client_id[:10]}...")
            logger.info(f"Scope: {settings.ZOHO_SCOPES}")
            
            response = requests.post(auth_url, data=auth_data)
            logger.info(f"Auth response status: {response.status_code}")
            logger.info(f"Auth response: {response.text[:500]}")
            
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token")
            
            # Set token expiration (default to 1 hour if not provided)
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            logger.info("Successfully authenticated with Zoho Sprints API")
            logger.info(f"Access token: {self.access_token[:20] if self.access_token else 'None'}...")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        if not self.access_token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        return {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def _is_token_expired(self) -> bool:
        """Check if the access token is expired."""
        if not self.token_expires_at:
            return True
        return datetime.now() >= self.token_expires_at
    
    async def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid access token."""
        if self._is_token_expired():
            logger.info("Access token expired, re-authenticating...")
            return await self.authenticate()
        return True
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects from Zoho Sprints."""
        try:            
            if not await self._ensure_authenticated():
                return []
            
            url = f"{self.base_url}/projects/?action=allprojects&index=1&range=50"            
            headers = self._get_headers()            
            response = requests.get(url, headers=headers)            
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching projects: {str(e)}")
            return []
    
    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific project by ID."""
        try:
            if not await self._ensure_authenticated():
                return None
            
            url = f"{self.base_url}/projects/{project_id}/?action=details"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching project {project_id}: {str(e)}")
            return None
    
    async def get_sprints(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all sprints for a project."""
        try:
            if not await self._ensure_authenticated():
                return []
            
            url = f"{self.base_url}/projects/{project_id}/sprints/?action=data&index=1&range=100&type=%5B2%5D"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching sprints for project {project_id}: {str(e)}")
            return None
    
    async def get_sprint(self, project_id: str, sprint_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific sprint by ID."""
        try:
            if not await self._ensure_authenticated():
                return None
            
            url = f"{self.base_url}/projects/{project_id}/sprints/{sprint_id}/?action=details"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching sprint {sprint_id}: {str(e)}")
            return None
    
    async def get_items(self, project_id: str, sprint_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get items (stories, tasks, bugs) for a project or sprint."""
        try:
            if not await self._ensure_authenticated():
                return []
            
            if sprint_id:
                url = f"{self.base_url}/projects/{project_id}/sprints/{sprint_id}/items"
            else:
                url = f"{self.base_url}/projects/{project_id}/items"
            
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            data = response.json()
            return data.get("items", [])
            
        except Exception as e:
            logger.error(f"Error fetching items: {str(e)}")
            return []
    
    async def get_item(self, project_id: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific item by ID."""
        try:
            if not await self._ensure_authenticated():
                return None
            
            url = f"{self.base_url}/projects/{project_id}/items/{item_id}"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching item {item_id}: {str(e)}")
            return None
    
    async def get_users(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all users for a project."""
        try:
            if not await self._ensure_authenticated():
                return []
            
            url = f"{self.base_url}/projects/{project_id}/users"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            data = response.json()
            return data.get("users", [])
            
        except Exception as e:
            logger.error(f"Error fetching users for project {project_id}: {str(e)}")
            return []
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific user by ID."""
        try:
            if not await self._ensure_authenticated():
                return None
            
            url = f"{self.base_url}/users/{user_id}"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {str(e)}")
            return None
    
    async def get_epics(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all epics for a project."""
        try:
            if not await self._ensure_authenticated():
                return []
            
            url = f"{self.base_url}/projects/{project_id}/epics"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            data = response.json()
            return data.get("epics", [])
            
        except Exception as e:
            logger.error(f"Error fetching epics for project {project_id}: {str(e)}")
            return []
    
    async def get_epic(self, project_id: str, epic_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific epic by ID."""
        try:
            if not await self._ensure_authenticated():
                return None
            
            url = f"{self.base_url}/projects/{project_id}/epics/{epic_id}"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching epic {epic_id}: {str(e)}")
            return None
    
    async def get_releases(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all releases for a project."""
        try:
            if not await self._ensure_authenticated():
                return []
            
            url = f"{self.base_url}/projects/{project_id}/releases"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            data = response.json()
            return data.get("releases", [])
            
        except Exception as e:
            logger.error(f"Error fetching releases for project {project_id}: {str(e)}")
            return []
    
    async def get_release(self, project_id: str, release_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific release by ID."""
        try:
            if not await self._ensure_authenticated():
                return None
            
            url = f"{self.base_url}/projects/{project_id}/releases/{release_id}"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching release {release_id}: {str(e)}")
            return None
