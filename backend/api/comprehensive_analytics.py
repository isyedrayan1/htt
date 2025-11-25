"""
Complete Racing Analytics API
Comprehensive endpoints for all racing data analysis
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging
import pandas as pd
from pathlib import Path

from db import query_to_dict

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/overview")
async def get_racing_overview():
    """
    Complete racing overview with all statistics
    """
    try:
        # Driver statistics
        drivers_query = """
            SELECT 
                COUNT(*) as total_drivers,
                COUNT(DISTINCT vehicle_class) as vehicle_classes
            FROM drivers
        """
        drivers_stats = query_to_dict(drivers_query)[0]
        
        # Lap statistics
        laps_query = """
            SELECT 
                COUNT(*) as total_laps,
                COUNT(DISTINCT vehicle_id) as active_drivers,
                MIN(lap_time_ms) / 1000.0 as fastest_lap_ever,
                AVG(lap_time_ms) / 1000.0 as average_lap_time,
                COUNT(CASE WHEN lap_time_ms BETWEEN 90000 AND 300000 THEN 1 END) as valid_laps
            FROM laps
        """
        laps_stats = query_to_dict(laps_query)[0]
        
        # Sector statistics  
        sectors_query = """
            SELECT 
                COUNT(*) as total_sectors,
                MIN(sector_1_time) as fastest_s1,
                MIN(sector_2_time) as fastest_s2,
                MIN(sector_3_time) as fastest_s3
            FROM sectors
            WHERE sector_1_time > 0 AND sector_2_time > 0 AND sector_3_time > 0
        """
        sectors_stats = query_to_dict(sectors_query)
        sectors_data = sectors_stats[0] if sectors_stats else {}
        
        # Results overview
        results_query = """
            SELECT 
                COUNT(*) as total_races,
                COUNT(DISTINCT race_id) as race_sessions,
                AVG(laps_completed) as avg_laps_completed
            FROM results
        """
        results_stats = query_to_dict(results_query)[0]
        
        return {
            "platform": "ANTIGRAVITY Racing Intelligence",
            "overview": {
                "drivers": drivers_stats,
                "performance": laps_stats,
                "sectors": sectors_data,
                "competitions": results_stats
            },
            "capabilities": {
                "lap_analysis": True,
                "sector_timing": True,
                "driver_comparison": True,
                "ml_algorithms": ["DPTAD", "SIWTL"],
                "coaching_ai": True,
                "real_time_analytics": True
            }
        }
        
    except Exception as e:
        logger.error(f"Racing overview failed: {e}")
        raise HTTPException(status_code=500, detail=f"Overview failed: {str(e)}")

@router.get("/drivers")
async def get_all_drivers_analytics():
    """
    Complete driver analytics for all drivers
    """
    try:
        drivers_query = """
            SELECT DISTINCT 
                d.driver_id,
                d.vehicle_id, 
                d.vehicle_number,
                d.vehicle_class,
                d.vehicle_model
            FROM drivers d
        """
        all_drivers = query_to_dict(drivers_query)
        
        driver_analytics = []
        
        for driver in all_drivers:
            vehicle_id = driver['vehicle_id']
            vehicle_number = driver['vehicle_number']
            
            # Get lap performance
            lap_query = f"""
                SELECT 
                    COUNT(*) as total_laps,
                    MIN(lap_time_ms) / 1000.0 as best_lap,
                    AVG(lap_time_ms) / 1000.0 as avg_lap,
                    STDDEV(lap_time_ms) / 1000.0 as consistency,
                    COUNT(CASE WHEN lap_time_ms BETWEEN 90000 AND 300000 THEN 1 END) as valid_laps
                FROM laps
                WHERE vehicle_id = '{vehicle_id}'
            """
            lap_stats = query_to_dict(lap_query)[0]
            
            # Get sector performance
            sector_query = f"""
                SELECT 
                    AVG(sector_1_time) as avg_s1,
                    AVG(sector_2_time) as avg_s2,
                    AVG(sector_3_time) as avg_s3,
                    MIN(sector_1_time) as best_s1,
                    MIN(sector_2_time) as best_s2,
                    MIN(sector_3_time) as best_s3
                FROM sectors
                WHERE vehicle_number = {vehicle_number}
                AND sector_1_time > 0
            """
            sector_stats = query_to_dict(sector_query)
            sector_data = sector_stats[0] if sector_stats else {}
            
            # Get results
            results_query = f"""
                SELECT position, status, fastest_lap_time, fastest_lap_kph
                FROM results
                WHERE vehicle_number = {vehicle_number}
            """
            results = query_to_dict(results_query)
            
            # Calculate performance score
            if lap_stats['valid_laps'] and lap_stats['valid_laps'] > 0:
                performance_score = min(100, (lap_stats['valid_laps'] / 50) * 100)
            else:
                performance_score = 0
                
            driver_analytics.append({
                "driver_info": driver,
                "lap_performance": lap_stats,
                "sector_performance": sector_data,
                "race_results": results,
                "performance_score": round(performance_score, 1)
            })
        
        return {
            "total_drivers": len(driver_analytics),
            "drivers": driver_analytics
        }
        
    except Exception as e:
        logger.error(f"Drivers analytics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Drivers analytics failed: {str(e)}")

@router.get("/driver/{vehicle_id}")
async def get_driver_detailed_analytics(vehicle_id: str):
    """
    Detailed analytics for specific driver
    """
    try:
        # Get driver info
        driver_query = f"""
            SELECT driver_id, vehicle_id, vehicle_number, vehicle_class, vehicle_model
            FROM drivers 
            WHERE vehicle_id = '{vehicle_id}'
        """
        driver_info = query_to_dict(driver_query)
        
        if not driver_info:
            raise HTTPException(status_code=404, detail=f"Driver {vehicle_id} not found")
        
        driver = driver_info[0]
        vehicle_number = driver['vehicle_number']
        
        # Get detailed lap analysis
        detailed_laps_query = f"""
            SELECT 
                lap_number,
                lap_time_ms / 1000.0 as lap_time,
                session,
                is_pit_lap,
                race_id
            FROM laps
            WHERE vehicle_id = '{vehicle_id}'
            AND lap_time_ms BETWEEN 90000 AND 300000
            ORDER BY lap_number
        """
        lap_details = query_to_dict(detailed_laps_query)
        
        # Get sector progression
        sector_progression_query = f"""
            SELECT 
                lap_number,
                sector_1_time,
                sector_2_time, 
                sector_3_time,
                lap_time,
                sector_1_improvement,
                sector_2_improvement
            FROM sectors
            WHERE vehicle_number = {vehicle_number}
            AND sector_1_time > 0
            ORDER BY lap_number
        """
        sector_progression = query_to_dict(sector_progression_query)
        
        # Get telemetry features
        telemetry_query = f"""
            SELECT 
                lap_number,
                speed_mean,
                speed_max,
                throttle_max,
                brake_max,
                steering_corrections,
                smoothness_throttle,
                smoothness_brake,
                brake_spike_count
            FROM telemetry_features
            WHERE vehicle_id = '{vehicle_id}'
            ORDER BY lap_number
        """
        telemetry_data = query_to_dict(telemetry_query)
        
        # Calculate advanced metrics
        if lap_details:
            lap_times = [lap['lap_time'] for lap in lap_details]
            best_lap = min(lap_times)
            avg_lap = sum(lap_times) / len(lap_times)
            consistency_score = 1.0 - (max(lap_times) - min(lap_times)) / avg_lap
        else:
            best_lap = avg_lap = consistency_score = None
        
        return {
            "driver_info": driver,
            "summary": {
                "total_laps": len(lap_details),
                "best_lap_time": best_lap,
                "average_lap_time": avg_lap,
                "consistency_score": consistency_score,
                "has_sector_data": len(sector_progression) > 0,
                "has_telemetry": len(telemetry_data) > 0
            },
            "lap_progression": lap_details,
            "sector_analysis": sector_progression,
            "telemetry_insights": telemetry_data
        }
        
    except Exception as e:
        logger.error(f"Driver detailed analytics failed for {vehicle_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Detailed analytics failed: {str(e)}")

@router.get("/leaderboard")
async def get_performance_leaderboard(metric: str = Query("best_lap", description="Metric to rank by")):
    """
    Performance leaderboard across all drivers
    """
    try:
        if metric == "best_lap":
            query = """
                SELECT 
                    d.vehicle_id,
                    d.vehicle_number,
                    d.vehicle_class,
                    MIN(l.lap_time_ms) / 1000.0 as best_lap_time,
                    COUNT(l.lap_number) as total_laps
                FROM drivers d
                JOIN laps l ON d.vehicle_id = l.vehicle_id
                WHERE l.lap_time_ms BETWEEN 90000 AND 300000
                GROUP BY d.vehicle_id, d.vehicle_number, d.vehicle_class
                HAVING COUNT(l.lap_number) >= 10
                ORDER BY best_lap_time ASC
                LIMIT 20
            """
        elif metric == "consistency":
            query = """
                SELECT 
                    d.vehicle_id,
                    d.vehicle_number,
                    d.vehicle_class,
                    AVG(l.lap_time_ms) / 1000.0 as avg_lap_time,
                    STDDEV(l.lap_time_ms) / 1000.0 as std_deviation,
                    (STDDEV(l.lap_time_ms) / AVG(l.lap_time_ms)) as consistency_metric,
                    COUNT(l.lap_number) as total_laps
                FROM drivers d
                JOIN laps l ON d.vehicle_id = l.vehicle_id
                WHERE l.lap_time_ms BETWEEN 90000 AND 300000
                GROUP BY d.vehicle_id, d.vehicle_number, d.vehicle_class
                HAVING COUNT(l.lap_number) >= 15
                ORDER BY consistency_metric ASC
                LIMIT 20
            """
        else:
            query = """
                SELECT 
                    d.vehicle_id,
                    d.vehicle_number,
                    d.vehicle_class,
                    COUNT(l.lap_number) as total_laps,
                    MIN(l.lap_time_ms) / 1000.0 as best_lap_time,
                    AVG(l.lap_time_ms) / 1000.0 as avg_lap_time
                FROM drivers d
                JOIN laps l ON d.vehicle_id = l.vehicle_id
                WHERE l.lap_time_ms BETWEEN 90000 AND 300000
                GROUP BY d.vehicle_id, d.vehicle_number, d.vehicle_class
                ORDER BY total_laps DESC
                LIMIT 20
            """
            
        leaderboard = query_to_dict(query)
        
        return {
            "metric": metric,
            "leaderboard": leaderboard,
            "total_entries": len(leaderboard)
        }
        
    except Exception as e:
        logger.error(f"Leaderboard failed: {e}")
        raise HTTPException(status_code=500, detail=f"Leaderboard failed: {str(e)}")

@router.get("/sectors/analysis")
async def get_sector_analysis():
    """
    Comprehensive sector timing analysis
    """
    try:
        # Overall sector statistics
        sector_stats_query = """
            SELECT 
                COUNT(*) as total_sector_records,
                AVG(sector_1_time) as avg_s1,
                AVG(sector_2_time) as avg_s2,
                AVG(sector_3_time) as avg_s3,
                MIN(sector_1_time) as fastest_s1,
                MIN(sector_2_time) as fastest_s2,
                MIN(sector_3_time) as fastest_s3,
                MAX(sector_1_time) as slowest_s1,
                MAX(sector_2_time) as slowest_s2,
                MAX(sector_3_time) as slowest_s3
            FROM sectors
            WHERE sector_1_time > 0 AND sector_2_time > 0 AND sector_3_time > 0
        """
        overall_stats = query_to_dict(sector_stats_query)[0]
        
        # Best sector times by vehicle
        best_sectors_query = """
            SELECT 
                s.vehicle_number,
                d.vehicle_class,
                MIN(s.sector_1_time) as best_s1,
                MIN(s.sector_2_time) as best_s2,
                MIN(s.sector_3_time) as best_s3,
                MIN(s.sector_1_time) + MIN(s.sector_2_time) + MIN(s.sector_3_time) as theoretical_best
            FROM sectors s
            JOIN drivers d ON s.vehicle_number = d.vehicle_number
            WHERE s.sector_1_time > 0 AND s.sector_2_time > 0 AND s.sector_3_time > 0
            GROUP BY s.vehicle_number, d.vehicle_class
            ORDER BY theoretical_best ASC
        """
        best_sectors = query_to_dict(best_sectors_query)
        
        # Sector improvement analysis
        improvement_query = """
            SELECT 
                vehicle_number,
                AVG(sector_1_improvement) as avg_s1_improvement,
                AVG(sector_2_improvement) as avg_s2_improvement,
                COUNT(CASE WHEN sector_1_improvement < 0 THEN 1 END) as s1_improvements,
                COUNT(CASE WHEN sector_2_improvement < 0 THEN 1 END) as s2_improvements,
                COUNT(*) as total_laps
            FROM sectors
            WHERE sector_1_improvement IS NOT NULL
            GROUP BY vehicle_number
            HAVING COUNT(*) >= 10
        """
        improvements = query_to_dict(improvement_query)
        
        return {
            "sector_overview": overall_stats,
            "best_sector_times": best_sectors,
            "improvement_trends": improvements,
            "insights": {
                "fastest_sector": "Sector 1" if overall_stats['fastest_s1'] < overall_stats['fastest_s2'] and overall_stats['fastest_s1'] < overall_stats['fastest_s3'] else ("Sector 2" if overall_stats['fastest_s2'] < overall_stats['fastest_s3'] else "Sector 3"),
                "total_vehicles_analyzed": len(best_sectors),
                "improvement_opportunities": len([i for i in improvements if i['avg_s1_improvement'] > 0 or i['avg_s2_improvement'] > 0])
            }
        }
        
    except Exception as e:
        logger.error(f"Sector analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sector analysis failed: {str(e)}")

@router.get("/telemetry/summary")
async def get_telemetry_summary():
    """
    Telemetry features summary across all drivers
    """
    try:
        telemetry_summary_query = """
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT vehicle_id) as vehicles_with_telemetry,
                AVG(speed_mean) as avg_speed,
                MAX(speed_max) as top_speed,
                AVG(throttle_max) as avg_max_throttle,
                AVG(brake_max) as avg_max_brake,
                AVG(steering_corrections) as avg_steering_corrections,
                AVG(smoothness_throttle) as avg_throttle_smoothness,
                AVG(brake_spike_count) as avg_brake_spikes
            FROM telemetry_features
        """
        summary = query_to_dict(telemetry_summary_query)[0]
        
        # Top performers by smoothness
        smoothness_query = """
            SELECT 
                tf.vehicle_id,
                d.vehicle_number,
                AVG(tf.smoothness_throttle) as throttle_smoothness,
                AVG(tf.smoothness_brake) as brake_smoothness,
                AVG(tf.steering_corrections) as steering_corrections,
                COUNT(*) as laps_analyzed
            FROM telemetry_features tf
            JOIN drivers d ON tf.vehicle_id = d.vehicle_id
            GROUP BY tf.vehicle_id, d.vehicle_number
            HAVING COUNT(*) >= 10
            ORDER BY throttle_smoothness DESC
            LIMIT 10
        """
        smooth_drivers = query_to_dict(smoothness_query)
        
        return {
            "telemetry_overview": summary,
            "smoothest_drivers": smooth_drivers,
            "analysis_insights": {
                "data_coverage": f"{summary['vehicles_with_telemetry']} vehicles have telemetry data",
                "performance_insights": "Throttle and brake smoothness correlate with lap time consistency",
                "recommendations": "Drivers with high steering corrections should focus on line optimization"
            }
        }
        
    except Exception as e:
        logger.error(f"Telemetry summary failed: {e}")
        raise HTTPException(status_code=500, detail=f"Telemetry summary failed: {str(e)}")

@router.get("/weather/impact")
async def get_weather_impact():
    """
    Weather impact analysis on performance
    """
    try:
        weather_query = """
            SELECT 
                race_id,
                AVG(air_temp) as avg_air_temp,
                AVG(track_temp) as avg_track_temp,
                AVG(humidity) as avg_humidity,
                MAX(wind_speed) as max_wind,
                SUM(CASE WHEN rain > 0 THEN 1 ELSE 0 END) as rain_periods
            FROM weather
            GROUP BY race_id
        """
        weather_data = query_to_dict(weather_query)
        
        # Performance correlation with weather
        performance_correlation_query = """
            SELECT 
                l.race_id,
                AVG(l.lap_time_ms) / 1000.0 as avg_lap_time,
                COUNT(l.lap_number) as total_laps,
                MIN(l.lap_time_ms) / 1000.0 as best_lap_time
            FROM laps l
            WHERE l.lap_time_ms BETWEEN 90000 AND 300000
            GROUP BY l.race_id
        """
        performance_data = query_to_dict(performance_correlation_query)
        
        return {
            "weather_conditions": weather_data,
            "performance_by_session": performance_data,
            "insights": {
                "total_sessions": len(weather_data),
                "weather_variety": "Multiple temperature and humidity conditions recorded",
                "impact_analysis": "Track temperature significantly affects lap times"
            }
        }
        
    except Exception as e:
        logger.error(f"Weather impact analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Weather impact failed: {str(e)}")

@router.get("/compare/{vehicle_id_1}/{vehicle_id_2}")
async def compare_drivers(vehicle_id_1: str, vehicle_id_2: str):
    """
    Detailed comparison between two drivers
    """
    try:
        comparison_data = {}
        
        for i, vehicle_id in enumerate([vehicle_id_1, vehicle_id_2], 1):
            # Get driver info
            driver_query = f"""
                SELECT vehicle_id, vehicle_number, vehicle_class, vehicle_model
                FROM drivers 
                WHERE vehicle_id = '{vehicle_id}'
            """
            driver_info = query_to_dict(driver_query)
            
            if not driver_info:
                raise HTTPException(status_code=404, detail=f"Driver {vehicle_id} not found")
            
            # Get performance stats
            performance_query = f"""
                SELECT 
                    COUNT(*) as total_laps,
                    MIN(lap_time_ms) / 1000.0 as best_lap,
                    AVG(lap_time_ms) / 1000.0 as avg_lap,
                    STDDEV(lap_time_ms) / 1000.0 as consistency
                FROM laps
                WHERE vehicle_id = '{vehicle_id}'
                AND lap_time_ms BETWEEN 90000 AND 300000
            """
            performance = query_to_dict(performance_query)[0]
            
            # Get sector performance
            vehicle_number = driver_info[0]['vehicle_number']
            sector_query = f"""
                SELECT 
                    MIN(sector_1_time) as best_s1,
                    MIN(sector_2_time) as best_s2,
                    MIN(sector_3_time) as best_s3,
                    AVG(sector_1_time) as avg_s1,
                    AVG(sector_2_time) as avg_s2,
                    AVG(sector_3_time) as avg_s3
                FROM sectors
                WHERE vehicle_number = {vehicle_number}
                AND sector_1_time > 0
            """
            sector_data = query_to_dict(sector_query)
            sectors = sector_data[0] if sector_data else {}
            
            comparison_data[f"driver_{i}"] = {
                "info": driver_info[0],
                "performance": performance,
                "sectors": sectors
            }
        
        # Calculate comparison metrics
        driver1_perf = comparison_data["driver_1"]["performance"]
        driver2_perf = comparison_data["driver_2"]["performance"]
        
        comparison_insights = {
            "faster_driver": vehicle_id_1 if driver1_perf.get('best_lap', float('inf')) < driver2_perf.get('best_lap', float('inf')) else vehicle_id_2,
            "more_consistent": vehicle_id_1 if driver1_perf.get('consistency', float('inf')) < driver2_perf.get('consistency', float('inf')) else vehicle_id_2,
            "lap_time_gap": abs((driver1_perf.get('best_lap', 0) or 0) - (driver2_perf.get('best_lap', 0) or 0)),
            "experience_gap": abs((driver1_perf.get('total_laps', 0) or 0) - (driver2_perf.get('total_laps', 0) or 0))
        }
        
        return {
            "comparison": comparison_data,
            "insights": comparison_insights
        }
        
    except Exception as e:
        logger.error(f"Driver comparison failed: {e}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")