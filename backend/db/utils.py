"""
Database Utilities
"""

def get_vehicle_number(vehicle_id: str) -> int:
    """
    Extract vehicle number from ID.
    Supports 'Car-2' -> 2 and 'GR86-002-2' -> 2
    """
    if vehicle_id.startswith("Car-"):
        return int(vehicle_id.replace("Car-", ""))
    elif vehicle_id.startswith("GR86-"):
        return int(vehicle_id.split("-")[-1])
    else:
        try:
            return int(vehicle_id)
        except ValueError:
            return 0

def format_vehicle_id(vehicle_number: int) -> str:
    """Format vehicle number as 'Car-X'"""
    return f"Car-{vehicle_number}"
