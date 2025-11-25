"""
Real-time Race Analytics API
Key endpoint for hackathon submission - provides streaming race simulation and live predictions
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List, Optional
import asyncio
import json
import logging
import time
from datetime import datetime

from db import query_to_dict

logger = logging.getLogger(__name__)
router = APIRouter()

class RaceReplay:
    """Replays real race data from the database"""
    
    def __init__(self):
        self.current_lap = 1
        self.max_laps = 20
        self.race_time = 0
        self.is_running = True
        
    async def get_live_telemetry(self, vehicle_id: str) -> Dict[str, Any]:
        """Get actual telemetry data for the current replay lap"""
        
        # Get actual data for this driver and lap
        query = f"""
            SELECT 
                lap_time_ms,
                lap_number
            FROM laps 
            WHERE vehicle_number = '{vehicle_id}'
            AND lap_number = {self.current_lap}
        """
        
        try:
            result = query_to_dict(query)
            if result:
                data = result[0]
                lap_time = data['lap_time_ms']
                # Simulate sector splits since they aren't in the DB
                s1 = lap_time * 0.33
                s2 = lap_time * 0.34
                s3 = lap_time * 0.33
            else:
                # Fallback if specific lap missing (e.g. DNF)
                lap_time = 0
                s1, s2, s3 = 0, 0, 0
                
        except Exception as e:
            logger.error(f"Error fetching telemetry for {vehicle_id}: {e}")
            lap_time = 0
            s1, s2, s3 = 0, 0, 0
            
        # Generate telemetry structure
        telemetry = {
            "vehicle_id": vehicle_id,
            "timestamp": datetime.now().isoformat(),
            "lap_number": self.current_lap,
            "sector_1": round(s1 / 1000, 2),
            "sector_2": round(s2 / 1000, 2),
            "sector_3": round(s3 / 1000, 2),
            "predicted_lap_time": round(lap_time / 1000, 2),
            # Add some simulated live values since we don't have high-freq telemetry in this table
            "throttle": 0.85, 
            "brake_pressure": 0.1,
            "speed": 220,
            "tire_temp_front": 100,
            "tire_temp_rear": 105,
            "fuel_remaining": max(0, 100 - (self.current_lap * 2.5)),
        }
        
        return telemetry
    
    def predict_pit_window(self, vehicle_id: str, telemetry: Dict) -> Dict[str, Any]:
        """Predict optimal pit stop window based on race progress"""
        
        fuel_remaining = telemetry.get("fuel_remaining", 50)
        
        # Simple logic for demo purposes
        urgency = "LOW"
        if fuel_remaining < 15:
            urgency = "HIGH"
        elif fuel_remaining < 30:
            urgency = "MEDIUM"
            
        return {
            "recommended_pit_lap": 12, # Fixed strategy for demo
            "urgency": urgency,
            "fuel_laps_remaining": round(fuel_remaining / 2.5, 1),
            "tire_degradation_pct": round((self.current_lap / 20) * 100, 1),
            "time_to_pit": 0
        }

# Global simulator instance
race_sim = RaceReplay()

@router.get("/live/summary")
async def get_live_race_summary() -> Dict[str, Any]:
    """Get current race state summary from DB"""
    
    # Get active drivers from database
    query = """
        SELECT DISTINCT vehicle_number 
        FROM laps 
        WHERE lap_time_ms > 30000 
        AND lap_number < 1000
        LIMIT 10
    """
    
    try:
        drivers = [row['vehicle_number'] for row in query_to_dict(query)]
    except:
        drivers = []
    
    # Generate live positions
    positions = []
    for i, driver in enumerate(drivers):
        telemetry = await race_sim.get_live_telemetry(driver)
        pit_prediction = race_sim.predict_pit_window(driver, telemetry)
        
        positions.append({
            "position": i + 1, # Simplified: just using list order for now
            "vehicle_id": driver,
            "current_lap": race_sim.current_lap,
            "last_lap_time": telemetry["predicted_lap_time"],
            "gap_to_leader": round(i * 1.5, 2),
            "pit_window": pit_prediction,
            "on_track": True
        })
    
    # Get Driver Analysis Metrics for Dashboard
    # We aggregate real stats here
    analysis_query = """
        SELECT 
            MIN(lap_time_ms)/1000.0 as best_lap,
            AVG(lap_time_ms)/1000.0 as avg_lap,
            STDDEV(lap_time_ms)/1000.0 as std_dev
        FROM laps
        WHERE lap_time_ms BETWEEN 90000 AND 200000
    """
    try:
        stats = query_to_dict(analysis_query)[0]
        theoretical_best = stats['best_lap'] - 0.5 # Simple heuristic
        potential_gain = round(stats['avg_lap'] - stats['best_lap'], 2)
        consistency = round(100 - (stats['std_dev'] * 2), 1)
    except:
        theoretical_best = 0
        potential_gain = 0
        consistency = 0

    return {
        "race_status": "GREEN",
        "current_lap": race_sim.current_lap,
        "total_laps": 20,
        "race_time": f"00:{race_sim.current_lap * 2:02d}",
        "positions": positions,
        "weather": {
            "track_temp": 42,
            "air_temp": 28,
            "humidity": 60,
            "wind_speed": 12
        },
        "driver_analysis": {
            "theoretical_best": f"{theoretical_best:.1f}",
            "potential_gain": f"+{potential_gain}s",
            "consistency_score": f"{consistency}%",
            "anomaly_count": "5" # Placeholder or fetch from anomalies table
        }
    }

@router.get("/live/telemetry/{vehicle_id}")
async def get_live_telemetry_endpoint(vehicle_id: str) -> Dict[str, Any]:
    """Get real-time telemetry for specific vehicle"""
    
    telemetry = await race_sim.get_live_telemetry(vehicle_id)
    pit_prediction = race_sim.predict_pit_window(vehicle_id, telemetry)
    
    return {
        "telemetry": telemetry,
        "predictions": {
            "pit_window": pit_prediction,
            "lap_time_trend": "STABLE",
            "tire_strategy": "BALANCED"
        },
        "insights": {
            "sector_performance": [
                {"sector": 1, "vs_best": 0.1},
                {"sector": 2, "vs_best": -0.2},
                {"sector": 3, "vs_best": 0.0}
            ],
            "strategy_recommendation": "Maintain pace"
        }
    }

@router.post("/live/advance")
async def advance_race_simulation() -> Dict[str, Any]:
    """Advance the race replay by one lap"""
    
    if race_sim.current_lap < race_sim.max_laps:
        race_sim.current_lap += 1
    else:
        race_sim.current_lap = 1 # Loop for demo
        
    return {
        "current_lap": race_sim.current_lap,
        "status": "Race advanced"
    }

@router.websocket("/live/stream")
async def race_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time race data streaming"""
    await websocket.accept()
    
    try:
        while True:
            # Send race summary
            summary = await get_live_race_summary()
            await websocket.send_text(json.dumps(summary))
            
            # Wait 5 seconds between updates
            await asyncio.sleep(5)
            
            # Auto-advance race every 10 seconds for demo flow
            # In a real replay, this might be faster or manual
            if int(time.time()) % 10 == 0:
                await advance_race_simulation()
                
    except WebSocketDisconnect:
        logger.info("Client disconnected from race stream")
    except Exception as e:
        logger.error(f"Error in race stream: {e}")
        await websocket.close()

@router.get("/strategy/pit-optimizer")
async def optimize_pit_strategy() -> Dict[str, Any]:
    """Pit stop strategy optimization"""
    
    # Get active drivers for strategy generation
    query = """
        SELECT DISTINCT vehicle_number 
        FROM laps 
        WHERE lap_time_ms > 30000 
        AND lap_number < 1000
        LIMIT 6
    """
    try:
        drivers = [row['vehicle_number'] for row in query_to_dict(query)]
    except:
        drivers = ["15", "23", "77"] # Fallback

    strategies = []
    for i, driver in enumerate(drivers):
        # Simulate different strategies based on position
        if i % 3 == 0:
            strategy_type = "UNDERCUT"
            pit_lap = race_sim.current_lap + 2
            confidence = 0.85
        elif i % 3 == 1:
            strategy_type = "OVERCUT"
            pit_lap = race_sim.current_lap + 5
            confidence = 0.75
        else:
            strategy_type = "AGGRESSIVE"
            pit_lap = race_sim.current_lap + 1
            confidence = 0.60
            
        strategies.append({
            "vehicle_id": driver,
            "current_position": i + 1,
            "strategy_type": strategy_type,
            "optimal_pit_lap": pit_lap,
            "predicted_time_loss": 22.5,
            "predicted_track_position": max(1, i + 1 - (1 if strategy_type == "UNDERCUT" else 0)),
            "confidence": confidence
        })
    
    return {
        "strategies": strategies,
        "race_conditions": {
            "safety_car_probability": 0.15,
            "weather_change_probability": 0.05,
            "track_evolution": "HIGH_DEGRADATION"
        },
        "recommendations": [
            "Monitor tire temps - High degradation detected",
            "Undercut window opening in 2 laps",
            "Traffic management critical for leaders"
        ]
    }