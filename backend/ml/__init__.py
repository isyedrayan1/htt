"""
Machine Learning Module for ANTIGRAVITY Platform
Innovative algorithms for racing intelligence
"""

from .dptad_detector import (
    DPTADDetector, 
    get_dptad_detector, 
    analyze_driver_anomalies
)
from .siwtl_calculator import (
    SIWTLCalculator, 
    get_siwtl_calculator, 
    calculate_driver_siwtl
)

__all__ = [
    'DPTADDetector',
    'get_dptad_detector', 
    'analyze_driver_anomalies',
    'SIWTLCalculator',
    'get_siwtl_calculator',
    'calculate_driver_siwtl'
]

__version__ = '2.0.0'
__algorithms__ = {
    'DPTAD': 'Dual-Path Temporal Anomaly Detection v1.0',
    'SIWTL': 'Smart Weighted Ideal Lap v2.0'
}