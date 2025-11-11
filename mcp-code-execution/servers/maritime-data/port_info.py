"""
Port and marina information tool.
Returns details about ports, marinas, berths, and facilities.
"""

from typing import Optional, List, Dict, Any


def execute(
    port_name: Optional[str] = None,
    country: Optional[str] = None,
    port_type: Optional[str] = None,
    has_fuel: Optional[bool] = None
) -> List[Dict[str, Any]]:
    """
    Get port and marina information.

    Args:
        port_name: Name of port/marina
        country: Country code or name
        port_type: Type (marina, commercial, naval)
        has_fuel: Filter by fuel availability

    Returns:
        List of port information
    """
    # Mock data
    mock_ports = [
        {
            "name": "Kalamış Marina",
            "country": "Turkey",
            "city": "Istanbul",
            "type": "marina",
            "latitude": 40.9823,
            "longitude": 29.0456,
            "berths": 750,
            "max_length": 50,
            "depth": 4.5,
            "facilities": [
                "fuel", "water", "electricity", "wifi",
                "restaurant", "security", "customs"
            ],
            "services": [
                "maintenance", "repairs", "provisioning"
            ],
            "contact": {
                "phone": "+90-216-XXX-XXXX",
                "email": "info@kalamismarina.com",
                "vhf": "Channel 73"
            }
        },
        {
            "name": "Istanbul Marina",
            "country": "Turkey",
            "city": "Istanbul",
            "type": "marina",
            "latitude": 41.0245,
            "longitude": 28.9785,
            "berths": 420,
            "max_length": 80,
            "depth": 6.0,
            "facilities": [
                "fuel", "water", "electricity", "wifi",
                "restaurant", "hotel", "security"
            ],
            "services": [
                "maintenance", "repairs", "storage"
            ],
            "contact": {
                "phone": "+90-212-XXX-XXXX",
                "email": "info@istanbulmarina.com",
                "vhf": "Channel 71"
            }
        }
    ]

    results = mock_ports

    if port_name:
        results = [p for p in results if port_name.lower() in p["name"].lower()]

    if country:
        results = [p for p in results if country.lower() in p["country"].lower()]

    if port_type:
        results = [p for p in results if p["type"] == port_type]

    if has_fuel is not None:
        results = [p for p in results if ("fuel" in p["facilities"]) == has_fuel]

    return results
