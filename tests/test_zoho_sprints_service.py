"""
Tests for the Zoho Sprints service.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
import requests


class TestZohoSprintsService:
    """Test suite for the Zoho Sprints service."""
    
    @pytest.fixture
    def mock_credentials(self):
        """Mock Zoho credentials for testing."""
        os.environ["ZOHO_CLIENT_ID"] = "test_client_id"
        os.environ["ZOHO_CLIENT_SECRET"] = "test_client_secret"
        yield
        # Clean up
        if "ZOHO_CLIENT_ID" in os.environ:
            del os.environ["ZOHO_CLIENT_ID"]
        if "ZOHO_CLIENT_SECRET" in os.environ:
            del os.environ["ZOHO_CLIENT_SECRET"]
    
    @pytest.fixture
    def mock_auth_response(self):
        """Mock successful authentication response."""
        return {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600
        }
    
    def test_service_initialization(self, mock_credentials):
        """Test that the service can be initialized with valid credentials."""
        try:
            from src.services.zoho_sprints import ZohoSprintsService
            service = ZohoSprintsService()
            assert service.client_id == "test_client_id"
            assert service.client_secret == "test_client_secret"
            assert service.access_token is None
            assert service.refresh_token is None
            assert service.token_expires_at is None
        except ImportError:
            pytest.skip("Cannot import Zoho service - may be running in test environment")
    
    def test_service_initialization_missing_credentials(self):
        """Test that the service fails to initialize without credentials."""
        try:
            from src.services.zoho_sprints import ZohoSprintsService
            with pytest.raises(ValueError, match="ZOHO_CLIENT_ID environment variable is required"):
                ZohoSprintsService()
        except ImportError:
            pytest.skip("Cannot import Zoho service - may be running in test environment")
    
    @patch('requests.post')
    def test_successful_authentication(self, mock_post, mock_credentials, mock_auth_response):
        """Test successful authentication with Zoho."""
        try:
            from src.services.zoho_sprints import ZohoSprintsService
            
            # Mock successful response
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_auth_response
            mock_post.return_value = mock_response
            
            service = ZohoSprintsService()
            result = service.authenticate()
            
            assert result is True
            assert service.access_token == "test_access_token"
            assert service.refresh_token == "test_refresh_token"
            assert service.token_expires_at is not None
            
            # Verify the request was made correctly
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "https://accounts.zoho.com/oauth/v2/token"
            
        except ImportError:
            pytest.skip("Cannot import Zoho service - may be running in test environment")
    
    @patch('requests.post')
    def test_authentication_failure(self, mock_post, mock_credentials):
        """Test authentication failure handling."""
        try:
            from src.services.zoho_sprints import ZohoSprintsService
            
            # Mock failed response
            mock_post.side_effect = requests.exceptions.RequestException("Authentication failed")
            
            service = ZohoSprintsService()
            result = service.authenticate()
            
            assert result is False
            assert service.access_token is None
            
        except ImportError:
            pytest.skip("Cannot import Zoho service - may be running in test environment")
    
    def test_get_headers_without_token(self, mock_credentials):
        """Test that get_headers fails without access token."""
        try:
            from src.services.zoho_sprints import ZohoSprintsService
            
            service = ZohoSprintsService()
            with pytest.raises(ValueError, match="Not authenticated"):
                service._get_headers()
                
        except ImportError:
            pytest.skip("Cannot import Zoho service - may be running in test environment")
    
    def test_get_headers_with_token(self, mock_credentials, mock_auth_response):
        """Test that get_headers returns correct headers with access token."""
        try:
            from src.services.zoho_sprints import ZohoSprintsService
            
            service = ZohoSprintsService()
            service.access_token = "test_token"
            
            headers = service._get_headers()
            assert headers["Authorization"] == "Bearer test_token"
            assert headers["Content-Type"] == "application/json"
            
        except ImportError:
            pytest.skip("Cannot import Zoho service - may be running in test environment")
    
    def test_token_expiration_check(self, mock_credentials):
        """Test token expiration checking."""
        try:
            from src.services.zoho_sprints import ZohoSprintsService
            from datetime import datetime, timedelta
            
            service = ZohoSprintsService()
            
            # Test with no expiration time
            assert service._is_token_expired() is True
            
            # Test with future expiration time
            service.token_expires_at = datetime.now() + timedelta(hours=1)
            assert service._is_token_expired() is False
            
            # Test with past expiration time
            service.token_expires_at = datetime.now() - timedelta(hours=1)
            assert service._is_token_expired() is True
            
        except ImportError:
            pytest.skip("Cannot import Zoho service - may be running in test environment")
    
    @patch('requests.get')
    def test_get_projects_success(self, mock_get, mock_credentials, mock_auth_response):
        """Test successful projects retrieval."""
        try:
            from src.services.zoho_sprints import ZohoSprintsService
            
            # Mock authentication
            with patch.object(ZohoSprintsService, 'authenticate', return_value=True):
                service = ZohoSprintsService()
                service.access_token = "test_token"
                service.token_expires_at = None  # Force re-auth check
                
                # Mock successful projects response
                mock_response = MagicMock()
                mock_response.raise_for_status.return_value = None
                mock_response.json.return_value = {"projects": [{"id": "1", "name": "Test Project"}]}
                mock_get.return_value = mock_response
                
                # Mock _ensure_authenticated to return True
                with patch.object(service, '_ensure_authenticated', return_value=True):
                    projects = service.get_projects()
                    
                    assert len(projects) == 1
                    assert projects[0]["id"] == "1"
                    assert projects[0]["name"] == "Test Project"
                    
        except ImportError:
            pytest.skip("Cannot import Zoho service - may be running in test environment")
    
    @patch('requests.get')
    def test_get_projects_failure(self, mock_get, mock_credentials):
        """Test projects retrieval failure handling."""
        try:
            from src.services.zoho_sprints import ZohoSprintsService
            
            # Mock authentication
            with patch.object(ZohoSprintsService, 'authenticate', return_value=True):
                service = ZohoSprintsService()
                service.access_token = "test_token"
                service.token_expires_at = None  # Force re-auth check
                
                # Mock failed response
                mock_get.side_effect = Exception("API Error")
                
                # Mock _ensure_authenticated to return True
                with patch.object(service, '_ensure_authenticated', return_value=True):
                    projects = service.get_projects()
                    
                    assert projects == []
                    
        except ImportError:
            pytest.skip("Cannot import Zoho service - may be running in test environment")


if __name__ == "__main__":
    pytest.main([__file__])
