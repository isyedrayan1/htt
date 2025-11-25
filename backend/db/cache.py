"""
Cache Manager
Loads and caches JSON data for fast access
"""
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Global cache
_cache = {
    "coaching": {},
    "ideal_laps": {},
    "anomalies": {}
}

def load_cache():
    """Load JSON files into memory cache"""
    global _cache
    
    data_dir = Path(__file__).parent.parent.parent / "data"
    
    # Load coaching reports
    coaching_file = data_dir / "coaching" / "coaching_reports.json"
    if coaching_file.exists():
        with open(coaching_file, 'r') as f:
            _cache["coaching"] = json.load(f)
        logger.info(f"Loaded {len(_cache['coaching'])} coaching reports")
    
    # Load ideal laps (from parquet, convert to dict)
    try:
        import pandas as pd
        ideal_laps_file = data_dir / "analysis" / "ideal_laps.parquet"
        if ideal_laps_file.exists():
            df = pd.read_parquet(ideal_laps_file)
            # Convert to dict, handling duplicates by taking first occurrence
            for _, row in df.iterrows():
                vehicle_id = row['vehicle_id']
                if vehicle_id not in _cache["ideal_laps"]:
                    _cache["ideal_laps"][vehicle_id] = row.to_dict()
            logger.info(f"Loaded {len(_cache['ideal_laps'])} ideal lap records")
    except Exception as e:
        logger.error(f"Failed to load ideal laps: {e}")
    
    # Load anomalies (from parquet)
    try:
        import pandas as pd
        anomalies_file = data_dir / "anomalies" / "anomaly_events.parquet"
        if anomalies_file.exists():
            df = pd.read_parquet(anomalies_file)
            # Group by vehicle_id
            for vehicle_id in df['vehicle_id'].unique():
                vehicle_anomalies = df[df['vehicle_id'] == vehicle_id].to_dict('records')
                _cache["anomalies"][vehicle_id] = vehicle_anomalies
            logger.info(f"Loaded anomalies for {len(_cache['anomalies'])} drivers")
    except Exception as e:
        logger.error(f"Failed to load anomalies: {e}")

def get_coaching(vehicle_id: str):
    """Get coaching report for a driver"""
    return _cache["coaching"].get(vehicle_id)

def get_ideal_lap(vehicle_id: str):
    """Get ideal lap data for a driver"""
    return _cache["ideal_laps"].get(vehicle_id)

def get_anomalies(vehicle_id: str):
    """Get anomalies for a driver"""
    return _cache["anomalies"].get(vehicle_id, [])

def get_all_drivers():
    """Get list of all drivers with coaching data"""
    return list(_cache["coaching"].keys())
