"""
Examples demonstrating MCP code execution for maritime AI.

Shows token savings and efficiency gains compared to traditional approach.
"""

import asyncio
from runtime import CodeExecutionRuntime


def example_1_vessel_tracking():
    """
    Example 1: Track and filter vessels

    Traditional approach:
    - Load all tool definitions: ~5,000 tokens
    - Return all vessels (100+ records): ~50,000 tokens
    - Filter in model context: another pass through
    Total: ~60,000 tokens

    Code execution approach:
    - Load only vessel_tracking tool: ~500 tokens
    - Filter locally, return summary: ~500 tokens
    Total: ~1,000 tokens
    Savings: 98.3%
    """

    runtime = CodeExecutionRuntime()

    code = """
# Search for vessel tracking tool
tools = search_tools("vessel", category="maritime")
print(f"Found {len(tools)} tools")

# Load vessel tracking
track_vessel = load_tool("maritime-data", "vessel_tracking")

# Get all vessels in region
vessels = track_vessel(region="Mediterranean")

# Process locally - filter large vessels only
large_vessels = [v for v in vessels if v['length'] > 100]

# Return concise summary (not raw data!)
result = {
    "total_vessels": len(vessels),
    "large_vessels": len(large_vessels),
    "average_speed": sum(v['speed'] for v in vessels) / len(vessels),
    "top_vessels": [
        {
            "name": v['name'],
            "length": v['length'],
            "destination": v['destination']
        }
        for v in sorted(large_vessels, key=lambda x: x['length'], reverse=True)[:3]
    ]
}
"""

    result = runtime.execute(code)

    print("=" * 60)
    print("Example 1: Vessel Tracking with Local Filtering")
    print("=" * 60)
    print(f"Success: {result.success}")
    print(f"Result: {result.result}")
    print(f"Tokens saved: {result.tokens_saved}")
    print(f"Execution time: {result.execution_time:.3f}s")
    print()


def example_2_marina_search():
    """
    Example 2: Find suitable marina berth

    Traditional: Load berth data → send to model → get recommendation
    Code execution: Filter locally, return only matches
    """

    runtime = CodeExecutionRuntime()

    code = """
# Find berth management tools
tools = search_tools("berth")
print(f"Found tools: {[t['name'] for t in tools]}")

# Load tools
check_availability = load_tool("berth-management", "check_availability")
port_info = load_tool("maritime-data", "port_info")

# Check availability at multiple marinas
vessel_length = 18.5
start = "2025-11-15"
end = "2025-11-20"

# Get marina info
marinas = port_info(country="Turkey")

# Check each marina (process locally!)
results = []
for marina in marinas:
    avail = check_availability(
        marina_id=marina['name'],
        vessel_length=vessel_length,
        start_date=start,
        end_date=end
    )

    if avail['available_berths'] > 0:
        best_berth = min(avail['berths'], key=lambda b: b['total_cost'])
        results.append({
            "marina": marina['name'],
            "city": marina['city'],
            "available": avail['available_berths'],
            "best_berth": best_berth['berth_id'],
            "cost": best_berth['total_cost'],
            "facilities": marina['facilities']
        })

# Return top 2 options
result = {
    "vessel_length": vessel_length,
    "period": f"{start} to {end}",
    "options_found": len(results),
    "recommendations": sorted(results, key=lambda x: x['cost'])[:2]
}
"""

    result = runtime.execute(code)

    print("=" * 60)
    print("Example 2: Marina Berth Search")
    print("=" * 60)
    print(f"Success: {result.success}")
    print(f"Result: {result.result}")
    print(f"Tokens saved: {result.tokens_saved}")
    print()


def example_3_weather_analysis():
    """
    Example 3: Weather analysis for voyage planning

    Process large forecast data locally, return only insights
    """

    runtime = CodeExecutionRuntime()

    code = """
# Load weather tool
forecast_tool = load_tool("weather", "marine_forecast")

# Get forecast for route (multiple points)
route_points = [
    (40.9823, 29.0456),  # Kalamış Marina
    (41.0245, 28.9785),  # Istanbul Marina
]

forecasts = []
for lat, lon in route_points:
    fc = forecast_tool(
        latitude=lat,
        longitude=lon,
        days=5,
        include_wind=True,
        include_waves=True
    )
    forecasts.append(fc)

# Analyze locally - find best departure window
good_conditions = []
for i, fc in enumerate(forecasts):
    for day in fc['forecast']:
        # Check if conditions are good
        if (day['wind']['speed'] < 15 and
            day['waves']['height'] < 2.0 and
            day['visibility'] == 'Good'):
            good_conditions.append({
                "point": i,
                "date": day['date'],
                "wind": day['wind']['speed'],
                "waves": day['waves']['height']
            })

# Return summary
result = {
    "route_points": len(route_points),
    "forecast_days": 5,
    "good_weather_windows": len(good_conditions),
    "best_windows": good_conditions[:3],
    "warnings": forecasts[0].get('warnings', [])
}
"""

    result = runtime.execute(code)

    print("=" * 60)
    print("Example 3: Weather Analysis for Voyage")
    print("=" * 60)
    print(f"Success: {result.success}")
    print(f"Result: {result.result}")
    print(f"Tokens saved: {result.tokens_saved}")
    print()


def example_4_state_persistence():
    """
    Example 4: Multi-step task with state persistence

    Demonstrates maintaining state across multiple executions
    """

    runtime = CodeExecutionRuntime()

    # Step 1: Search for vessels and save favorites
    code1 = """
# Track vessels
track = load_tool("maritime-data", "vessel_tracking")
vessels = track(vessel_type="yacht")

# Save favorites
favorites = [v for v in vessels if v['length'] > 80]
save_state("favorite_vessels", favorites)

result = {
    "step": "search",
    "favorites_saved": len(favorites)
}
"""

    result1 = runtime.execute(code1)
    print("Step 1:", result1.result)

    # Step 2: Get weather for favorite vessels
    code2 = """
# Load favorites from previous step
favorites = load_state("favorite_vessels", [])

# Get weather for each
weather_tool = load_tool("weather", "marine_forecast")

weather_reports = []
for vessel in favorites:
    fc = weather_tool(
        latitude=vessel['latitude'],
        longitude=vessel['longitude'],
        days=1
    )
    weather_reports.append({
        "vessel": vessel['name'],
        "location": f"{vessel['latitude']}, {vessel['longitude']}",
        "conditions": fc['forecast'][0]['conditions'],
        "wind": fc['forecast'][0]['wind']['speed']
    })

result = {
    "step": "weather_check",
    "vessels_checked": len(favorites),
    "reports": weather_reports
}
"""

    result2 = runtime.execute(code2)

    print("=" * 60)
    print("Example 4: State Persistence")
    print("=" * 60)
    print(f"Step 2: {result2.result}")
    print(f"Total tokens saved: {runtime.get_total_tokens_saved()}")
    print()


def example_5_progressive_loading():
    """
    Example 5: Progressive tool discovery

    Shows how tools are loaded on-demand, not all at once
    """

    runtime = CodeExecutionRuntime()

    code = """
# Start with search - no tools loaded yet
all_servers = list_servers()
print(f"Available servers: {all_servers}")

# Search only when needed
maritime_tools = search_tools("", server="maritime-data")
print(f"Maritime tools: {len(maritime_tools)}")

weather_tools = search_tools("", server="weather")
print(f"Weather tools: {len(weather_tools)}")

# Load only what we need
port_tool = load_tool("maritime-data", "port_info")
ports = port_tool(country="Turkey")

result = {
    "servers_available": len(all_servers),
    "tools_discovered": len(maritime_tools) + len(weather_tools),
    "tools_loaded": 1,  # Only port_info
    "ports_found": len(ports)
}
"""

    result = runtime.execute(code)

    print("=" * 60)
    print("Example 5: Progressive Tool Loading")
    print("=" * 60)
    print(f"Result: {result.result}")
    print(f"Tools used: {result.tools_used}")
    print("(Note: Only 1 tool loaded vs. loading all definitions upfront)")
    print()


def run_all_examples():
    """Run all examples"""
    print("\n")
    print("=" * 60)
    print("MCP CODE EXECUTION EXAMPLES")
    print("Demonstrating efficient maritime AI operations")
    print("=" * 60)
    print("\n")

    example_1_vessel_tracking()
    example_2_marina_search()
    example_3_weather_analysis()
    example_4_state_persistence()
    example_5_progressive_loading()

    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_examples()
