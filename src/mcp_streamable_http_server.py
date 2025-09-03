"""
MCP Server implementation using FastAPI for StreamableHttp transport.
This server integrates with Zoho Sprints API to provide project management tools.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from src.services.zoho_sprints import ZohoSprintsService
from src.utils.logger import logger
from src.config.settings import settings


class MCPRequest(BaseModel):
    """MCP request model."""
    jsonrpc: str = "2.0"
    id: Optional[int] = None
    method: str
    params: Optional[Dict[str, Any]] = None


class MCPResponse(BaseModel):
    """MCP response model."""
    jsonrpc: str = "2.0"
    id: Optional[int] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class StreamableHttpMCPServer:
    """MCP Server that communicates via StreamableHttp transport and integrates with Zoho Sprints."""
    
    def __init__(self, host: str = None, port: int = None):
        """Initialize the StreamableHttp MCP server."""
        self.host = host or settings.HOST
        self.port = port or settings.PORT
        self.initialized = False
        self.zoho_service = None
        self.app = FastAPI(title="Zoho Sprints MCP Server", version="1.0.0")
        self.setup_routes()
    
    def setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint."""
            return {
                "name": "zoho-sprints-mcp-server",
                "version": "1.0.0",
                "transport": "streamablehttp",
                "framework": "fastapi",
                "endpoints": {
                    "health": "GET /health",
                    "mcp": "POST /mcp"
                }
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy", 
                "transport": "streamablehttp",
                "framework": "fastapi",
                "service": "zoho-sprints"
            }
        
        @self.app.post("/mcp")
        async def handle_mcp_request(request: MCPRequest):
            """Handle MCP requests via HTTP POST."""
            try:
                response = await self.process_mcp_request(request)
                return response
            except Exception as e:
                logger.error(f"Error processing MCP request: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def process_mcp_request(self, request: MCPRequest) -> Dict[str, Any]:
        """Process MCP requests."""
        method = request.method
        params = request.params or {}
        request_id = request.id
        
        logger.info(f"Processing MCP request: {method}")
        
        try:
            if method == "initialize":
                return await self.handle_initialize(params, request_id)
            elif method == "notifications/initialized":
                logger.info("Received initialization notification")
                return {"jsonrpc": "2.0", "id": request_id}
            elif method == "tools/list":
                return await self.handle_tools_list(params, request_id)
            elif method == "tools/call":
                return await self.handle_tools_call(params, request_id)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": "Method not found",
                        "data": f"Unknown method: {method}"
                    }
                }
        except Exception as e:
            logger.error(f"Error processing request {method}: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }
    
    async def handle_initialize(self, params: Dict[str, Any], request_id: int) -> Dict[str, Any]:
        """Handle initialize request and authenticate with Zoho Sprints."""
        logger.info("Initializing Zoho Sprints MCP server")
        
        try:
            # Initialize Zoho Sprints service
            self.zoho_service = ZohoSprintsService()
            
            # Authenticate with Zoho Sprints
            auth_success = await self.zoho_service.authenticate()
            if not auth_success:
                raise Exception("Failed to authenticate with Zoho Sprints API")
            
            self.initialized = True
            logger.info("Successfully initialized and authenticated with Zoho Sprints")
            logger.info(f"Zoho Sprints access token: {self.zoho_service.access_token}")
            logger.info(f"Zoho Sprints refresh token: {self.zoho_service.refresh_token}")
            logger.info(f"Zoho Sprints token expires at: {self.zoho_service.token_expires_at}")
            logger.info(f"Zoho Sprints base URL: {self.zoho_service.base_url}")
            logger.info(f"Zoho Sprints client ID: {self.zoho_service.client_id}")
            logger.info(f"Zoho Sprints client secret: {self.zoho_service.client_secret}")

            # Use the client's protocol version if available, otherwise default to 2024-11-05
            client_protocol_version = params.get("protocolVersion", "2024-11-05")
            logger.info(f"Client protocol version: {client_protocol_version}")
            
            # Return server capabilities
            capabilities = {
                "tools": {
                    "listChanged": True,
                    "listRequired": False
                }
            }
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": client_protocol_version,
                    "capabilities": capabilities,
                    "serverInfo": {
                        "name": "zoho-sprints-mcp-server",
                        "version": "1.0.0"
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": "Initialization failed",
                    "data": str(e)
                }
            }
    
    async def handle_tools_list(self, params: Dict[str, Any], request_id: int) -> Dict[str, Any]:
        """Handle tools/list request."""
        tools = [
            {
                "name": "get_projects",
                "description": "Get all projects from Zoho Sprints",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_project",
                "description": "Get a specific project by ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Project ID"}
                    },
                    "required": ["project_id"]
                }
            },
            {
                "name": "get_sprints",
                "description": "Get all sprints for a project",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Project ID"}
                    },
                    "required": ["project_id"]
                }
            },
            {
                "name": "get_sprint",
                "description": "Get a specific sprint by ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Project ID"},
                        "sprint_id": {"type": "string", "description": "Sprint ID"}
                    },
                    "required": ["project_id", "sprint_id"]
                }
            },
            {
                "name": "get_items",
                "description": "Get items (stories, tasks, bugs) for a project sprint or backlog",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Project ID"},
                        "sprint_id_or_backlog_id": {"type": "string", "description": "Sprint ID or Backlog ID (required)"}
                    },
                    "required": ["project_id", "sprint_id_or_backlog_id"]
                }
            },
            {
                "name": "get_item",
                "description": "Get a specific item by ID from a project sprint or backlog",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Project ID"},
                        "sprint_id_or_backlog_id": {"type": "string", "description": "Sprint ID or Backlog ID (required)"},
                        "item_id": {"type": "string", "description": "Item ID"}
                    },
                    "required": ["project_id", "sprint_id_or_backlog_id", "item_id"]
                }
            },

            {
                "name": "get_epics",
                "description": "Get all epics for a project",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Project ID"}
                    },
                    "required": ["project_id"]
                }
            },
            {
                "name": "get_epic",
                "description": "Get a specific epic by ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Project ID"},
                        "epic_id": {"type": "string", "description": "Epic ID"}
                    },
                    "required": ["project_id", "epic_id"]
                }
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools}
        }
    
    async def handle_tools_call(self, params: Dict[str, Any], request_id: int) -> Dict[str, Any]:
        """Handle tools/call request."""
        if not self.initialized or not self.zoho_service:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": "Server not initialized",
                    "data": "Call initialize() first"
                }
            }
        
        logger.info(f"Tools call params: {params}")
        tool_calls = params.get("toolCalls", params.get("calls", params.get("tool_calls", [])))
        
        # If no toolCalls array found, check if the tool call is directly in params
        if not tool_calls and "name" in params:
            tool_calls = [params]
            
        logger.info(f"Tool calls extracted: {tool_calls}")
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("arguments", {})
            
            logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
            
            try:
                result = await self._execute_zoho_tool(tool_name, tool_args)
                
                # Format the result
                if "error" not in result:
                    results.append({
                        "name": tool_name,
                        "content": [{
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }]
                    })
                else:
                    results.append({
                        "name": tool_name,
                        "content": [{
                            "type": "text",
                            "text": f"Error: {result.get('error', 'Unknown error')}"
                        }]
                    })
                
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {str(e)}")
                results.append({
                    "name": tool_name,
                    "content": [{
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }]
                })
        
        # Return results in the format expected by MCP clients
        if len(results) == 1:
            single_result = results[0]
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "name": single_result["name"],
                    "content": single_result["content"]
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "calls": results
                }
            }
    
    async def _execute_zoho_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Zoho Sprints tool."""
        try:
            if tool_name == "get_projects":
                logger.info("Executing get_projects tool~~~~")
                projects = await self.zoho_service.get_projects()
                return {"projects": projects, "count": len(projects)}
                
            elif tool_name == "get_project":
                project_id = tool_args.get("project_id")
                if not project_id:
                    return {"error": "project_id is required"}
                project = await self.zoho_service.get_project(project_id)
                return {"project": project} if project else {"error": "Project not found"}
                
            elif tool_name == "get_sprints":
                project_id = tool_args.get("project_id")
                if not project_id:
                    return {"error": "project_id is required"}
                sprints = await self.zoho_service.get_sprints(project_id)
                return {"sprints": sprints, "count": len(sprints)}
                
            elif tool_name == "get_sprint":
                project_id = tool_args.get("project_id")
                sprint_id = tool_args.get("sprint_id")
                if not project_id or not sprint_id:
                    return {"error": "project_id and sprint_id are required"}
                sprint = await self.zoho_service.get_sprint(project_id, sprint_id)
                return {"sprint": sprint} if sprint else {"error": "Sprint not found"}
                
            elif tool_name == "get_items":
                project_id = tool_args.get("project_id")
                sprint_id_or_backlog_id = tool_args.get("sprint_id_or_backlog_id")
                if not project_id or not sprint_id_or_backlog_id:
                    return {"error": "project_id and sprint_id_or_backlog_id are required"}
                items = await self.zoho_service.get_items(project_id, sprint_id_or_backlog_id)
                return {"items": items, "count": len(items)}
                
            elif tool_name == "get_item":
                project_id = tool_args.get("project_id")
                sprint_id_or_backlog_id = tool_args.get("sprint_id_or_backlog_id")
                item_id = tool_args.get("item_id")
                if not project_id or not sprint_id_or_backlog_id or not item_id:
                    return {"error": "project_id, sprint_id_or_backlog_id, and item_id are required"}
                item = await self.zoho_service.get_item(project_id, sprint_id_or_backlog_id, item_id)
                return {"item": item} if item else {"error": "Item not found"}
                
            elif tool_name == "get_epics":
                project_id = tool_args.get("project_id")
                if not project_id:
                    return {"error": "project_id is required"}
                epics = await self.zoho_service.get_epics(project_id)
                return {"epics": epics, "count": len(epics)}
                
            elif tool_name == "get_epic":
                project_id = tool_args.get("project_id")
                epic_id = tool_args.get("epic_id")
                if not project_id or not epic_id:
                    return {"error": "project_id and epic_id are required"}
                epic = await self.zoho_service.get_epic(project_id, epic_id)
                return {"epic": epic} if epic else {"error": "Epic not found"}
                
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            logger.error(f"Error executing Zoho tool {tool_name}: {str(e)}")
            return {"error": str(e)}
    
    def run(self):
        """Run the StreamableHttp MCP server."""
        logger.info(f"Starting Zoho Sprints MCP Server (StreamableHttp mode) on {self.host}:{self.port}")
        logger.info("Using FastAPI framework")
        
        # Run the server using uvicorn
        uvicorn.run(self.app, host=self.host, port=self.port, log_level="info")


def main():
    """Main entry point for the StreamableHttp MCP server."""
    server = StreamableHttpMCPServer()
    server.run()


if __name__ == "__main__":
    main()
