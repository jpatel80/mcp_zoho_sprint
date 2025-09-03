# Zoho Sprints MCP Server

A Model Context Protocol (MCP) server that integrates with Zoho Sprints API to provide project management tools for integration with Claude Desktop and other AI assistants.

## Features

- **Zoho Sprints Integration**: Full access to Zoho Sprints project management data
- **Comprehensive API Coverage**: Projects, sprints, items, users, epics, and releases
- **MCP Protocol Compliance**: Implements the Model Context Protocol for seamless AI integration
- **Docker-First Design**: Containerized for consistent deployment and testing
- **OAuth 2.0 Authentication**: Secure authentication with Zoho Sprints API
- **StreamableHttp Transport**: HTTP-based communication using FastAPI framework
- **Error Handling**: Robust error handling for API failures and invalid inputs
- **JSON-RPC 2.0**: Uses JSON-RPC 2.0 for communication

## Prerequisites

- **Docker and Docker Compose** (required)
- **Zoho Developer Account** with Sprints API access
- **Claude Desktop** (for MCP integration)

## Quick Start

### 1. Set Up Zoho Sprints API Credentials

1. **Get API Credentials**:
   - Go to [Zoho Developer Console](https://api-console.zoho.com/)
   - Create a new client application
   - Note your `client_id` and `client_secret`

2. **Set Environment Variables**:
   ```bash
   export ZOHO_CLIENT_ID="your_client_id_here"
   export ZOHO_CLIENT_SECRET="your_client_secret_here"
   ```

### 2. Start the Server

**Using Make (Recommended)**:
```bash
git clone <repository-url>
cd mcp_zoho_sprint
make setup
make start
```

**Or manually**:
```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with your Zoho credentials
docker compose --env-file .env up --build -d
```

### 3. Verify Server is Running

```bash
# Check container status
make status

# Test the MCP server
make verify
```

### 4. Connect to Claude Desktop

Follow the detailed setup instructions below to connect this MCP server to Claude Desktop.

## Claude Desktop MCP Setup

### Transport Options

This MCP server uses **StreamableHttp transport** for HTTP-based communication:

**StreamableHttp Transport** - HTTP-based communication using FastAPI framework
- **Default mode**: Launches automatically when running `python src/main.py`
- **Best for**: Cloud deployment, remote access, and Docker containers
- **Uses**: `mcp-remote` tool for Claude Desktop integration
- **Works from**: Anywhere with internet access
- **FastAPI framework**: Modern, fast web framework for Python
- **Efficient MCP protocol handling**: Optimized request processing

### Step 1: Start the MCP Server

1. **Using Docker (Recommended)**:
   ```bash
   # Ensure .env file is configured with your Zoho credentials
   docker compose --env-file .env up zoho-sprints-mcp-server -d
   ```

2. **Or manually**:
   ```bash
   cd src
   pip install -r requirements.txt
   python src/main.py
   ```

The server will automatically start in HTTP mode on port 8000.

### Step 2: Configure Claude Desktop

**Important**: MCP servers must be executable processes, not HTTP endpoints. The server needs to run as a process that Claude Desktop can communicate with directly.

1. **Open Claude Desktop**

2. **Access Developer Settings**:
   - Go to **Settings** (gear icon)
   - Click **Developer**
   - Click **Edit Config**

3. **Add MCP Server Configuration**:
   ```json
   {
     "mcpServers": {
       "zoho-sprints": {
         "command": "mcp-remote",
         "args": ["http://localhost:8000/mcp"],
         "env": {}
       }
     }
   }
   ```

4. **Restart Claude Desktop**

## Available Tools

The Zoho Sprints MCP Server provides the following tools:

### Project Management
- **`get_projects`**: Get all projects from Zoho Sprints
- **`get_project`**: Get a specific project by ID

### Sprint Management
- **`get_sprints`**: Get all sprints for a project
- **`get_sprint`**: Get a specific sprint by ID

### Item Management
- **`get_items`**: Get items (stories, tasks, bugs) for a project sprint or backlog
- **`get_item`**: Get a specific item by ID from a project sprint or backlog

### Epic Management
- **`get_epics`**: Get all epics for a project
- **`get_epic`**: Get a specific epic by ID

## API Documentation

For detailed information about the Zoho Sprints API, visit:
- [Zoho Sprints API Documentation](https://sprints.zoho.com/apidoc.html#Overview)

## Development

### Project Structure

```
/
├── agents.md              # Development guidelines
├── .gitignore            # Git ignore patterns
├── .dockerignore         # Docker ignore patterns
├── CHANGELOG.md          # Project change log
├── README.md             # Project documentation
├── docker-compose.yml    # Docker Compose configuration
├── src/                  # Source code directory
│   ├── Dockerfile       # Container configuration
│   ├── requirements.txt # Python dependencies
│   ├── main.py         # Application entry point
│   ├── services/       # Microservices
│   ├── config/         # Configuration files
│   ├── mcp/            # MCP server implementations
│   └── utils/          # Utility modules
└── tests/               # Test files directory
```

### Running Tests

```bash
# Run tests in Docker container
docker compose exec zoho-sprints-mcp-server bash -c "cd tests && python -m pytest -v"

# Run tests with coverage
docker compose exec zoho-sprints-mcp-server bash -c "cd tests && python -m pytest --cov=../src --cov-report=term-missing"
```

### Code Quality Checks

```bash
# Format code
docker compose exec zoho-sprints-mcp-server python -m black --check src/

# Lint code
docker compose exec zoho-sprints-mcp-server python -m flake8 src/
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ZOHO_CLIENT_ID` | Zoho OAuth client ID | Yes | - |
| `ZOHO_CLIENT_SECRET` | Zoho OAuth client secret | Yes | - |
| `HOST` | Server host | No | `0.0.0.0` |
| `PORT` | Server port | No | `8000` |
| `LOG_LEVEL` | Logging level | No | `INFO` |

### Docker Configuration

The server runs in a Docker container with the following configuration:
- **Base Image**: Python 3.11-slim
- **Port**: 8000 (HTTP)
- **User**: Non-root user for security
- **Health Check**: Automatic health monitoring

## Troubleshooting

### Common Issues

1. **Authentication Failed**:
   - Verify your `ZOHO_CLIENT_ID` and `ZOHO_CLIENT_SECRET`
   - Check that your Zoho application has the correct scopes
   - Ensure your Zoho account has access to Sprints

2. **Server Won't Start**:
   - Check Docker logs: `docker compose logs zoho-sprints-mcp-server`
   - Verify environment variables are set
   - Check port 8000 is available

3. **API Calls Fail**:
   - Check authentication status
   - Verify project IDs and other parameters
   - Check Zoho Sprints API status

### Logs

```bash
# View server logs
docker compose logs zoho-sprints-mcp-server

# Follow logs in real-time
docker compose logs -f zoho-sprints-mcp-server
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the [Zoho Sprints API documentation](https://sprints.zoho.com/apidoc.html#Overview)
3. Open an issue in this repository

