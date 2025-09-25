# Repository Guidelines

## Project Structure & Modules
- `app.py` — FastMCP HTTP server at `/mcp`; defines tools via `@mcp.tool`.
- `auth.py` — minimal ASGI token auth via `AUTH_TOKEN`.
- `logging_config.py` — request/tool logging and rotating file handlers.
- `Dockerfile`, `compose.yaml` — containerization (exposes `8005`).
- `requirements.txt`, `pyproject.toml` — Python deps (3.11–3.12; Docker uses 3.11, project targets 3.12).
- `images/` — docs screenshots. `shared_data/` — created at runtime for logs.

## Build, Test, and Development
- Setup (local): `uv pip install -r requirements.txt` (or `pip install -r requirements.txt`).
- Run (local): `uvicorn app:app --host 0.0.0.0 --port 8005 --log-level debug`.
- Env: `copy example.env .env` (Windows) or `cp example.env .env`, then edit as needed.
- Docker: `docker compose build --no-cache server` then `docker compose up -d`.

## Coding Style & Naming
- Python 3.11+ (pyproject targets 3.12). Use 4‑space indents and type hints, especially for tool inputs/outputs.
- Functions: `snake_case`; classes: `PascalCase`; constants: `UPPER_CASE`.
- Tools: decorate with `@mcp.tool` and `@log_tool`; write concise docstrings describing behavior and payloads.
- Logging: use logger utilities; avoid `print` in app code.
- Formatting: prefer Black defaults and Ruff if installed (not enforced in CI).

Example tool:
```python
@mcp.tool
@log_tool
def get_event_descriptions() -> dict:
    """Map event name -> description."""
    return {"example": "An example event."}
```

## Testing Guidelines
- Framework: pytest (recommended). Place tests under `tests/` named `test_*.py`.
- Run: `pytest -q`.
- Cover tool functions directly and, when needed, HTTP behavior against `/mcp` (e.g., with `httpx`).

## Commit & Pull Request Guidelines
- Commits: short, imperative subject (<=72 chars). Use conventional prefixes when helpful: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:` (consistent with existing history).
- PRs should include: clear description, linked issues, steps to test (local and Docker), and screenshots/log snippets for behavior changes.

## Security & Configuration
- `AUTH_TOKEN` enables Bearer auth. Require it for non‑local use; pass via header or `?token=`.
- Do not commit secrets or `.env`. Logs default to `shared_data/logs`; avoid logging sensitive data.
- Keep tools idempotent and fast; avoid long‑running or blocking work in request path.

