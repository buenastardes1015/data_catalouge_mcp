# Claude Desktop Integration Guide

This guide shows how to connect your Data Catalog MCP server to Claude Desktop.

## Prerequisites

✅ Your MCP server is running on `http://localhost:8005/mcp` (confirmed working)
✅ Claude Desktop is installed on your system

## Step-by-Step Setup

### Step 1: Locate Claude Desktop Configuration File

The configuration file location depends on your operating system:

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### Step 2: Open/Create Configuration File

1. Navigate to the configuration directory
2. If `claude_desktop_config.json` doesn't exist, create it
3. Open the file in a text editor

### Step 3: Add Your MCP Server Configuration

Add this configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "data-catalog": {
      "url": "http://localhost:8005/mcp",
      "transport": "http"
    }
  }
}
```

### Step 4: Make Sure Your Server is Running

Before starting Claude Desktop, ensure your server is running:

```bash
cd C:\Users\praute\Dev\data_catalouge_mcp
uvicorn app:app --host 0.0.0.0 --port 8005 --log-level debug
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8005 (Press CTRL+C to quit)
```

### Step 5: Restart Claude Desktop

1. Close Claude Desktop completely
2. Start Claude Desktop again
3. Wait for it to connect to your MCP server

### Step 6: Test the Connection

In Claude Desktop, try asking:

```
"Search for wayfinder events in the data catalog"
```

or

```
"What interaction events are available in the data catalog?"
```

Claude should now be able to use your MCP tools:
- `add` - Add two numbers
- `get_event_descriptions` - Get all event descriptions
- `search_interaction_events` - Search for events by query

## Troubleshooting

### Problem: Claude Desktop can't connect

**Check:**
1. Your MCP server is running on port 8005
2. No firewall is blocking port 8005
3. Configuration file syntax is valid JSON

**Test server manually:**
```bash
python test_mcp_client.py
```

### Problem: Tools not appearing

**Check:**
1. Restart Claude Desktop after config changes
2. Check Claude Desktop logs for connection errors
3. Verify your server shows connection logs

### Problem: Authentication required

If you have `AUTH_TOKEN` set in your `.env` file, add it to the config:

```json
{
  "mcpServers": {
    "data-catalog": {
      "url": "http://localhost:8005/mcp",
      "transport": "http",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN_HERE"
      }
    }
  }
}
```

## Verification

Once connected, Claude Desktop will be able to:

✅ Search your interaction events catalog
✅ Get event descriptions
✅ Use fuzzy matching to find relevant events
✅ Return confidence scores and detailed event information

## Advanced Configuration

### Multiple MCP Servers

You can add multiple servers to the same config:

```json
{
  "mcpServers": {
    "data-catalog": {
      "url": "http://localhost:8005/mcp",
      "transport": "http"
    },
    "another-server": {
      "command": "python",
      "args": ["path/to/another/server.py"]
    }
  }
}
```

### Environment Variables

If your server needs environment variables:

```json
{
  "mcpServers": {
    "data-catalog": {
      "url": "http://localhost:8005/mcp",
      "transport": "http",
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

## Next Steps

Once connected, you can ask Claude to:
- Search for specific events like "outlet", "wayfinder", "search"
- Get descriptions of all available events
- Find events related to specific tools or areas of your site
- Get confidence scores for event matches

Your MCP server will provide Claude with real-time access to your data catalog!