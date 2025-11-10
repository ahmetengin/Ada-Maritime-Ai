"""Weather information and forecasting skill for marinas"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import random

from .base_skill import BaseSkill
from ..database.models import Weather
from ..database.interface import DatabaseInterface
from ..logger import setup_logger


logger = setup_logger(__name__)


class WeatherSkill(BaseSkill):
    """Skill for retrieving and analyzing weather information for marinas"""

    def __init__(self, database: DatabaseInterface):
        super().__init__()
        self.database = database
        self.name = "weather"
        self.description = "Get weather information and forecasts for marina locations"
        self.version = "1.0.0"
        self.author = "Ada Maritime AI"

    async def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute weather operations

        Operations:
            - current_weather: Get current weather at marina location
            - forecast: Get weather forecast for marina
            - sailing_conditions: Analyze sailing conditions
            - weather_alerts: Check for weather warnings

        Args:
            operation: The weather operation to perform
            parameters: Operation-specific parameters

        Returns:
            Operation results
        """
        logger.info(f"Executing weather operation: {operation}")

        if operation == "current_weather":
            return await self._get_current_weather(parameters)
        elif operation == "forecast":
            return await self._get_forecast(parameters)
        elif operation == "sailing_conditions":
            return await self._analyze_sailing_conditions(parameters)
        elif operation == "weather_alerts":
            return await self._check_weather_alerts(parameters)
        else:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}"
            }

    async def _get_current_weather(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get current weather for a marina"""
        marina_id = params.get("marina_id")

        if not marina_id:
            return {"success": False, "error": "marina_id required"}

        marina = self.database.get_marina_by_id(marina_id)
        if not marina:
            return {"success": False, "error": f"Marina {marina_id} not found"}

        # In production, this would call a real weather API (OpenWeatherMap, etc.)
        weather = self._generate_mock_weather(marina.coordinates)

        return {
            "success": True,
            "marina_id": marina_id,
            "marina_name": marina.name,
            "location": f"{marina.city}, {marina.country}",
            "coordinates": marina.coordinates,
            "weather": {
                "temperature_celsius": weather.temperature_celsius,
                "feels_like_celsius": weather.temperature_celsius - 2,
                "wind_speed_knots": weather.wind_speed_knots,
                "wind_direction": weather.wind_direction,
                "wind_description": self._describe_wind(weather.wind_speed_knots),
                "wave_height_meters": weather.wave_height_meters,
                "visibility_km": weather.visibility_km,
                "conditions": weather.conditions,
                "timestamp": weather.timestamp,
                "humidity_percent": random.randint(40, 80),
                "pressure_hpa": random.randint(1000, 1020),
            }
        }

    async def _get_forecast(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather forecast for a marina"""
        marina_id = params.get("marina_id")
        days = params.get("days", 5)

        if not marina_id:
            return {"success": False, "error": "marina_id required"}

        marina = self.database.get_marina_by_id(marina_id)
        if not marina:
            return {"success": False, "error": f"Marina {marina_id} not found"}

        # Generate mock forecast
        forecast_days = []
        base_temp = 20 + random.uniform(-5, 10)

        for i in range(days):
            date = datetime.now() + timedelta(days=i)
            temp = base_temp + random.uniform(-3, 3)
            wind = random.uniform(5, 25)

            forecast_days.append({
                "date": date.strftime("%Y-%m-%d"),
                "day_name": date.strftime("%A"),
                "temperature_celsius": round(temp, 1),
                "temperature_high": round(temp + 3, 1),
                "temperature_low": round(temp - 3, 1),
                "wind_speed_knots": round(wind, 1),
                "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
                "wave_height_meters": round(random.uniform(0.2, 2.0), 1),
                "conditions": random.choice([
                    "Clear", "Partly Cloudy", "Cloudy",
                    "Light Rain", "Sunny"
                ]),
                "precipitation_chance": random.randint(0, 60)
            })

        return {
            "success": True,
            "marina_id": marina_id,
            "marina_name": marina.name,
            "location": f"{marina.city}, {marina.country}",
            "forecast_days": forecast_days
        }

    async def _analyze_sailing_conditions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current sailing conditions"""
        marina_id = params.get("marina_id")

        if not marina_id:
            return {"success": False, "error": "marina_id required"}

        marina = self.database.get_marina_by_id(marina_id)
        if not marina:
            return {"success": False, "error": f"Marina {marina_id} not found"}

        weather = self._generate_mock_weather(marina.coordinates)

        # Analyze conditions
        wind_speed = weather.wind_speed_knots
        wave_height = weather.wave_height_meters
        visibility = weather.visibility_km

        # Determine sailing suitability
        if wind_speed < 5:
            sailing_rating = "Poor"
            sailing_advice = "Very light winds, motoring may be necessary"
        elif wind_speed <= 15:
            sailing_rating = "Good"
            sailing_advice = "Good sailing conditions"
        elif wind_speed <= 25:
            sailing_rating = "Moderate"
            sailing_advice = "Moderate winds, experienced sailors recommended"
        else:
            sailing_rating = "Challenging"
            sailing_advice = "Strong winds, only experienced sailors should venture out"

        if wave_height > 2.0:
            sailing_advice += ". Rough seas, exercise caution."
        elif wave_height > 1.5:
            sailing_advice += ". Moderate seas."

        return {
            "success": True,
            "marina_id": marina_id,
            "marina_name": marina.name,
            "sailing_conditions": {
                "rating": sailing_rating,
                "advice": sailing_advice,
                "wind_speed_knots": wind_speed,
                "wind_direction": weather.wind_direction,
                "wave_height_meters": wave_height,
                "visibility_km": visibility,
                "conditions": weather.conditions,
                "safe_for_beginners": wind_speed <= 15 and wave_height <= 1.0,
                "timestamp": weather.timestamp
            }
        }

    async def _check_weather_alerts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check for weather warnings and alerts"""
        marina_id = params.get("marina_id")

        if not marina_id:
            return {"success": False, "error": "marina_id required"}

        marina = self.database.get_marina_by_id(marina_id)
        if not marina:
            return {"success": False, "error": f"Marina {marina_id} not found"}

        weather = self._generate_mock_weather(marina.coordinates)

        alerts = []

        # Check for alerts based on conditions
        if weather.wind_speed_knots > 30:
            alerts.append({
                "type": "gale_warning",
                "severity": "high",
                "title": "Gale Warning",
                "description": f"Strong winds of {weather.wind_speed_knots} knots expected",
                "issued_at": datetime.now().isoformat()
            })

        if weather.wave_height_meters > 3.0:
            alerts.append({
                "type": "rough_seas",
                "severity": "medium",
                "title": "Rough Seas Advisory",
                "description": f"Wave heights of {weather.wave_height_meters}m expected",
                "issued_at": datetime.now().isoformat()
            })

        if weather.visibility_km < 2.0:
            alerts.append({
                "type": "low_visibility",
                "severity": "medium",
                "title": "Low Visibility Warning",
                "description": f"Reduced visibility: {weather.visibility_km}km",
                "issued_at": datetime.now().isoformat()
            })

        return {
            "success": True,
            "marina_id": marina_id,
            "marina_name": marina.name,
            "alerts": alerts,
            "alert_count": len(alerts),
            "has_alerts": len(alerts) > 0
        }

    def _generate_mock_weather(self, coordinates: Dict[str, float]) -> Weather:
        """Generate mock weather data (in production, call real API)"""
        conditions = ["Clear", "Partly Cloudy", "Cloudy", "Light Rain", "Overcast"]
        wind_directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

        return Weather(
            temperature_celsius=round(15 + random.uniform(0, 15), 1),
            wind_speed_knots=round(random.uniform(5, 25), 1),
            wind_direction=random.choice(wind_directions),
            wave_height_meters=round(random.uniform(0.3, 2.5), 1),
            visibility_km=round(random.uniform(5, 20), 1),
            conditions=random.choice(conditions),
            timestamp=datetime.now().isoformat()
        )

    def _describe_wind(self, wind_speed_knots: float) -> str:
        """Describe wind conditions in Beaufort scale terms"""
        if wind_speed_knots < 1:
            return "Calm"
        elif wind_speed_knots < 4:
            return "Light air"
        elif wind_speed_knots < 7:
            return "Light breeze"
        elif wind_speed_knots < 11:
            return "Gentle breeze"
        elif wind_speed_knots < 17:
            return "Moderate breeze"
        elif wind_speed_knots < 22:
            return "Fresh breeze"
        elif wind_speed_knots < 28:
            return "Strong breeze"
        elif wind_speed_knots < 34:
            return "Near gale"
        elif wind_speed_knots < 41:
            return "Gale"
        elif wind_speed_knots < 48:
            return "Strong gale"
        elif wind_speed_knots < 56:
            return "Storm"
        else:
            return "Violent storm"
