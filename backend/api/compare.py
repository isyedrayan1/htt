"""
Driver Comparison API Endpoint
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
import pandas as pd
import numpy as np

from db import query_to_df
from db.utils import get_vehicle_number

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{vehicle_id_1}/{vehicle_id_2}")
async def compare_drivers(vehicle_id_1: str, vehicle_id_2: str) -> Dict[str, Any]:
    """
    Compare two drivers head-to-head with comprehensive metrics
    """
    try:
        logger.info(f"Comparing {vehicle_id_1} vs {vehicle_id_2}")
        
        # Fetch lap data for both drivers
        laps_query_1 = f"""
            SELECT 
                l.lap_number,
                l.lap_time_ms,
                s.sector_1_time,
                s.sector_2_time,
                s.sector_3_time
            FROM laps l
            LEFT JOIN sectors s ON l.vehicle_number = s.vehicle_number AND l.lap_number = s.lap_number
            WHERE l.vehicle_id = '{vehicle_id_1}'
            AND l.lap_number < 1000
            AND l.lap_time_ms > 30000
            ORDER BY l.lap_number
        """
        
        laps_query_2 = f"""
            SELECT 
                l.lap_number,
                l.lap_time_ms,
                s.sector_1_time,
                s.sector_2_time,
                s.sector_3_time
            FROM laps l
            LEFT JOIN sectors s ON l.vehicle_number = s.vehicle_number AND l.lap_number = s.lap_number
            WHERE l.vehicle_id = '{vehicle_id_2}'
            AND l.lap_number < 1000
            AND l.lap_time_ms > 30000
            ORDER BY l.lap_number
        """
        
        df1 = query_to_df(laps_query_1)
        df2 = query_to_df(laps_query_2)
        
        if df1.empty or df2.empty:
            raise HTTPException(status_code=404, detail="Insufficient data for comparison")
        
        # Convert to seconds
        df1['lap_time'] = df1['lap_time_ms'] / 1000.0
        df2['lap_time'] = df2['lap_time_ms'] / 1000.0
        
        # Calculate metrics for driver 1
        driver1_metrics = {
            'best_lap': float(df1['lap_time'].min()),
            'avg_lap': float(df1['lap_time'].mean()),
            'worst_lap': float(df1['lap_time'].max()),
            'lap_count': len(df1),
            'std_dev': float(df1['lap_time'].std()),
            'consistency_score': float(max(0, 100 - (df1['lap_time'].std() / df1['lap_time'].mean() * 100))),
            'median_lap': float(df1['lap_time'].median())
        }
        
        # Calculate metrics for driver 2
        driver2_metrics = {
            'best_lap': float(df2['lap_time'].min()),
            'avg_lap': float(df2['lap_time'].mean()),
            'worst_lap': float(df2['lap_time'].max()),
            'lap_count': len(df2),
            'std_dev': float(df2['lap_time'].std()),
            'consistency_score': float(max(0, 100 - (df2['lap_time'].std() / df2['lap_time'].mean() * 100))),
            'median_lap': float(df2['lap_time'].median())
        }
        
        # Sector comparison
        sector_comparison = {}
        for sector in ['sector_1_time', 'sector_2_time', 'sector_3_time']:
            df1_sector = df1[df1[sector].notna() & (df1[sector] > 0)]
            df2_sector = df2[df2[sector].notna() & (df2[sector] > 0)]
            
            if not df1_sector.empty and not df2_sector.empty:
                sector_comparison[sector] = {
                    'driver1_avg': float(df1_sector[sector].mean()),
                    'driver2_avg': float(df2_sector[sector].mean()),
                    'driver1_best': float(df1_sector[sector].min()),
                    'driver2_best': float(df2_sector[sector].min()),
                    'delta': float(df1_sector[sector].mean() - df2_sector[sector].mean())
                }
        
        # Head-to-head statistics
        head_to_head = {
            'faster_best_lap': vehicle_id_1 if driver1_metrics['best_lap'] < driver2_metrics['best_lap'] else vehicle_id_2,
            'faster_avg_lap': vehicle_id_1 if driver1_metrics['avg_lap'] < driver2_metrics['avg_lap'] else vehicle_id_2,
            'more_consistent': vehicle_id_1 if driver1_metrics['consistency_score'] > driver2_metrics['consistency_score'] else vehicle_id_2,
            'best_lap_delta': abs(driver1_metrics['best_lap'] - driver2_metrics['best_lap']),
            'avg_lap_delta': abs(driver1_metrics['avg_lap'] - driver2_metrics['avg_lap'])
        }
        
        # Lap progression data for charts
        lap_progression = {
            'driver1': {
                'lap_numbers': df1['lap_number'].tolist(),
                'lap_times': df1['lap_time'].tolist()
            },
            'driver2': {
                'lap_numbers': df2['lap_number'].tolist(),
                'lap_times': df2['lap_time'].tolist()
            }
        }
        
        # Generate AI summary
        ai_summary = _generate_comparison_summary(
            vehicle_id_1, vehicle_id_2,
            driver1_metrics, driver2_metrics,
            head_to_head, sector_comparison
        )
        
        return {
            "vehicle_id_1": vehicle_id_1,
            "vehicle_id_2": vehicle_id_2,
            "driver1_metrics": driver1_metrics,
            "driver2_metrics": driver2_metrics,
            "sector_comparison": sector_comparison,
            "head_to_head": head_to_head,
            "lap_progression": lap_progression,
            "ai_summary": ai_summary,
            "comparison_timestamp": pd.Timestamp.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comparison failed for {vehicle_id_1} vs {vehicle_id_2}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_comparison_summary(
    vehicle_id_1: str, vehicle_id_2: str,
    driver1_metrics: Dict, driver2_metrics: Dict,
    head_to_head: Dict, sector_comparison: Dict
) -> Dict[str, Any]:
    """Generate AI-powered comparison summary"""
    
    # Try AI generation first
    try:
        from src.coaching.llm_client import GroqClient
        llm_client = GroqClient()
        
        if llm_client.client:
            comparison_context = {
                "driver1": vehicle_id_1,
                "driver2": vehicle_id_2,
                "driver1_best": driver1_metrics['best_lap'],
                "driver2_best": driver2_metrics['best_lap'],
                "driver1_avg": driver1_metrics['avg_lap'],
                "driver2_avg": driver2_metrics['avg_lap'],
                "driver1_consistency": driver1_metrics['consistency_score'],
                "driver2_consistency": driver2_metrics['consistency_score'],
                "faster_driver": head_to_head['faster_best_lap'],
                "more_consistent_driver": head_to_head['more_consistent'],
                "lap_delta": head_to_head['best_lap_delta']
            }
            
            prompt = f"""Analyze this head-to-head driver comparison and provide racing insights:

Driver 1 ({vehicle_id_1}):
- Best Lap: {driver1_metrics['best_lap']:.3f}s
- Average Lap: {driver1_metrics['avg_lap']:.3f}s
- Consistency: {driver1_metrics['consistency_score']:.1f}%

Driver 2 ({vehicle_id_2}):
- Best Lap: {driver2_metrics['best_lap']:.3f}s
- Average Lap: {driver2_metrics['avg_lap']:.3f}s
- Consistency: {driver2_metrics['consistency_score']:.1f}%

Provide a concise 3-4 sentence analysis covering: 1) Who has the pace advantage, 2) Who is more consistent, 3) Key strategic insights."""
            
            try:
                response = llm_client.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=200
                )
                
                ai_text = response.choices[0].message.content.strip()
                
                return {
                    "text": ai_text,
                    "key_findings": [
                        f"{head_to_head['faster_best_lap']} has the faster single-lap pace ({head_to_head['best_lap_delta']:.3f}s advantage)",
                        f"{head_to_head['more_consistent']} shows better consistency",
                        f"Average lap time advantage: {head_to_head['avg_lap_delta']:.3f}s"
                    ],
                    "generated_by": "AI (Groq LLaMA 3.3)"
                }
            except Exception as ai_error:
                logger.warning(f"AI summary generation failed: {ai_error}")
    except Exception as e:
        logger.warning(f"Could not load AI client: {e}")
    
    # Fallback to rule-based summary
    pace_advantage = head_to_head['faster_best_lap']
    consistency_advantage = head_to_head['more_consistent']
    
    summary_text = f"{pace_advantage} demonstrates superior single-lap pace with a {head_to_head['best_lap_delta']:.3f}s advantage. "
    summary_text += f"{consistency_advantage} shows better race consistency with a {max(driver1_metrics['consistency_score'], driver2_metrics['consistency_score']):.1f}% consistency score. "
    
    if pace_advantage == consistency_advantage:
        summary_text += f"{pace_advantage} has a clear overall advantage in both pace and consistency."
    else:
        summary_text += f"This creates an interesting dynamic where raw speed meets consistent execution."
    
    return {
        "text": summary_text,
        "key_findings": [
            f"{pace_advantage} has faster single-lap pace",
            f"{consistency_advantage} is more consistent",
            f"Best lap delta: {head_to_head['best_lap_delta']:.3f}s"
        ],
        "generated_by": "Rule-based analysis"
    }
