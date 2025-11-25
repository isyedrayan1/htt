"""
SIWTL (Smart Weighted Ideal Lap) Algorithm
Innovative realistic lap time target calculation
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class SIWTLCalculator:
    """
    Smart Weighted Ideal Lap Calculator
    
    Computes the most realistic possible lap a driver can achieve by:
    1. Identifying each sector's top performance
    2. Computing achievability weights based on:
       - Consistency in that sector
       - Telemetry smoothness
       - Similar stint conditions
       - Temperature closeness
       - Traffic flags
    3. Weighted sum: SIWTL = S1_w + S2_w + S3_w
    
    Unlike theoretical best laps, SIWTL produces achievable targets.
    """
    
    def __init__(self, 
                 consistency_weight: float = 0.3,
                 smoothness_weight: float = 0.25,
                 conditions_weight: float = 0.2,
                 temperature_weight: float = 0.15,
                 traffic_weight: float = 0.1):
        
        # Weighting factors for achievability calculation
        self.consistency_weight = consistency_weight
        self.smoothness_weight = smoothness_weight
        self.conditions_weight = conditions_weight
        self.temperature_weight = temperature_weight
        self.traffic_weight = traffic_weight
        
        # Validation
        total_weight = sum([consistency_weight, smoothness_weight, conditions_weight, 
                           temperature_weight, traffic_weight])
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"SIWTL weights sum to {total_weight:.3f}, not 1.0")
    
    def calculate_siwtl(self, 
                       driver_data: pd.DataFrame, 
                       sector_data: pd.DataFrame = None,
                       telemetry_data: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Calculate SIWTL for a driver
        
        Args:
            driver_data: Lap times and sector data for driver
            sector_data: Detailed sector timing data
            telemetry_data: Optional telemetry for smoothness analysis
            
        Returns:
            SIWTL calculation results
        """
        logger.info(f"Calculating SIWTL for {len(driver_data)} laps")
        
        # Validate input data
        required_columns = ['lap_number', 'lap_time_ms']
        if not all(col in driver_data.columns for col in required_columns):
            raise ValueError(f"Driver data must contain: {required_columns}")
        
        # Filter valid laps (realistic racing times)
        valid_laps = driver_data[
            (driver_data['lap_time_ms'] >= 120000) & 
            (driver_data['lap_time_ms'] <= 200000)
        ].copy()
        
        if len(valid_laps) < 5:
            logger.warning("Insufficient valid laps for SIWTL calculation")
            return self._create_insufficient_data_result()
        
        # Calculate theoretical best lap
        theoretical_best = self._calculate_theoretical_best(valid_laps, sector_data)
        
        # Calculate sector achievability weights
        sector_weights = self._calculate_sector_weights(
            valid_laps, sector_data, telemetry_data
        )
        
        # Compute SIWTL
        siwtl_result = self._compute_siwtl(
            theoretical_best, sector_weights, valid_laps
        )
        
        # Add metadata
        siwtl_result.update({
            'algorithm': 'SIWTL v2.0 - Smart Weighted Ideal Lap',
            'total_laps_analyzed': len(valid_laps),
            'calculation_timestamp': pd.Timestamp.now().isoformat(),
            'achievability_factors': {
                'consistency_weight': self.consistency_weight,
                'smoothness_weight': self.smoothness_weight,
                'conditions_weight': self.conditions_weight,
                'temperature_weight': self.temperature_weight,
                'traffic_weight': self.traffic_weight
            }
        })
        
        return siwtl_result
    
    def _calculate_theoretical_best(self, 
                                   valid_laps: pd.DataFrame, 
                                   sector_data: pd.DataFrame = None) -> Dict[str, float]:
        """
        Calculate theoretical best lap from sector bests
        """
        if sector_data is not None and len(sector_data) > 0:
            # Use sector data if available
            sector_cols = ['sector_1_time', 'sector_2_time', 'sector_3_time']
            available_sectors = [col for col in sector_cols if col in sector_data.columns]
            
            if len(available_sectors) >= 2:
                sector_bests = {}
                for i, col in enumerate(available_sectors, 1):
                    valid_times = sector_data[col][
                        (sector_data[col] > 20) & (sector_data[col] < 80)
                    ]
                    if len(valid_times) > 0:
                        sector_bests[f's{i}'] = valid_times.min()
                
                if len(sector_bests) >= 2:
                    theoretical_best_ms = sum(sector_bests.values()) * 1000
                    return {
                        'theoretical_best_lap': theoretical_best_ms / 1000.0,
                        'sector_bests': sector_bests,
                        'method': 'sector_based'
                    }
        
        # Fallback: use best lap time
        best_lap_ms = valid_laps['lap_time_ms'].min()
        return {
            'theoretical_best_lap': best_lap_ms / 1000.0,
            'sector_bests': {},
            'method': 'lap_based'
        }
    
    def _calculate_sector_weights(self, 
                                 valid_laps: pd.DataFrame,
                                 sector_data: pd.DataFrame = None,
                                 telemetry_data: pd.DataFrame = None) -> Dict[str, Dict[str, float]]:
        """
        Calculate achievability weights for each sector
        """
        sector_weights = {}
        
        if sector_data is not None and len(sector_data) > 0:
            sector_cols = ['sector_1_time', 'sector_2_time', 'sector_3_time']
            
            for i, col in enumerate(sector_cols, 1):
                if col in sector_data.columns:
                    sector_weights[f's{i}'] = self._calculate_single_sector_weight(
                        sector_data[col], 
                        i,
                        valid_laps,
                        telemetry_data
                    )
        
        # If no sector data, create uniform weights
        if not sector_weights:
            uniform_weight = 1.0 / 3.0
            for i in range(1, 4):
                sector_weights[f's{i}'] = {
                    'consistency_score': uniform_weight,
                    'smoothness_score': uniform_weight,
                    'conditions_score': uniform_weight,
                    'temperature_score': uniform_weight,
                    'traffic_score': uniform_weight,
                    'combined_weight': uniform_weight
                }
        
        return sector_weights
    
    def _calculate_single_sector_weight(self, 
                                       sector_times: pd.Series,
                                       sector_num: int,
                                       valid_laps: pd.DataFrame,
                                       telemetry_data: pd.DataFrame = None) -> Dict[str, float]:
        """
        Calculate achievability weight for a single sector
        """
        # Filter valid sector times
        valid_sector_times = sector_times[
            (sector_times > 20) & (sector_times < 80)
        ]
        
        if len(valid_sector_times) < 3:
            return self._default_sector_weight()
        
        # 1. Consistency Score
        consistency_score = self._calculate_consistency_score(valid_sector_times)
        
        # 2. Smoothness Score (from telemetry if available)
        smoothness_score = self._calculate_smoothness_score(
            telemetry_data, sector_num
        ) if telemetry_data is not None else 0.7  # Default decent score
        
        # 3. Conditions Score (stint similarity)
        conditions_score = self._calculate_conditions_score(
            valid_laps, valid_sector_times
        )
        
        # 4. Temperature Score
        temperature_score = self._calculate_temperature_score(valid_laps)
        
        # 5. Traffic Score
        traffic_score = self._calculate_traffic_score(valid_laps)
        
        # Combine weighted scores
        combined_weight = (
            consistency_score * self.consistency_weight +
            smoothness_score * self.smoothness_weight +
            conditions_score * self.conditions_weight +
            temperature_score * self.temperature_weight +
            traffic_score * self.traffic_weight
        )
        
        return {
            'consistency_score': consistency_score,
            'smoothness_score': smoothness_score,
            'conditions_score': conditions_score,
            'temperature_score': temperature_score,
            'traffic_score': traffic_score,
            'combined_weight': combined_weight
        }
    
    def _calculate_consistency_score(self, sector_times: pd.Series) -> float:
        """
        Calculate consistency score (lower variation = higher achievability)
        """
        if len(sector_times) < 2:
            return 0.5
        
        cv = sector_times.std() / sector_times.mean()  # Coefficient of variation
        
        # Lower CV = higher consistency = higher achievability
        # Transform CV to 0-1 score (0.1 CV = 0 score, 0.01 CV = 1.0 score)
        consistency_score = max(0.0, min(1.0, (0.1 - cv) / 0.09))
        
        return consistency_score
    
    def _calculate_smoothness_score(self, 
                                   telemetry_data: pd.DataFrame, 
                                   sector_num: int) -> float:
        """
        Calculate smoothness score from telemetry data
        """
        if telemetry_data is None or len(telemetry_data) == 0:
            return 0.7  # Default score
        
        # Look for smoothness indicators in telemetry
        smoothness_signals = ['throttle', 'brake', 'steering_angle']
        available_signals = [s for s in smoothness_signals if s in telemetry_data.columns]
        
        if not available_signals:
            return 0.7
        
        smoothness_scores = []
        
        for signal in available_signals:
            # Calculate signal variation (lower = smoother)
            signal_data = telemetry_data[signal]
            if len(signal_data) > 1:
                # Use rate of change as smoothness metric
                rate_of_change = np.diff(signal_data)
                smoothness = 1.0 / (1.0 + np.std(rate_of_change))
                smoothness_scores.append(smoothness)
        
        return np.mean(smoothness_scores) if smoothness_scores else 0.7
    
    def _calculate_conditions_score(self, 
                                   valid_laps: pd.DataFrame,
                                   sector_times: pd.Series) -> float:
        """
        Calculate conditions similarity score
        """
        # Look for stint or conditions indicators
        if 'stint_number' in valid_laps.columns:
            # Analyze stint consistency
            stint_sector_means = {}
            for stint in valid_laps['stint_number'].unique():
                stint_laps = valid_laps[valid_laps['stint_number'] == stint]
                if len(stint_laps) > 2:
                    stint_idx = stint_laps.index.intersection(sector_times.index)
                    if len(stint_idx) > 0:
                        stint_sector_means[stint] = sector_times.loc[stint_idx].mean()
            
            if len(stint_sector_means) > 1:
                # Lower variation between stints = better conditions score
                stint_variation = np.std(list(stint_sector_means.values()))
                conditions_score = max(0.3, min(1.0, (2.0 - stint_variation) / 2.0))
                return conditions_score
        
        # Default: assume decent conditions
        return 0.75
    
    def _calculate_temperature_score(self, valid_laps: pd.DataFrame) -> float:
        """
        Calculate temperature consistency score
        """
        # Look for temperature data
        temp_cols = ['air_temp', 'track_temp', 'temp_delta_from_start']
        available_temp = [col for col in temp_cols if col in valid_laps.columns]
        
        if not available_temp:
            return 0.8  # Assume decent temperature conditions
        
        # Analyze temperature variation during session
        temp_scores = []
        for col in available_temp:
            temp_data = valid_laps[col].dropna()
            if len(temp_data) > 1:
                temp_range = temp_data.max() - temp_data.min()
                # Lower temperature variation = higher achievability
                if col == 'air_temp':
                    # Air temp: 5°C range is acceptable
                    temp_score = max(0.2, min(1.0, (5.0 - temp_range) / 5.0))
                elif col == 'track_temp':
                    # Track temp: 10°C range is acceptable
                    temp_score = max(0.2, min(1.0, (10.0 - temp_range) / 10.0))
                else:
                    # Delta from start: 3°C is acceptable
                    temp_score = max(0.2, min(1.0, (3.0 - abs(temp_range)) / 3.0))
                
                temp_scores.append(temp_score)
        
        return np.mean(temp_scores) if temp_scores else 0.8
    
    def _calculate_traffic_score(self, valid_laps: pd.DataFrame) -> float:
        """
        Calculate traffic/flag impact score
        """
        # Look for traffic indicators
        traffic_indicators = ['traffic_indicator', 'yellow_flag_indicator', 'is_clear_lap']
        available_indicators = [col for col in traffic_indicators if col in valid_laps.columns]
        
        if not available_indicators:
            return 0.85  # Assume mostly clear conditions
        
        # Calculate percentage of clear laps
        clear_laps = 0
        total_scored_laps = 0
        
        for col in available_indicators:
            indicator_data = valid_laps[col].dropna()
            if len(indicator_data) > 0:
                if col == 'is_clear_lap':
                    clear_laps += indicator_data.sum()
                elif col in ['traffic_indicator', 'yellow_flag_indicator']:
                    # Invert: 0 = clear, 1 = traffic/yellow
                    clear_laps += len(indicator_data) - indicator_data.sum()
                total_scored_laps = max(total_scored_laps, len(indicator_data))
        
        if total_scored_laps > 0:
            clear_percentage = clear_laps / total_scored_laps
            return max(0.3, min(1.0, clear_percentage))
        
        return 0.85
    
    def _compute_siwtl(self, 
                      theoretical_best: Dict[str, Any],
                      sector_weights: Dict[str, Dict[str, float]],
                      valid_laps: pd.DataFrame) -> Dict[str, Any]:
        """
        Compute final SIWTL value
        """
        theoretical_lap = theoretical_best['theoretical_best_lap']
        
        if 'sector_bests' in theoretical_best and theoretical_best['sector_bests']:
            # Sector-based SIWTL calculation
            siwtl_sectors = {}
            total_weighted_time = 0
            
            for sector_id, best_time in theoretical_best['sector_bests'].items():
                if sector_id in sector_weights:
                    weight = sector_weights[sector_id]['combined_weight']
                    # Apply achievability: realistic time = best_time / weight
                    realistic_time = best_time / max(weight, 0.1)  # Prevent division by zero
                    siwtl_sectors[sector_id] = {
                        'best_time': best_time,
                        'achievability_weight': weight,
                        'realistic_time': realistic_time
                    }
                    total_weighted_time += realistic_time
            
            siwtl_lap = total_weighted_time
        else:
            # Lap-based SIWTL calculation
            # Use average achievability across all factors
            if sector_weights:
                avg_weight = np.mean([
                    weights['combined_weight'] 
                    for weights in sector_weights.values()
                ])
            else:
                avg_weight = 0.75  # Default achievability
            
            siwtl_lap = theoretical_lap / max(avg_weight, 0.1)
            siwtl_sectors = {}
        
        # Calculate potential gain
        current_avg_lap = valid_laps['lap_time_ms'].mean() / 1000.0
        potential_gain = current_avg_lap - siwtl_lap
        
        # Calculate achievability score (0-1)
        achievability_score = min(1.0, theoretical_lap / siwtl_lap)
        
        return {
            'siwtl_lap': siwtl_lap,
            'theoretical_best_lap': theoretical_lap,
            'current_avg_lap': current_avg_lap,
            'potential_gain_sec': potential_gain,
            'achievability_score': achievability_score,
            'sector_analysis': siwtl_sectors,
            'sector_weights': sector_weights,
            'confidence_level': self._calculate_confidence_level(
                len(valid_laps), sector_weights
            )
        }
    
    def _calculate_confidence_level(self, 
                                   num_laps: int, 
                                   sector_weights: Dict) -> str:
        """
        Calculate confidence level in SIWTL result
        """
        if num_laps >= 30 and len(sector_weights) >= 2:
            return "High"
        elif num_laps >= 15:
            return "Medium"
        else:
            return "Low"
    
    def _default_sector_weight(self) -> Dict[str, float]:
        """Return default sector weight when calculation fails"""
        return {
            'consistency_score': 0.6,
            'smoothness_score': 0.6,
            'conditions_score': 0.7,
            'temperature_score': 0.8,
            'traffic_score': 0.8,
            'combined_weight': 0.68
        }
    
    def _create_insufficient_data_result(self) -> Dict[str, Any]:
        """Create result when insufficient data available"""
        return {
            'siwtl_lap': None,
            'theoretical_best_lap': None,
            'potential_gain_sec': None,
            'achievability_score': None,
            'error': 'Insufficient valid lap data for SIWTL calculation',
            'algorithm': 'SIWTL v2.0 - Smart Weighted Ideal Lap',
            'confidence_level': 'None'
        }

# Global SIWTL instance for backend use
_siwtl_calculator = None

def get_siwtl_calculator() -> SIWTLCalculator:
    """Get global SIWTL calculator instance"""
    global _siwtl_calculator
    if _siwtl_calculator is None:
        _siwtl_calculator = SIWTLCalculator()
    return _siwtl_calculator

def calculate_driver_siwtl(vehicle_id: str, 
                          lap_data: pd.DataFrame,
                          sector_data: pd.DataFrame = None,
                          telemetry_data: pd.DataFrame = None) -> Dict[str, Any]:
    """Calculate SIWTL for a specific driver"""
    calculator = get_siwtl_calculator()
    
    # Run SIWTL calculation
    siwtl_result = calculator.calculate_siwtl(
        lap_data, sector_data, telemetry_data
    )
    
    # Add vehicle context
    siwtl_result['vehicle_id'] = vehicle_id
    
    return siwtl_result