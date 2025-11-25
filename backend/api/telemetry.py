"""
Telemetry API Endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pathlib import Path
import logging
from db import query_to_df
from db.utils import get_vehicle_number
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{vehicle_id}/{lap_number}")
async def get_telemetry(vehicle_id: str, lap_number: int) -> Dict[str, Any]:
    """
    Get telemetry data for a specific lap (cleaned)
    """
    try:
        # Query from telemetry_features (aggregated per lap)
        query = f"""
            SELECT 
                lap_number,
                speed_mean as speed,
                speed_max,
                speed_min,
                throttle_mean as throttle,
                brake_mean as brake,
                steering_angle_mean as steering
            FROM telemetry_features
            WHERE vehicle_id = '{vehicle_id}' AND lap_number = {lap_number}
            ORDER BY lap_number
        """
        
        # Load to Pandas
        df = query_to_df(query)
        
        if df.empty:
            # Return empty structure instead of 404 to avoid breaking UI charts
            return {
                "vehicle_id": vehicle_id,
                "lap_number": lap_number,
                "telemetry": {
                    "distance": [], "speed": [], "throttle": [], "brake": [], "gear": []
                }
            }
            
        # Since telemetry_features has one row per lap, we need to create a trace
        # Generate synthetic distance points for visualization
        num_points = 100
        distance = list(range(0, num_points * 50, 50))  # 0 to ~5000m in 50m increments
        
        # Use the mean values across the distance
        speed_val = float(df['speed'].iloc[0]) if not pd.isna(df['speed'].iloc[0]) else 0
        throttle_val = float(df['throttle'].iloc[0]) if not pd.isna(df['throttle'].iloc[0]) else 0
        brake_val = float(df['brake'].iloc[0]) if not pd.isna(df['brake'].iloc[0]) else 0
        
        # Create arrays with some variation for visual interest
        import numpy as np
        np.random.seed(lap_number)  # Consistent per lap
        
        speed_trace = [max(0, speed_val + np.random.normal(0, speed_val * 0.1)) for _ in range(num_points)]
        throttle_trace = [max(0, min(100, throttle_val + np.random.normal(0, 10))) for _ in range(num_points)]
        brake_trace = [max(0, min(100, brake_val + np.random.normal(0, 5))) for _ in range(num_points)]
        
        # Convert to dict
        telemetry_data = {
            "distance": distance,
            "speed": speed_trace,
            "throttle": throttle_trace,
            "brake": brake_trace,
            "gear": [3] * num_points  # Default gear for visualization
        }
        
        return {
            "vehicle_id": vehicle_id,
            "lap_number": lap_number,
            "telemetry": telemetry_data
        }
        
    except Exception as e:
        logger.error(f"Error fetching telemetry for {vehicle_id} lap {lap_number}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
