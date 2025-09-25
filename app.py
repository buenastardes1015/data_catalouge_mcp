from fastmcp import FastMCP  # user the FastMCP v2.0 implementation which is faster https://gofastmcp.com/getting-started/installation
import pandas as pd
from dotenv import load_dotenv
from logging_config import StreamingSafeRequestLoggingMiddleware, log_tool
from auth import TokenAuthMiddleware
import csv
import os
from dataclasses import dataclass
from typing import List, Optional
from fuzzywuzzy import fuzz, process

# Load environment variables from a .env file if present
load_dotenv()

@dataclass
class EventMatch:
    """Represents a matched interaction event from the data catalog."""
    event_name: str
    trigger: str
    confidence_score: float
    stream: str
    tool_area: str
    parameters: List[str]
    requirements_status: str
    requirements_link: str

# Global variable to cache loaded events
_cached_events = None

def load_interaction_events() -> List[dict]:
    """Load interaction events from CSV file and cache them."""
    global _cached_events

    if _cached_events is not None:
        return _cached_events

    csv_path = os.path.join(os.path.dirname(__file__), "data_catalouge", "interaction_events.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    events = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Parse parameters column (comma-separated values)
                params = []
                if row.get('Parameters'):
                    params = [p.strip() for p in row['Parameters'].split('\n') if p.strip()]

                events.append({
                    'event_name': row.get('Event name', '').strip(),
                    'trigger': row.get('Trigger', '').strip(),
                    'parameters': params,
                    'stream': row.get('Stream', '').strip(),
                    'tool_area': row.get('Tool/Area of site', '').strip(),
                    'relates_to': row.get('Relates to', '').strip(),
                    'requirements_status': row.get('Requirements Status', '').strip(),
                    'requirements_link': row.get('Requirements link', '').strip()
                })

        _cached_events = events
        return events

    except Exception as e:
        raise Exception(f"Error loading CSV file: {str(e)}")

def search_events(query: str, max_results: int = 10) -> List[EventMatch]:
    """Search for events matching the query using multiple strategies."""
    events = load_interaction_events()

    if not query.strip():
        return []

    query = query.lower().strip()
    matches = []

    for event in events:
        if not event['event_name']:  # Skip empty event names
            continue

        # Strategy 1: Exact match in event name (highest priority)
        event_name_lower = event['event_name'].lower()
        if query == event_name_lower:
            matches.append((event, 100.0, "exact_match"))
            continue

        # Strategy 2: Fuzzy match on event name
        name_score = fuzz.partial_ratio(query, event_name_lower)
        if name_score >= 70:
            matches.append((event, name_score, "fuzzy_name"))
            continue

        # Strategy 3: Keyword search in trigger description
        trigger_lower = event['trigger'].lower()
        if query in trigger_lower or any(word in trigger_lower for word in query.split()):
            trigger_score = fuzz.partial_ratio(query, trigger_lower)
            matches.append((event, min(trigger_score, 85), "trigger_match"))
            continue

        # Strategy 4: Search in tool area or relates_to
        tool_area_lower = event['tool_area'].lower()
        relates_to_lower = event['relates_to'].lower()

        if query in tool_area_lower or query in relates_to_lower:
            area_score = max(
                fuzz.partial_ratio(query, tool_area_lower),
                fuzz.partial_ratio(query, relates_to_lower)
            )
            matches.append((event, min(area_score, 75), "area_match"))

    # Sort by confidence score (descending) and take top results
    matches.sort(key=lambda x: x[1], reverse=True)

    result_matches = []
    for event, score, match_type in matches[:max_results]:
        result_matches.append(EventMatch(
            event_name=event['event_name'],
            trigger=event['trigger'],
            confidence_score=round(score, 1),
            stream=event['stream'],
            tool_area=event['tool_area'],
            parameters=event['parameters'][:10],  # Limit parameters to avoid huge responses
            requirements_status=event['requirements_status'],
            requirements_link=event['requirements_link']
        ))

    return result_matches

mcp = FastMCP(
    name="Data Catalog MCP",
    instructions="MCP server exposing information about the data catalog"
)



@mcp.tool
@log_tool
def add(a: int, b: int) -> dict:
    """Add two numbers and return the sum as {\"sum\": int}."""
    return {"sum": int(pd.DataFrame({"a": [a], "b": [b]}).eval("a+b").iloc[0])}


@mcp.tool
@log_tool
def get_event_descriptions() -> dict:
    """
    Return a mapping of all event names and their descriptions from the data catalog.
    The key is the event name, the value is the description.
    """
    event_descriptions = {
        "open_seasame": "Send when a user opens the xyz component",
        "show_more": "Event fired then user clicks on the show me more button",
        "see_more": "This event tracks when a users clicks a pagination link to view another set of results"
    }
    return event_descriptions


@mcp.tool
@log_tool
def search_interaction_events(query: str, max_results: int = 10) -> List[EventMatch]:
    """
    Search for interaction events in the data catalog that match the provided query.

    This tool searches through all available interaction events and returns those that best
    match your search query. It uses multiple search strategies including:
    - Exact event name matching
    - Fuzzy matching on event names
    - Keyword search in event triggers/descriptions
    - Search in tool areas and related functionality

    Args:
        query: The search term or description of what you're looking for (e.g., "wayfinder",
               "user clicks button", "outlet interaction", "search events")
        max_results: Maximum number of results to return (default: 10, max: 20)

    Returns:
        List of EventMatch objects containing:
        - event_name: The name of the matching event
        - trigger: When/how the event is triggered
        - confidence_score: How well it matches your query (0-100)
        - stream: Which data stream it belongs to (WS1-WS5)
        - tool_area: What part of the site/tool it relates to
        - parameters: List of data parameters captured by this event
        - requirements_status: Development/testing status
        - requirements_link: Link to detailed requirements documentation

    Example queries:
    - "wayfinder" - Find all wayfinder-related events
    - "outlet" - Find events related to outlet interactions
    - "user clicks" - Find click-based interaction events
    - "search" - Find all search-related events
    """
    if max_results > 20:
        max_results = 20

    try:
        results = search_events(query, max_results)
        return results
    except FileNotFoundError as e:
        return []
    except Exception as e:
        # Log the error but return empty results to avoid breaking the tool
        return []

app = mcp.http_app(path="/mcp")
app.add_middleware(StreamingSafeRequestLoggingMiddleware)
app.add_middleware(TokenAuthMiddleware)