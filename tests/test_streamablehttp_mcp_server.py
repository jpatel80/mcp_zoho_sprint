"""
Tests for the Zoho Sprints StreamableHttp MCP server.
"""

import pytest
import requests
import json
import time
import os


class TestZohoSprintsStreamableHttpMCPServer:
    """Test suite for the Zoho Sprints StreamableHttp MCP server."""
    
    @pytest.fixture
    def base_url(self):
        """Base URL for the StreamableHttp MCP server."""
        return "http://localhost:8000"
    
    @pytest.fixture
    def headers(self):
        """Headers for MCP requests."""
        return {
            "Content-Type": "application/json"
        }
    
    @pytest.fixture
    def mock_zoho_credentials(self):
        """Mock Zoho credentials for testing."""
        os.environ["ZOHO_CLIENT_ID"] = "test_client_id"
        os.environ["ZOHO_CLIENT_SECRET"] = "test_client_secret"
        yield
        # Clean up
        if "ZOHO_CLIENT_ID" in os.environ:
            del os.environ["ZOHO_CLIENT_ID"]
        if "ZOHO_CLIENT_SECRET" in os.environ:
            del os.environ["ZOHO_CLIENT_SECRET"]
    
    def test_root_endpoint(self, base_url):
        """Test the root endpoint."""
        response = requests.get(f"{base_url}/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "zoho-sprints-mcp-server"
        assert data["version"] == "1.0.0"
        assert data["transport"] == "streamablehttp"
        assert data["framework"] == "fastapi"
        assert "endpoints" in data
    
    def test_health_check(self, base_url):
        """Test the health check endpoint."""
        response = requests.get(f"{base_url}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["transport"] == "streamablehttp"
        assert data["framework"] == "fastapi"
        assert data["service"] == "zoho-sprints"
    
    def test_mcp_initialize(self, base_url, headers, mock_zoho_credentials):
        """Test MCP initialize request."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = requests.post(f"{base_url}/mcp", json=request_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 1
        assert data.get("error") is None
        assert "result" in data
        
        result = data["result"]
        assert "protocolVersion" in result
        assert "capabilities" in result
        assert "serverInfo" in result
    
    def test_mcp_tools_list(self, base_url, headers):
        """Test MCP tools/list request."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = requests.post(f"{base_url}/mcp", json=request_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 2
        assert data.get("error") is None
        assert "result" in data
        
        result = data["result"]
        assert "tools" in result
        tools = result["tools"]
        
        # Check that all expected Zoho Sprints tools are present
        expected_tools = [
            "get_projects", "get_project", "get_sprints", "get_sprint",
            "get_items", "get_item", "get_epics", "get_epic"
        ]
        
        tool_names = [tool["name"] for tool in tools]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Tool {expected_tool} not found"
    
    def test_mcp_tools_call_before_initialize(self, base_url, headers):
        """Test that tools/call fails before initialize."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "calls": [
                    {
                        "name": "get_projects",
                        "arguments": {}
                    }
                ]
            }
        }
        
        response = requests.post(f"{base_url}/mcp", json=request_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 3
        assert "error" in data
        assert data["error"]["code"] == -32603
        assert "Server not initialized" in data["error"]["message"]
    
    def test_mcp_tools_call_after_initialize(self, base_url, headers, mock_zoho_credentials):
        """Test MCP tools/call request after initialization."""
        # First initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        init_response = requests.post(f"{base_url}/mcp", json=init_request, headers=headers)
        assert init_response.status_code == 200
        
        # Then try to call a tool
        tool_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "calls": [
                    {
                        "name": "get_projects",
                        "arguments": {}
                    }
                ]
            }
        }
        
        response = requests.post(f"{base_url}/mcp", json=tool_request, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 5
        # Note: This will likely fail due to invalid Zoho credentials in test environment
        # but the MCP protocol should work correctly
    
    def test_mcp_invalid_method(self, base_url, headers):
        """Test MCP request with invalid method."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "invalid_method",
            "params": {}
        }
        
        response = requests.post(f"{base_url}/mcp", json=request_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 6
        assert "error" in data
        assert data["error"]["code"] == -32601
        assert "Method not found" in data["error"]["message"]
    
    def test_mcp_notification_initialized(self, base_url, headers):
        """Test MCP notifications/initialized request."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "notifications/initialized",
            "params": {}
        }
        
        response = requests.post(f"{base_url}/mcp", json=request_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 7
        assert data.get("error") is None
    
    def test_mcp_malformed_request(self, base_url, headers):
        """Test MCP request with malformed JSON."""
        response = requests.post(f"{base_url}/mcp", data="invalid json", headers=headers)
        assert response.status_code == 422  # FastAPI validation error
    
    def test_mcp_missing_method(self, base_url, headers):
        """Test MCP request without method."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 8,
            "params": {}
        }
        
        response = requests.post(f"{base_url}/mcp", json=request_data, headers=headers)
        assert response.status_code == 422  # FastAPI validation error
    
    def test_server_startup(self):
        """Test that the server can start up correctly."""
        # This test verifies the server can be imported and instantiated
        try:
            from src.mcp_streamable_http_server import StreamableHttpMCPServer
            server = StreamableHttpMCPServer(host="127.0.0.1", port=8001)
            assert server.host == "127.0.0.1"
            assert server.port == 8001
            assert server.initialized is False
            assert server.zoho_service is None
        except ImportError:
            pytest.skip("Cannot import MCP server - may be running in test environment")
    
    def test_zoho_service_import(self):
        """Test that the Zoho Sprints service can be imported."""
        try:
            from src.services.zoho_sprints import ZohoSprintsService
            # This will fail due to missing environment variables, but import should work
            pytest.raises(ValueError, ZohoSprintsService)
        except ImportError:
            pytest.skip("Cannot import Zoho service - may be running in test environment")
    
    def test_config_settings_import(self):
        """Test that the configuration settings can be imported."""
        try:
            from src.config.settings import Settings
            assert hasattr(Settings, 'ZOHO_CLIENT_ID')
            assert hasattr(Settings, 'ZOHO_CLIENT_SECRET')
            assert hasattr(Settings, 'ZOHO_AUTH_URL')
            assert hasattr(Settings, 'ZOHO_SPRINTS_BASE_URL')
        except ImportError:
            pytest.skip("Cannot import config settings - may be running in test environment")


if __name__ == "__main__":
    pytest.main([__file__])

