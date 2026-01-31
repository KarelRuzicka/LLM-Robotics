import asyncio
import json
import urllib.request
from pydantic_ai import Agent, FunctionToolset, RunContext
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from datetime import datetime

toolset = FunctionToolset()


toolset.add_tool(duckduckgo_search_tool())

@toolset.tool
async def get_date_and_time(ctx: RunContext, question: str) -> str:
    """Provides the current date and time."""
    now = datetime.now()
    return f"The current date and time is: {now.strftime('%Y-%m-%d %H:%M:%S')}"

@toolset.tool
async def get_current_location(ctx: RunContext) -> str:
    """
    Returns an approximate location (city, region, country, coordinates).
    """
    def fetch():
        with urllib.request.urlopen("https://ipinfo.io/json", timeout=5) as resp:
            return json.load(resp)

    try:
        data = await asyncio.to_thread(fetch)

        city = data.get("city")
        region = data.get("region")
        country = data.get("country")
        loc = data.get("loc")


        return f"Approximate location: {city}, {region}, {country} (Coordinates: {loc})"
    except Exception:
        return "Could not determine rough location."