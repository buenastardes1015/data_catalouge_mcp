# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Local Development
```bash
# Setup virtual environment (Python 3.12+ required)
python3.12 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.\.venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Run the server locally
uvicorn app:app --host 0.0.0.0 --port 8005 --log-level debug
```

### Docker Development
```bash
# Build and run with Docker Compose
docker compose build --no-cache server
docker compose up -d

# Stop the services
docker compose down
```

### Environment Setup
```bash
# Copy example environment file
cp example.env .env  # Linux/macOS
# or
copy example.env .env  # Windows

# Edit .env to set AUTH_TOKEN if authentication is desired
```

## Architecture Overview

This is a **Model Context Protocol (MCP) server** that exposes tools over HTTP for AI clients like Claude Desktop and Cursor. The server runs on port 8005 and serves the MCP endpoint at `/mcp`.

### Core Components

- **`app.py`**: Main server using FastMCP v2.0. Defines MCP tools and creates the HTTP app with middleware
- **`auth.py`**: Token-based authentication middleware (optional, controlled by `AUTH_TOKEN` env var)
- **`logging_config.py`**: Comprehensive logging setup with both console and rotating file outputs
- **`data_catalouge/`**: Additional modules for data catalog functionality (if present)

### Key Architectural Patterns

1. **Tool Definition**: All MCP tools are decorated with `@mcp.tool` and `@log_tool` for automatic registration and logging
2. **Middleware Stack**: Request logging and auth are handled via ASGI middleware, not affecting tool logic
3. **Environment Configuration**: Uses `python-dotenv` for `.env` file loading
4. **Logging Strategy**: Separate loggers for requests (`requests.log`), tools (`tools.log`), and auth (`auth.log`)

### MCP Tool Structure
```python
@mcp.tool
@log_tool
def your_tool(param: type) -> dict:
    """Tool description for AI clients."""
    return {"result": "data"}
```

### Authentication Flow
- If `AUTH_TOKEN` is set: requires `Authorization: Bearer <token>` header or `?token=<token>` query param
- If `AUTH_TOKEN` is empty/unset: authentication is disabled
- All auth decisions are logged to `auth.log`

### Client Integration
MCP clients connect via `mcp-remote` pointing to `http://localhost:8005/mcp`. Example configs are provided in README.md for:
- Claude Desktop
- Cursor IDE

### File Structure
- `shared_data/logs/`: Log files (created at runtime)
- `requirements.txt`: Pinned dependencies for consistent builds
- `pyproject.toml`: Project metadata, requires Python 3.12+
- `Dockerfile` + `compose.yaml`: Container deployment

The server is designed to be lightweight, fast, and easily extensible with new tools for data catalog operations.
- after each mayor tool/feature implementation I would like you to document is in @docs\OVERVIEW.md, before you do ask if the feature has passed QA and is the state is ready to be documented