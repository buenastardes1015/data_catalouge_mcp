# Data Catalog MCP Server — Friendly Overview

This project is a small, fast Model Context Protocol (MCP) server that exposes a few example "tools" over HTTP so MCP‑aware apps (like Claude Desktop and Cursor) can call them.

Think of it as a local micro‑service that an AI app can talk to. You decide what the tools do (query a database, call an API, read files, etc.), and the AI can invoke them safely through the MCP layer.

---

## What Is Here, In Plain Terms

- `app.py`: the main server. It defines the tools and serves them at the HTTP path `/mcp`.
- `auth.py`: simple token check so only callers that know your token can use the server.
- `logging_config.py`: logs requests and tool calls to the console and rotating log files.
- `data_catalouge/`: CSV files containing your website tracking event catalog.
- `Dockerfile` + `compose.yaml`: run the server in Docker on port `8005`.
- `requirements.txt` / `pyproject.toml`: Python dependencies; the project targets Python 3.12.
- `images/`: screenshots used by the README.
- `shared_data/`: created at runtime; holds logs by default (`shared_data/logs`).

You’ll interact with this repo by either:
1) running it locally with Python, or
2) running it via Docker Compose.

---

## How The Pieces Talk To Each Other

1) An MCP client (Claude Desktop, Cursor, etc.) connects to this server via HTTP at `http://localhost:8005/mcp` using the MCP protocol (usually through a small helper called `mcp-remote`).
2) The client asks for a list of tools, then calls a tool by name and passes inputs.
3) The server runs your Python function and returns the result.
4) Everything is logged; optional token auth can allow/deny requests.

---

## The Important Files

### `app.py`

Key points:
- Uses `FastMCP` to host tools and build an ASGI app.
- Defines three tools:
  - `add(a, b)`: adds two numbers and returns `{"sum": <number>}`.
  - `get_event_descriptions()`: returns a dictionary of event name → description.
  - `search_interaction_events()`: **NEW!** searches the data catalog for website tracking events.
- Wraps each tool with `@log_tool` to log every invocation and parameters.
- Exposes the HTTP app at `/mcp` and adds two middlewares:
  - `StreamingSafeRequestLoggingMiddleware` (request logs with request IDs)
  - `TokenAuthMiddleware` (simple shared‑secret style auth)

What a tool looks like (short version):

```python
@mcp.tool
@log_tool
def add(a: int, b: int) -> dict:
    """Add two numbers and return the sum as {"sum": int}."""
    return {"sum": a + b}
```

Tips for adding tools:
- Always decorate with `@mcp.tool` so clients can see/call it.
- Prefer simple, fast, idempotent actions (avoid long‑running work in requests).
- Use type hints and a clear docstring — clients surface this text in UI.

### `auth.py`

Lightweight protection for local use:
- Reads `AUTH_TOKEN` from environment (e.g., from a `.env` file).
- Accepts either `Authorization: Bearer <token>` header or `?token=<token>` query param.
- If `AUTH_TOKEN` is missing/empty, auth is disabled (requests are allowed).
- Writes auth decisions to `shared_data/logs/auth.log`.

This is intentionally simple. For production or remote use, put this behind proper TLS and a more robust auth/identity layer.

### `logging_config.py`

- Configures loggers that write to both console and rotating files under `LOG_DIR`.
- Defaults to `shared_data/logs` (created if missing). Override with `LOG_DIR` in `.env`.
- Adds an `x-request-id` header to responses so you can correlate logs with client calls.

Main log files:
- `requests.log`: one line per HTTP request
- `tools.log`: one line per tool invocation with parameters
- `auth.log`: auth enabled/disabled at startup, and unauthorized attempts

### `Dockerfile` and `compose.yaml`

- Builds a Python image, installs dependencies, runs `uvicorn` on port `8005`.
- `compose.yaml` maps `8005:8005` and mounts `./shared_data` so logs persist on your host.
- Loads environment variables from `.env`.

### `requirements.txt` and `pyproject.toml`

- `pyproject.toml` declares `requires-python = ">=3.12"` and a small set of core deps.
- `requirements.txt` pins concrete versions used for Docker/local installs.

---

## Running It Locally (short version)

Prerequisites: Python 3.12 installed.

1) Create a virtual environment in the repo folder:
   - Windows PowerShell:
     - `& "$Env:LocalAppData\Programs\Python\Python312\python.exe" -m venv .venv`
     - `\.\.venv\Scripts\Activate.ps1`
   - macOS/Linux:
     - `python3.12 -m venv .venv`
     - `source .venv/bin/activate`
2) Install dependencies:
   - `pip install -r requirements.txt`
3) (Optional) Copy environment file and set a token:
   - Windows: `copy example.env .env`
   - macOS/Linux: `cp example.env .env`
   - Edit `.env` and set `AUTH_TOKEN=your_secret_here`
4) Start the server:
   - `uvicorn app:app --host 0.0.0.0 --port 8005 --log-level debug`
5) Test quickly in a browser or curl:
   - If you set a token: `http://localhost:8005/mcp?token=your_secret_here`
   - Otherwise: `http://localhost:8005/mcp`

You won’t see a pretty web page; the MCP endpoint is meant for MCP clients, not humans. The useful output is in the logs and in your MCP client (Claude, Cursor, etc.).

---

## Using With Claude Desktop or Cursor

- Claude Desktop: add an MCP server config that runs `mcp-remote` and points it to `http://localhost:8005/mcp`.
- Cursor: similar idea under Settings → MCP & Integrations.

Exact copy‑paste configs are in `README.md` (look for “Update Claude desktop” and “In Cursor”). If you set `AUTH_TOKEN`, append `?token=YOUR_TOKEN` in the URL.

---

## Adding Your Own Tools

1) Open `app.py`.
2) Add a new Python function for your action, with type hints and a docstring.
3) Decorate it with `@mcp.tool` and `@log_tool`.
4) Return simple JSON‑serializable values (dicts, lists, strings, numbers).
5) Keep it quick — slow work should be offloaded or chunked.

Example — return the current server time:

```python
from datetime import datetime, timezone

@mcp.tool
@log_tool
def get_server_time() -> dict:
    """Return the current server time as {"iso": "..."}."""
    return {"iso": datetime.now(timezone.utc).isoformat()}
```

After saving, restart the server. Your MCP client will discover the new tool automatically.

---

## Environment Variables

Create `.env` to customize behavior. Common options:

- `AUTH_TOKEN`: if set, enables simple token auth. Provide it via header `Authorization: Bearer <token>` or append `?token=<token>` to the URL.
- `LOG_DIR`: where to write logs (defaults to `shared_data/logs`).

These are safe defaults for local work. Avoid placing secrets in logs or source control.

---

## Logs and Where To Find Them

- Default directory: `shared_data/logs/`
  - `requests.log` — one line per HTTP request with status and timing
  - `tools.log` — each tool call with parameters
  - `auth.log` — whether auth is on, plus unauthorized attempts

In Docker, `compose.yaml` mounts `./shared_data` so logs appear on your host machine too.

---

## Troubleshooting

- “Unauthorized” when testing: set `AUTH_TOKEN` and pass it in the header or as `?token=<token>`.
- Port already in use: something else may be using `8005`. Stop it or change the port in the `uvicorn` command and your MCP client config.
- Activation errors on Windows PowerShell: ensure the path is `\.\.venv\Scripts\Activate.ps1` (note the leading dot) and, if scripts are blocked, run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` once.

---

## What To Change First

1) Rename the server and its `instructions` in `app.py` to reflect your project.
2) Replace the sample tools with your real actions.
3) Set `AUTH_TOKEN` in `.env` before using this outside your machine.
4) Keep logs, but avoid printing sensitive data.

That's it — you now have a simple, extensible MCP server you can shape into your own.

---

## 🔍 Data Catalog Search Tool

This server now includes a powerful **interaction event search tool** that helps you discover and understand website tracking events from your data catalog.

### What It Does (Non-Technical Explanation)

**For Product Managers, Analysts & Stakeholders:**

Think of this as a smart search engine for your website's data tracking setup. When your website tracks user actions (like clicking buttons, viewing pages, or filling forms), each action has a specific "event" that gets recorded.

This tool lets you:
- **Ask questions in plain English** about what events exist
- **Discover tracking capabilities** you might not know about
- **Understand what data gets captured** for any user action
- **Find related events** for comprehensive tracking coverage

**Real-world scenarios:**
- *"What events track wayfinder usage?"* → Shows all wayfinder-related tracking
- *"How do we track outlet interactions?"* → Lists outlet_interaction, outlet_view, etc.
- *"What happens when users click buttons?"* → Finds all click-based events
- *"What tracking exists for search functionality?"* → Discovers all search events

### Technical Details

The `search_interaction_events` tool:
- **Searches 101 website tracking events** from `data_catalouge/interaction_events.csv`
- **Uses intelligent matching** with fuzzy search, exact matching, and keyword detection
- **Returns ranked results** with confidence scores (0-100)
- **Provides complete context** including event triggers, parameters, and requirements

### How To Use It

#### Via Claude Desktop/Cursor:
```
"What events track when users interact with providers?"
"Show me all wayfinder-related events"
"How do we track search behavior?"
"What events capture outlet interactions?"
```

#### Example Response Format:
Each search returns structured information:
- **Event Name**: `outlet_interaction`
- **Trigger**: When/how the event fires
- **Confidence Score**: How well it matches your query (85.2%)
- **Stream**: Which data stream (WS1-Website, WS2-FaP, etc.)
- **Tool Area**: What part of the site (Outlets, Wayfinder, etc.)
- **Parameters**: What data gets captured (`interaction_type`, `outlet_name`, etc.)
- **Requirements Status**: Development status (Ready for Dev, Tested, etc.)
- **Documentation Link**: Link to detailed requirements

### Data Coverage

The tool searches across:
- **101 interaction events** covering all website functionality
- **5 data streams**: WS1-Website, WS2-FaP, WS3-?, WS4-Fees & Costs, WS5-Supported Decisions
- **Multiple tool areas**: Wayfinder, Outlets, Providers, Search, My Guide, Budget Planner, etc.
- **Complete metadata**: Requirements status, documentation links, parameter lists

### Business Value

**For Data Teams:**
- Quickly discover existing tracking capabilities
- Avoid duplicate event implementation
- Understand parameter requirements
- Find gaps in tracking coverage

**For Product Teams:**
- Understand what user actions are being tracked
- Identify opportunities for new insights
- Validate tracking for new features
- Ensure comprehensive analytics coverage

**For Development Teams:**
- Find correct event names for implementation
- Understand parameter requirements
- Access requirement documentation quickly
- Ensure consistent event usage

This tool transforms a static CSV file into an intelligent, searchable knowledge base that makes your data catalog accessible to both technical and non-technical team members.

