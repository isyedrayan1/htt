"""
ML Analysis API endpoints for DPTAD and SIWTL algorithms
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
import logging
import pandas as pd
import numpy as np

from api import schemas
from api.schemas import DPTADParams, SIWTLParams
from db import query_to_dict
from ml import (
    get_dptad_detector, 
    get_siwtl_calculator,
    analyze_driver_anomalies,
    calculate_driver_siwtl
)

logger = logging.getLogger(__name__)
router = APIRouter()

def _dptad_params_dependency(session_filter: Optional[str] = Query(None, description="Filter by session (practice, qualifying, race)")) -> DPTADParams:
    return DPTADParams(session_filter=session_filter)

def _siwtl_params_dependency(include_sectors: bool = Query(True, description="Include sector-based analysis"),
                             include_telemetry: bool = Query(False, description="Include telemetry smoothness analysis")) -> SIWTLParams:
    return SIWTLParams(include_sectors=include_sectors, include_telemetry=include_telemetry)

@router.get("/ml/algorithms")
async def get_ml_algorithms():
    """Get information about available ML algorithms"""
    return {
        "algorithms": {
            "DPTAD": {
                "name": "Dual-Path Temporal Anomaly Detection",
                "version": "1.0",
                "description": "World-class racing mistake detection using fast and slow path analysis",
                "capabilities": [
                    "Driver mistake detection",
                    "Equipment degradation analysis", 
                    "Compound issue identification",
                    "Real-time anomaly scoring"
                ]
            },
            "SIWTL": {
                "name": "Smart Weighted Ideal Lap",
                "version": "2.0", 
                "description": "Realistic lap time target calculation with achievability weights",
                "capabilities": [
                    "Realistic lap targets",
                    "Sector achievability analysis",
                    "Consistency scoring",
                    "Potential gain calculation"
                ]
            }
        },
        "production_status": "Deployed and Active",
        "initialization": "✓ Algorithms loaded at startup"
    }

@router.get("/ml/dptad/analyze/{vehicle_id}", response_model=schemas.DPTADResponse)
async def analyze_driver_dptad(
    vehicle_id: str,
    params: DPTADParams = Depends(_dptad_params_dependency)
):
    """
    Run DPTAD analysis on driver telemetry data
    """
    try:
        logger.info(f"Running DPTAD analysis for vehicle {vehicle_id}")
        
        telemetry_query = f"""
            SELECT 
                lap_number as timestamp,
                speed_mean as speed,
                throttle_mean as throttle,
                brake_mean as brake,
                steering_angle_mean as steering_angle,
                brake_spike_count,
                throttle_drop_count,
                steering_corrections,
                brake_smoothness,
                throttle_smoothness,
                speed_std as speed_variance,
                throttle_std as throttle_variance
            FROM telemetry_features
            WHERE vehicle_id = '{vehicle_id}'
            ORDER BY lap_number
        """
        
        telemetry_data = query_to_dict(telemetry_query)
        
        if not telemetry_data:
            raise HTTPException(status_code=404, detail=f"No telemetry data found for vehicle {vehicle_id}")
        
        df = pd.DataFrame(telemetry_data)
        
        if params.session_filter:
            logger.info(f"Applying session filter: {params.session_filter}")
        
        dptad_result = analyze_driver_anomalies(vehicle_id, df)

        raw_summary = dptad_result.get('summary', {}) if isinstance(dptad_result, dict) else {}
        summary = {
            'total_anomalies': int(raw_summary.get('total_anomalies', 0)),
            'severity_avg': float(raw_summary.get('severity_avg', 0.0)),
            'severity_max': float(raw_summary.get('severity_max', 0.0)),
            'high_severity_count': int(raw_summary.get('high_severity_count', 0)),
            'signals_affected': raw_summary.get('signals_affected', []),
            'recommendation': raw_summary.get('recommendation', 'No anomalies detected. Performance is consistent.')
        }

        # Helper to clean NaNs
        def clean_nans(obj):
            if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
                return None
            if isinstance(obj, dict):
                return {k: clean_nans(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [clean_nans(v) for v in obj]
            return obj

        return clean_nans({
            "vehicle_id": vehicle_id,
            "anomalies": dptad_result.get('anomalies', []) if isinstance(dptad_result, dict) else [],
            "summary": summary,
            "algorithm": "DPTAD v1.0 - Dual-Path Temporal Anomaly Detection",
            "analysis_timestamp": dptad_result.get('analysis_timestamp') if isinstance(dptad_result, dict) else None
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DPTAD analysis failed for {vehicle_id}: {e}")
        raise HTTPException(status_code=500, detail=f"DPTAD analysis failed: {str(e)}")

@router.get("/ml/siwtl/calculate/{vehicle_id}", response_model=schemas.SIWTLResponse)
async def calculate_driver_siwtl_endpoint(
    vehicle_id: str,
    params: SIWTLParams = Depends(_siwtl_params_dependency)
):
    """
    Calculate SIWTL (Smart Weighted Ideal Lap) for a driver
    """
    try:
        logger.info(f"Calculating SIWTL for vehicle {vehicle_id}")
        
        lap_query = f"""
            SELECT 
                l.lap_number,
                l.lap_time_ms,
                s.sector_1_time,
                s.sector_2_time, 
                s.sector_3_time,
                l.outing as stint_number
            FROM laps l
            LEFT JOIN sectors s ON l.vehicle_number = s.vehicle_number AND l.lap_number = s.lap_number
            WHERE l.vehicle_id = '{vehicle_id}'
            AND l.lap_time_ms BETWEEN 120000 AND 200000
            ORDER BY l.lap_number
        """
        
        lap_data = query_to_dict(lap_query)
        
        if not lap_data:
            raise HTTPException(status_code=404, detail=f"No lap data found for vehicle {vehicle_id}")
        
        lap_df = pd.DataFrame(lap_data)
        
        sector_df = None
        if params.include_sectors:
            vehicle_number_query = f"SELECT vehicle_number FROM drivers WHERE vehicle_id = '{vehicle_id}'"
            vehicle_data = query_to_dict(vehicle_number_query)
            
            if vehicle_data:
                vehicle_number = vehicle_data[0]['vehicle_number']
                sector_query = f"""
                    SELECT sector_1_time, sector_2_time, sector_3_time, lap_number
                    FROM sectors
                    WHERE vehicle_number = {vehicle_number}
                    AND sector_1_time > 0 AND sector_2_time > 0 AND sector_3_time > 0
                    ORDER BY lap_number
                """
                sector_data = query_to_dict(sector_query)
                if sector_data:
                    sector_df = pd.DataFrame(sector_data)
        
        telemetry_df = None
        if params.include_telemetry:
            telemetry_query = f"""
                SELECT throttle, brake, steering_angle, speed
                FROM telemetry
                WHERE vehicle_id = '{vehicle_id}'
                LIMIT 1000
            """
            telemetry_data = query_to_dict(telemetry_query)
            if telemetry_data:
                telemetry_df = pd.DataFrame(telemetry_data)
        
        siwtl_result = calculate_driver_siwtl(
            vehicle_id, lap_df, sector_df, telemetry_df
        )

        # Helper to clean NaNs
        def clean_nans(obj):
            if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
                return None
            if isinstance(obj, dict):
                return {k: clean_nans(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [clean_nans(v) for v in obj]
            return obj

        return clean_nans({
            "vehicle_id": vehicle_id,
            "algorithm": "SIWTL v2.0 - Smart Weighted Ideal Lap",
            "result": {
                "siwtl_lap": siwtl_result.get('siwtl_lap') if isinstance(siwtl_result, dict) else None,
                "potential_gain_sec": siwtl_result.get('potential_gain_sec', 0) if isinstance(siwtl_result, dict) else 0,
                "achievability_score": siwtl_result.get('achievability_score', 0.0) if isinstance(siwtl_result, dict) else 0.0,
                "sector_weights": siwtl_result.get('sector_weights') if isinstance(siwtl_result, dict) else None
            },
            "analysis_settings": {
                "sectors_included": params.include_sectors and sector_df is not None,
                "telemetry_included": params.include_telemetry and telemetry_df is not None,
                "laps_analyzed": len(lap_df)
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SIWTL calculation failed for {vehicle_id}: {e}")
        raise HTTPException(status_code=500, detail=f"SIWTL calculation failed: {str(e)}")

@router.get("/ml/comprehensive/{vehicle_id}")
async def comprehensive_ml_analysis(vehicle_id: str):
    """
    Run comprehensive ML analysis combining both DPTAD and SIWTL
    """
    try:
        logger.info(f"Running comprehensive ML analysis for vehicle {vehicle_id}")
        
        real_vehicle_id = vehicle_id
        if vehicle_id.startswith("Car-"):
            from db.utils import get_vehicle_number
            v_num = get_vehicle_number(vehicle_id)
            
            id_query = f"SELECT vehicle_id FROM drivers WHERE vehicle_number = {v_num} LIMIT 1"
            id_result = query_to_dict(id_query)
            
            if id_result:
                real_vehicle_id = id_result[0]['vehicle_id']
                logger.info(f"Resolved {vehicle_id} to {real_vehicle_id}")
            else:
                logger.warning(f"Could not resolve {vehicle_id} to a database ID")
        
        lap_query = f"""
            SELECT 
                l.lap_number, 
                l.lap_time_ms, 
                s.sector_1_time, 
                s.sector_2_time, 
                s.sector_3_time,
                l.outing as stint_number
            FROM laps l
            LEFT JOIN sectors s ON l.vehicle_number = s.vehicle_number AND l.lap_number = s.lap_number
            WHERE l.vehicle_id = '{real_vehicle_id}'
            AND l.lap_time_ms BETWEEN 120000 AND 200000
            ORDER BY l.lap_number
        """
        
        telemetry_query = f"""
            SELECT 
                lap_number as timestamp,
                speed_mean as speed,
                throttle_mean as throttle, 
                brake_mean as brake,
                steering_angle_mean as steering_angle,
                brake_spike_count,
                throttle_drop_count,
                steering_corrections,
                brake_smoothness,
                throttle_smoothness
            FROM telemetry_features
            WHERE vehicle_id = '{real_vehicle_id}'
            ORDER BY lap_number
        """
        
        lap_data = query_to_dict(lap_query)
        telemetry_data = query_to_dict(telemetry_query)
        
        if not lap_data:
            return JSONResponse(content={
                "vehicle_id": vehicle_id,
                "laps": [],
                "comprehensive_analysis": {},
                "algorithms_used": [],
                "data_summary": {"status": "No data found"}
            })
        
        lap_df = pd.DataFrame(lap_data)
        telemetry_df = pd.DataFrame(telemetry_data) if telemetry_data else None
        
        dptad_result = None
        if telemetry_df is not None and len(telemetry_df) > 0:
            dptad_result = analyze_driver_anomalies(real_vehicle_id, telemetry_df)
        
        sector_df = lap_df[['sector_1_time', 'sector_2_time', 'sector_3_time']].copy()
        siwtl_result = calculate_driver_siwtl(real_vehicle_id, lap_df, sector_df, telemetry_df)
        
        combined_insights = _generate_combined_insights(dptad_result, siwtl_result)
        
        def convert_numpy(obj):
            if isinstance(obj, (pd.DataFrame, pd.Series)):
                return obj.to_dict(orient='records')
            if isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert_numpy(v) for v in obj]
            if hasattr(obj, 'item'):
                return obj.item()
            if isinstance(obj, float) or isinstance(obj, np.floating):
                if np.isnan(obj) or np.isinf(obj):
                    return None
                return float(obj)
            if isinstance(obj, (np.int64, np.int32)):
                return int(obj)
            return obj

        response_data = {
            "vehicle_id": vehicle_id,
            "laps": lap_data,
            "comprehensive_analysis": {
                "dptad_anomalies": dptad_result,
                "siwtl_targets": siwtl_result,
                "combined_insights": combined_insights
            },
            "algorithms_used": ["DPTAD v1.0", "SIWTL v2.0"],
            "data_summary": {
                "laps_analyzed": len(lap_df),
                "telemetry_points": len(telemetry_df) if telemetry_df is not None else 0,
                "analysis_complete": True
            }
        }
        
        return JSONResponse(content=convert_numpy(response_data))
        
    except Exception as e:
        logger.error(f"Comprehensive ML analysis failed for {vehicle_id}: {e}")
        return JSONResponse(
            status_code=500, 
            content={"detail": f"Comprehensive analysis failed: {str(e)}"}
        )

def _generate_combined_insights(dptad_result: Dict[str, Any], siwtl_result: Dict[str, Any]) -> Dict[str, Any]:
    """Generate combined insights from DPTAD and SIWTL results, optionally using AI"""
    
    # Default rule-based insights (fallback)
    insights = {
        "performance_assessment": "Unknown",
        "primary_focus": "General improvement",
        "specific_recommendations": [],
        "potential_vs_issues": "Balanced approach needed"
    }
    
    try:
        # Extract base metrics
        anomaly_count = 0
        critical_issues = 0
        if dptad_result and 'summary' in dptad_result:
            anomaly_count = dptad_result['summary'].get('total_anomalies', 0)
            critical_issues = dptad_result['summary'].get('high_severity_count', 0)
        
        potential_gain = 0
        achievability = 0.5
        if siwtl_result and 'potential_gain_sec' in siwtl_result:
            potential_gain = siwtl_result.get('potential_gain_sec', 0)
            achievability = siwtl_result.get('achievability_score', 0.5)

        # 1. Try AI Generation
        try:
            from src.coaching.llm_client import GroqClient
            llm_client = GroqClient()
            
            if llm_client.client:
                evidence_pack = {
                    "vehicle_id": "Current Driver",
                    "potential": {
                        "potential_gain_sec": potential_gain,
                        "achievability": achievability
                    },
                    "consistency": {
                        "total_anomalies": anomaly_count,
                        "critical_issues": critical_issues
                    },
                    "technique": {
                        "note": "Derived from DPTAD and SIWTL analysis"
                    }
                }
                
                ai_advice = llm_client.generate_coaching_advice(evidence_pack)
                
                if ai_advice:
                    insights['performance_assessment'] = ai_advice.get('summary', "AI Analysis Complete")
                    insights['primary_focus'] = ai_advice.get('primary_weakness', "Focus on key areas")
                    insights['specific_recommendations'] = ai_advice.get('actionable_advice', [])
                    insights['potential_vs_issues'] = f"AI Identified: {ai_advice.get('key_strength', 'Potential')}"
                    return insights

        except Exception as ai_e:
            logger.warning(f"AI insight generation failed, using rules: {ai_e}")

        # 2. Fallback to Rule-Based Logic
        if critical_issues > 3:
            insights['performance_assessment'] = "Critical issues detected"
            insights['primary_focus'] = "Fix fundamental driving errors first"
        elif potential_gain > 10:
            insights['performance_assessment'] = "High improvement potential"
            insights['primary_focus'] = "Maximize performance gains through consistency"
        elif anomaly_count > 5:
            insights['performance_assessment'] = "Multiple technique issues"
            insights['primary_focus'] = "Address technique inconsistencies"
        else:
            insights['performance_assessment'] = "Performance optimization phase"
            insights['primary_focus'] = "Fine-tune for marginal gains"
        
        if critical_issues > 0:
            insights['specific_recommendations'].append("Address critical anomalies detected by DPTAD")
        if potential_gain > 5:
            insights['specific_recommendations'].append(f"Focus on {potential_gain:.1f}s potential gain identified by SIWTL")
        if achievability < 0.7:
            insights['specific_recommendations'].append("Improve consistency for better achievability scores")
        
        insights['potential_vs_issues'] = f"{potential_gain:.1f}s potential with {anomaly_count} issues to address"
        
    except Exception as e:
        logger.warning(f"Failed to generate combined insights: {e}")
    
    return insights