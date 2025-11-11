"""
Check berth availability at marina.
Integrates with existing berth management skill.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta


def execute(
    marina_id: str,
    vessel_length: float,
    start_date: str,
    end_date: str,
    vessel_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Check berth availability for vessel.

    Args:
        marina_id: Marina identifier
        vessel_length: Vessel length in meters
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        vessel_type: Type of vessel (motor, sail, catamaran)

    Returns:
        Availability information and suitable berths
    """
    # Mock availability data
    available_berths = [
        {
            "berth_id": "A-12",
            "length": 15.0,
            "width": 5.0,
            "depth": 3.5,
            "type": "floating",
            "utilities": ["electricity", "water", "wifi"],
            "daily_rate": 150,
            "available": True
        },
        {
            "berth_id": "B-08",
            "length": 20.0,
            "width": 6.0,
            "depth": 4.0,
            "type": "fixed",
            "utilities": ["electricity", "water", "wifi", "cable_tv"],
            "daily_rate": 200,
            "available": True
        },
        {
            "berth_id": "C-15",
            "length": 25.0,
            "width": 7.0,
            "depth": 5.0,
            "type": "floating",
            "utilities": ["electricity", "water", "wifi", "pump_out"],
            "daily_rate": 250,
            "available": False
        }
    ]

    # Filter suitable berths
    suitable = [
        b for b in available_berths
        if b["length"] >= vessel_length and b["available"]
    ]

    # Calculate duration and total cost
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    days = (end - start).days

    for berth in suitable:
        berth["total_cost"] = berth["daily_rate"] * days

    return {
        "marina_id": marina_id,
        "vessel_length": vessel_length,
        "period": {
            "start": start_date,
            "end": end_date,
            "days": days
        },
        "available_berths": len(suitable),
        "berths": suitable,
        "recommendations": suitable[:2] if suitable else []
    }
