"""
Laps API Endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from db import query_to_df
from db.utils import get_vehicle_number
import pandas as pd

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{vehicle_id}")
async def get_laps(vehicle_id: str) -> Dict[str, Any]:
    """
    Get all laps for a specific driver (cleaned)
    """
    try:
        v_num = get_vehicle_number(vehicle_id)
        
        # Query raw data
        query = f"""
            SELECT 
                l.lap_number,
                l.lap_time_ms,
                s.sector_1_time as sector_1,
                s.sector_2_time as sector_2,
                s.sector_3_time as sector_3
            FROM laps l
            LEFT JOIN sectors s ON l.vehicle_number = s.vehicle_number AND l.lap_number = s.lap_number
            WHERE l.vehicle_number = {v_num}
            ORDER BY l.lap_number
        """
        
        # Load to Pandas for cleaning
        df = query_to_df(query)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No laps found for {vehicle_id}")
            
        # Clean data
        df = df[df['lap_number'] < 1000]  # Filter out corrupted lap numbers
        df = df[df['lap_time_ms'] > 30000]  # Filter invalid short laps
        df = df.drop_duplicates(subset=['lap_number'])  # Remove duplicates
        
        # Convert ms to seconds
        df['lap_time'] = df['lap_time_ms'] / 1000.0
        
        # Select columns
        cols = ['lap_number', 'lap_time', 'sector_1', 'sector_2', 'sector_3']
        laps = df[cols].to_dict('records')
        
        return {
            "vehicle_id": vehicle_id,
            "laps": laps
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching laps for {vehicle_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
