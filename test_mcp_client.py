#!/usr/bin/env python3
"""
Test script to verify MCP server functionality using proper FastMCP client.
"""
import asyncio
from fastmcp import Client

async def test_mcp_server():
    """Test the MCP server using proper client."""
    print("Testing MCP server with FastMCP client...")

    try:
        # Connect to the MCP server via HTTP
        client = Client("http://localhost:8005/mcp")

        async with client:
            print("SUCCESS: Connected to MCP server")

            # List all available tools
            tools = await client.list_tools()
            print(f"SUCCESS: Found {len(tools)} tools:")

            for i, tool in enumerate(tools, 1):
                print(f"  {i}. {tool.name}")
                print(f"     Description: {tool.description[:80]}...")

            # Check if our search tool exists
            search_tool = next((t for t in tools if t.name == 'search_interaction_events'), None)
            if search_tool:
                print(f"\nSUCCESS: Found search_interaction_events tool!")
                print(f"   Input schema: {search_tool.inputSchema}")

                # Test the search tool
                print(f"\nTesting search_interaction_events tool...")
                try:
                    result = await client.call_tool("search_interaction_events", {
                        "query": "wayfinder",
                        "max_results": 3
                    })
                    print(f"SUCCESS: Tool call successful!")
                    print(f"   Result type: {type(result)}")
                    if hasattr(result, 'content') and result.content:
                        content = result.content[0]
                        if hasattr(content, 'text'):
                            print(f"   Result preview: {str(content.text)[:200]}...")
                        else:
                            print(f"   Result content: {content}")
                    else:
                        print(f"   Result: {result}")

                except Exception as e:
                    print(f"FAIL: Tool call failed: {e}")

            else:
                print(f"\nFAIL: search_interaction_events tool not found!")
                print("Available tools:", [t.name for t in tools])

            # Test the add tool as well
            add_tool = next((t for t in tools if t.name == 'add'), None)
            if add_tool:
                print(f"\nTesting add tool...")
                try:
                    result = await client.call_tool("add", {"a": 5, "b": 3})
                    print(f"SUCCESS: Add tool result: {result}")
                except Exception as e:
                    print(f"FAIL: Add tool failed: {e}")

    except Exception as e:
        print(f"FAIL: Failed to connect to MCP server: {e}")
        print(f"   Make sure the server is running on http://localhost:8005")
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    if success:
        print(f"\nSUCCESS: MCP server test PASSED")
    else:
        print(f"\nFAIL: MCP server test FAILED")