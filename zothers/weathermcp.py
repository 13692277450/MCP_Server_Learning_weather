from typing import Any
import httpx  
import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP()
NWS_API_BASE = "https://api.weatherapi.io/"   #weatherapi data api
USER_AGENT = "weather-mcp/0.1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"HTTP error: {e}", file=sys.stderr)
            return None
        
def format_alert(feature: dict) -> str:
    props = feature["properties"]
    return f"""

Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown severity')}
Description: {props.get('description', 'Unknown description')}
Instruction: {props.get('instruction', 'Unknown instruction')}
"""

@mcp.tool()
async def get_alerts(state: str) -> str:
    url = f"{NWS_API_BASE}/alerts/active?state={state}"
    data = await make_nws_request(url)
    if not data or "features" not in data:
        return "No active alerts for this state."
    if not data["features"]:
        return "No active alerts for this state."
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n".join(alerts)
@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    point_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(point_url)
    if not points_data:
        return "No forecast available for this location."
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)
    if not forecast_data:
        return "No forecast available for this location."
    periods = forecast_data["properties"]["periods"]
    forecasts =[]
    for period in periods[:5]:
        forecasts.append(f"""
                         {period['name']}:
                         Temperature: {period['temperature']}°C
                         Humidity: {period['humidity']}%
                         Wind: {period['wind']} mph
                         Clouds: {period['clouds']}%
                         Rain: {period['rain']} mm
                         Snow: {period['snow']} mm
                         Weather: {period['weather']}
                         """
                         )
    return "\n-----\n".join(forecasts)

def main():
    print("Hello from weather!", file=sys.stderr)


if __name__ == "__main__":
    mcp.run(transport='stdio')
    
                         
                         
                         




                