"""
Coaching API Endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from db import get_coaching, get_ideal_lap, get_anomalies

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{vehicle_id}")
async def get_coaching_report(vehicle_id: str) -> Dict[str, Any]:
    """Get AI coaching report for a driver.

    Returns a dictionary with `vehicle_id`, `cards` (list of coaching cards),
    and a `summary` object. If no coaching data exists for the driver, an
    empty structure is returned so the frontend can display a friendly message
    instead of a 404 error.
    """
    try:
        # 1. Try to get cached coaching first as a base
        coaching = get_coaching(vehicle_id)
        
        # Resolve vehicle ID if needed (GR86 -> Car-X)
        real_vehicle_id = vehicle_id
        if not coaching and vehicle_id.startswith("GR86-"):
            from db import query_to_dict
            v_num_query = f"SELECT vehicle_number FROM drivers WHERE vehicle_id = '{vehicle_id}'"
            v_data = query_to_dict(v_num_query)
            if v_data:
                car_id = f"Car-{v_data[0]['vehicle_number']}"
                coaching = get_coaching(car_id)
                if coaching:
                    coaching['vehicle_id'] = vehicle_id
        
        # 2. If we have an API key, try to generate FRESH AI insights
        from src.coaching.llm_client import GroqClient
        llm_client = GroqClient()
        
        if llm_client.client:
            try:
                # Fetch fresh data for the AI
                from db import query_to_dict
                
                # Get SIWTL data
                ideal_lap = get_ideal_lap(vehicle_id) or {}
                
                # Get Anomalies
                anomalies = get_anomalies(vehicle_id) or []
                
                # Get recent telemetry stats
                telemetry_query = f"""
                    SELECT 
                        AVG(speed_mean) as avg_speed,
                        AVG(throttle_smoothness) as throttle_smoothness,
                        AVG(brake_smoothness) as brake_smoothness,
                        SUM(brake_spike_count) as brake_spikes,
                        SUM(throttle_drop_count) as throttle_drops
                    FROM telemetry_features
                    WHERE vehicle_id = '{vehicle_id}'
                """
                telemetry_stats = query_to_dict(telemetry_query)
                stats = telemetry_stats[0] if telemetry_stats else {}

                evidence_pack = {
                    "vehicle_id": vehicle_id,
                    "potential": {
                        "potential_gain_sec": ideal_lap.get('potential_gain', 0),
                        "theoretical_best": ideal_lap.get('theoretical_best_lap', 0),
                        "achievability": ideal_lap.get('achievability_score', 0)
                    },
                    "consistency": {
                        "total_anomalies": len(anomalies),
                        "brake_spikes": stats.get('brake_spikes', 0),
                        "throttle_drops": stats.get('throttle_drops', 0)
                    },
                    "technique": {
                        "brake_smoothness": stats.get('brake_smoothness', 0),
                        "throttle_smoothness": stats.get('throttle_smoothness', 0)
                    }
                }
                
                # Generate AI Advice
                ai_advice = llm_client.generate_coaching_advice(evidence_pack)
                
                # Construct/Update the coaching object
                if not coaching:
                    coaching = {"vehicle_id": vehicle_id, "cards": []}
                
                # Map AI response to frontend structure
                coaching["summary"] = {
                    "driver_name": f"Driver {vehicle_id}", # Placeholder name
                    "session_date": "2024-05-15", # Placeholder date
                    "track_name": "Circuit of the Americas",
                    "conditions": "Dry",
                    "executive_summary": ai_advice.get("summary", "No summary available.")
                }
                
                # Create cards from AI advice
                new_cards = []
                
                if "key_strength" in ai_advice:
                    new_cards.append({
                        "title": "Key Strength",
                        "category": "Technique",
                        "icon": "Brain",
                        "content": ai_advice["key_strength"],
                        "priority": "LOW",
                        "action_items": ["Maintain this advantage"],
                        "evidence": {
                            "consistency_score": f"{evidence_pack['consistency']['total_anomalies']} anomalies",
                            "technique_rating": "Solid"
                        },
                        "confidence": 92,
                        "potential_gain": 0.0
                    })
                    
                if "primary_weakness" in ai_advice:
                    new_cards.append({
                        "title": "Primary Focus Area",
                        "category": "Improvement",
                        "icon": "Target",
                        "content": ai_advice["primary_weakness"],
                        "priority": "HIGH",
                        "action_items": ai_advice.get("actionable_advice", []),
                        "evidence": {
                            "potential_gain": f"{evidence_pack['potential']['potential_gain_sec']:.2f}s",
                            "brake_spikes": evidence_pack['consistency']['brake_spikes'],
                            "throttle_drops": evidence_pack['consistency']['throttle_drops']
                        },
                        "confidence": 88,
                        "potential_gain": evidence_pack['potential']['potential_gain_sec']
                    })
                    
                if "drill" in ai_advice:
                     new_cards.append({
                        "title": "Recommended Drill",
                        "category": "Training",
                        "icon": "TrendingUp",
                        "content": ai_advice["drill"],
                        "priority": "MEDIUM",
                        "action_items": ["Practice in next session"],
                        "evidence": {
                            "focus": "Skill Acquisition",
                            "difficulty": "Intermediate"
                        },
                        "confidence": 95,
                        "potential_gain": 0.5
                    })
                
                coaching["cards"] = new_cards
                
            except Exception as ai_error:
                logger.error(f"AI Generation failed, falling back to cache: {ai_error}")
                # Fallback to existing coaching object (from cache) if AI fails
                pass

        if not coaching:
            # Fallback empty response
            return {
                "vehicle_id": vehicle_id,
                "cards": [],
                "summary": {}
            }
        return coaching
    except Exception as e:
        logger.error(f"Error fetching coaching for {vehicle_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{vehicle_id}/siwtl")
async def get_siwtl(vehicle_id: str) -> Dict[str, Any]:
    """Get SIWTL ideal lap analysis for a driver.

    Returns theoretical best lap, SIWTL lap, average lap, potential gain, and
    achievability score.
    """
    try:
        ideal_lap = get_ideal_lap(vehicle_id)
        if not ideal_lap:
            raise HTTPException(status_code=404, detail=f"SIWTL data not found for {vehicle_id}")
        return {
            "vehicle_id": vehicle_id,
            "theoretical_best": ideal_lap.get('theoretical_best_lap'),
            "siwtl_lap": ideal_lap.get('siwtl_lap'),
            "avg_lap": ideal_lap.get('avg_lap'),
            "potential_gain": ideal_lap.get('potential_gain'),
            "achievability_score": ideal_lap.get('achievability_score')
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching SIWTL for {vehicle_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{vehicle_id}/anomalies")
async def get_driver_anomalies(vehicle_id: str) -> Dict[str, Any]:
    """Get detected anomalies for a driver.

    Returns total count and a list of anomaly records.
    """
    try:
        anomalies = get_anomalies(vehicle_id)
        return {
            "vehicle_id": vehicle_id,
            "total_anomalies": len(anomalies),
            "anomalies": anomalies
        }
    except Exception as e:
        logger.error(f"Error fetching anomalies for {vehicle_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
