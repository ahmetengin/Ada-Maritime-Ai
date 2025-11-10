"""
Marine weather forecast tool.
Provides weather forecasts for maritime operations.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta


def execute(
    latitude: float,
    longitude: float,
    days: int = 3,
    include_wind: bool = True,
    include_waves: bool = True,
    include_tides: bool = False
) -> Dict[str, Any]:
    """
    Get marine weather forecast for location.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        days: Number of days to forecast (1-7)
        include_wind: Include wind data
        include_waves: Include wave height/period data
        include_tides: Include tide information

    Returns:
        Weather forecast data
    """
    # Mock forecast data
    base_date = datetime.now()

    forecasts = []
    for i in range(min(days, 7)):
        date = base_date + timedelta(days=i)

        forecast = {
            "date": date.strftime("%Y-%m-%d"),
            "temperature": {
                "high": 22 + i,
                "low": 16 + i,
                "water": 19
            },
            "conditions": "Partly cloudy" if i % 2 == 0 else "Clear",
            "visibility": "Good" if i < 3 else "Moderate",
            "precipitation": 10 if i > 2 else 0
        }

        if include_wind:
            forecast["wind"] = {
                "speed": 10 + (i * 2),
                "direction": "NW" if i % 2 == 0 else "SW",
                "gusts": 15 + (i * 2)
            }

        if include_waves:
            forecast["waves"] = {
                "height": 1.0 + (i * 0.3),
                "period": 5 + i,
                "direction": "W"
            }

        if include_tides:
            forecast["tides"] = [
                {"time": "06:30", "type": "high", "height": 1.2},
                {"time": "12:45", "type": "low", "height": 0.3},
                {"time": "18:30", "type": "high", "height": 1.4},
                {"time": "00:45", "type": "low", "height": 0.4}
            ]

        forecasts.append(forecast)

    return {
        "location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "forecast": forecasts,
        "warnings": ["Small craft advisory in effect"] if days > 2 else []
    }
