# Makefile for Zoho Sprints MCP Server
# Commands to prepare environment before starting Claude Desktop

.PHONY: help build start stop restart test clean logs status setup verify

# Default target
help:
	@echo "Zoho Sprints MCP Server - Available Commands:"
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup     - Complete setup: build, start, and verify MCP server"
	@echo "  build     - Build the Docker container"
	@echo "  start     - Start the MCP server container"
	@echo "  stop      - Stop the MCP server container"
	@echo "  restart   - Restart the MCP server container"
	@echo ""
	@echo "Verification Commands:"
	@echo "  test      - Run all tests"
	@echo "  verify    - Verify MCP server is working correctly"
	@echo "  status    - Check container status"
	@echo "  logs      - Show container logs"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  clean     - Stop containers and remove images"
	@echo "  rebuild   - Clean and rebuild everything from scratch"
	@echo ""
	@echo "Usage:"
	@echo "  make setup    # Complete setup before starting Claude Desktop"
	@echo "  make verify   # Quick verification that everything works"

# Complete setup - run this before starting Claude Desktop
setup: build start verify
	@echo "✅ MCP Server setup complete!"
	@echo "🚀 You can now start Claude Desktop and connect to the MCP server"

# Build the Docker container
build:
	@echo "🔨 Building Docker container..."
	docker compose build
	@echo "✅ Build complete"

# Start the MCP server container
start:
	@echo "🚀 Starting MCP server container..."
	docker compose up -d
	@echo "✅ Container started"

# Stop the MCP server container
stop:
	@echo "🛑 Stopping MCP server container..."
	docker compose down
	@echo "✅ Container stopped"

# Restart the MCP server container
restart: stop start
	@echo "✅ Container restarted"

# Run all tests
test:
	@echo "🧪 Running tests..."
	docker compose exec zoho-sprints-mcp-server bash -c "cd tests && python -m pytest -v"
	@echo "✅ Tests complete"

# Run tests with coverage
test-coverage:
	@echo "🧪 Running tests with coverage..."
	docker compose exec zoho-sprints-mcp-server bash -c "cd tests && python -m pytest --cov=../src --cov-report=term-missing"
	@echo "✅ Coverage report complete"

# Verify MCP server is working correctly
verify: status
	@echo "🔍 Verifying MCP server..."
	@echo "Testing HTTP endpoint..."
	@curl -f http://localhost:8000/health > /dev/null 2>&1 || (echo "❌ Health check failed" && exit 1)
	@echo "✅ MCP server verification complete"

# Check container status
status:
	@echo "📊 Container status:"
	docker compose ps
	@echo ""

# Show container logs
logs:
	@echo "📋 Container logs:"
	docker compose logs zoho-sprints-mcp-server

# Clean up containers and images
clean:
	@echo "🧹 Cleaning up containers and images..."
	docker compose down --rmi all --volumes --remove-orphans
	@echo "✅ Cleanup complete"

# Rebuild everything from scratch
rebuild: clean build start verify
	@echo "✅ Complete rebuild finished"

# Quick health check
health:
	@echo "🏥 Health check..."
	@curl -f http://localhost:8000/health > /dev/null 2>&1 && echo "✅ Server is healthy" || echo "❌ Server is not responding"

# Show project path for Claude Desktop configuration
path:
	@echo "📁 Project path for Claude Desktop configuration:"
	@echo "Current directory: $(shell pwd)"
	@echo ""
	@echo "For StreamableHttp transport, use this configuration in Claude Desktop:"
	@echo '{'
	@echo '  "mcpServers": {'
	@echo '    "zoho-sprints": {'
	@echo '      "command": "mcp-remote",'
	@echo '      "args": ["http://localhost:8000/mcp"],'
	@echo '      "env": {}'
	@echo '    }'
	@echo '  }'
	@echo '}'

# Development workflow
dev: build start
	@echo "🔧 Development environment ready"
	@echo "📝 Make changes in src/ directory"
	@echo "🔄 Run 'make restart' to apply changes"

# Production-like setup
prod: build start
	@echo "🚀 Production environment ready"
	@echo "📊 Monitor with: make status, make logs, make health"
