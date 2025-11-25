"""
Fleet Summary API Endpoint
Provides aggregated metrics across all drivers
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
import pandas as pd
import numpy as np

from db import query_to_df

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/summary")
async def get_fleet_summary() -> Dict[str, Any]:
    """
    Get fleet-wide summary with aggregated metrics and top performers
    """
    try:
        logger.info("Fetching fleet summary")
        
        # Get all laps data
        laps_query = """
            SELECT 
                l.vehicle_id,
                l.lap_number,
                l.lap_time_ms,
                s.sector_1_time,
                s.sector_2_time,
                s.sector_3_time
            FROM laps l
            LEFT JOIN sectors s ON l.vehicle_number = s.vehicle_number AND l.lap_number = s.lap_number
            WHERE l.lap_number < 1000
            AND l.lap_time_ms > 30000
            ORDER BY l.vehicle_id, l.lap_number
        """
        
        df = query_to_df(laps_query)
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No fleet data available")
        
        # Convert to seconds
        df['lap_time'] = df['lap_time_ms'] / 1000.0
        
        # Fleet-wide metrics
        total_drivers = df['vehicle_id'].nunique()
        total_laps = len(df)
        fastest_lap = float(df['lap_time'].min())
        fastest_driver = df.loc[df['lap_time'].idxmin(), 'vehicle_id']
        avg_lap_time = float(df['lap_time'].mean())
        
        # Per-driver statistics
        driver_stats = []
        for vehicle_id in df['vehicle_id'].unique():
            driver_df = df[df['vehicle_id'] == vehicle_id]
            
            best_lap = float(driver_df['lap_time'].min())
            avg_lap = float(driver_df['lap_time'].mean())
            lap_count = len(driver_df)
            std_dev = float(driver_df['lap_time'].std())
            consistency = float(max(0, 100 - (std_dev / avg_lap * 100))) if avg_lap > 0 else 0
            
            driver_stats.append({
                'vehicle_id': vehicle_id,
                'best_lap': best_lap,
                'avg_lap': avg_lap,
                'lap_count': lap_count,
                'std_dev': std_dev,
                'consistency_score': consistency
            })
        
        # Sort by best lap for leaderboard
        driver_stats_sorted = sorted(driver_stats, key=lambda x: x['best_lap'])
        top_performers = driver_stats_sorted[:5]
        
        # Most consistent driver
        most_consistent = max(driver_stats, key=lambda x: x['consistency_score'])
        
        # Fleet consistency average
        fleet_consistency = float(np.mean([d['consistency_score'] for d in driver_stats]))
        
        # Get anomaly count (if DPTAD data exists)
        try:
            anomaly_query = "SELECT COUNT(*) as count FROM anomalies"
            anomaly_df = query_to_df(anomaly_query)
            total_anomalies = int(anomaly_df['count'].iloc[0]) if not anomaly_df.empty else 0
        except:
            total_anomalies = 0
        
        # Generate AI session insights
        ai_insights = _generate_session_insights(
            total_drivers, total_laps, fastest_lap, fastest_driver,
            avg_lap_time, fleet_consistency, top_performers, most_consistent
        )
        
        return {
            "fleet_metrics": {
                "total_drivers": total_drivers,
                "total_laps": total_laps,
                "fastest_lap": fastest_lap,
                "fastest_driver": fastest_driver,
                "avg_lap_time": avg_lap_time,
                "fleet_consistency": fleet_consistency,
                "total_anomalies": total_anomalies
            },
            "top_performers": top_performers,
            "most_consistent": {
                "vehicle_id": most_consistent['vehicle_id'],
                "consistency_score": most_consistent['consistency_score'],
                "avg_lap": most_consistent['avg_lap']
            },
            "ai_insights": ai_insights,
            "session_info": {
                "track": "Circuit of the Americas (COTA)",
                "session_type": "Practice/Qualifying",
                "total_distance_km": round(total_laps * 5.513, 2)  # COTA lap length
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fleet summary failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_session_insights(
    total_drivers: int, total_laps: int, fastest_lap: float, fastest_driver: str,
    avg_lap_time: float, fleet_consistency: float, top_performers: list, most_consistent: dict
) -> Dict[str, Any]:
    """Generate AI-powered session insights"""
    
    # Try AI generation first
    try:
        from src.coaching.llm_client import GroqClient
        llm_client = GroqClient()
        
        if llm_client.client:
            prompt = f"""Analyze this racing session data and provide insights:

Session Overview:
- Total Drivers: {total_drivers}
- Total Laps: {total_laps}
- Fastest Lap: {fastest_lap:.3f}s by {fastest_driver}
- Average Lap Time: {avg_lap_time:.3f}s
- Fleet Consistency: {fleet_consistency:.1f}%

Top 3 Performers:
1. {top_performers[0]['vehicle_id']}: {top_performers[0]['best_lap']:.3f}s
2. {top_performers[1]['vehicle_id']}: {top_performers[1]['best_lap']:.3f}s
3. {top_performers[2]['vehicle_id']}: {top_performers[2]['best_lap']:.3f}s

Most Consistent: {most_consistent['vehicle_id']} ({most_consistent['consistency_score']:.1f}%)

Provide a 3-4 sentence session summary highlighting: 1) Overall performance level, 2) Standout performers, 3) Fleet consistency trends."""
            
            try:
                response = llm_client.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=200
                )
                
                ai_text = response.choices[0].message.content.strip()
                
                return {
                    "summary": ai_text,
                    "highlights": [
                        f"{fastest_driver} set the pace with {fastest_lap:.3f}s",
                        f"Fleet averaged {avg_lap_time:.3f}s with {fleet_consistency:.1f}% consistency",
                        f"{most_consistent['vehicle_id']} showed exceptional consistency"
                    ],
                    "generated_by": "AI (Groq LLaMA 3.3)"
                }
            except Exception as ai_error:
                logger.warning(f"AI insights generation failed: {ai_error}")
    except Exception as e:
        logger.warning(f"Could not load AI client: {e}")
    
    # Fallback to rule-based insights
    pace_gap = avg_lap_time - fastest_lap
    consistency_rating = "excellent" if fleet_consistency > 90 else "good" if fleet_consistency > 80 else "moderate"
    
    summary = f"The session saw {total_drivers} drivers complete {total_laps} laps at COTA. "
    summary += f"{fastest_driver} dominated with a {fastest_lap:.3f}s lap, {pace_gap:.3f}s faster than the fleet average. "
    summary += f"Overall fleet consistency was {consistency_rating} at {fleet_consistency:.1f}%, "
    summary += f"with {most_consistent['vehicle_id']} showing the most consistent performance."
    
    return {
        "summary": summary,
        "highlights": [
            f"Fastest: {fastest_driver} ({fastest_lap:.3f}s)",
            f"Fleet Average: {avg_lap_time:.3f}s",
            f"Most Consistent: {most_consistent['vehicle_id']} ({most_consistent['consistency_score']:.1f}%)"
        ],
        "generated_by": "Rule-based analysis"
    }
