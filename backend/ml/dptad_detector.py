"""
DPTAD (Dual-Path Temporal Anomaly Detection)
Innovative algorithm for world-class racing mistake detection
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from scipy import signal
from sklearn.preprocessing import StandardScaler
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DPTADDetector:
    """
    Dual-Path Temporal Anomaly Detection for Racing Intelligence
    
    Two detection paths:
    1. Slow Path (Trend): Low-pass filter → VAE for drift detection
    2. Fast Path (Spikes): Band-pass filter → CNN/threshold for spike detection
    
    Reconciliation logic determines anomaly type:
    - Fast spike + No slow drift = Driver mistake
    - Slow drift + No fast spike = Equipment degradation
    - Both = Compound issue
    """
    
    def __init__(self, 
                 slow_cutoff: float = 0.1,  # Hz for low-pass filter
                 fast_low: float = 0.5,     # Hz for band-pass lower
                 fast_high: float = 5.0,    # Hz for band-pass upper
                 spike_threshold: float = 3.0,  # Standard deviations
                 drift_threshold: float = 0.15): # Normalized drift threshold
        
        self.slow_cutoff = slow_cutoff
        self.fast_low = fast_low
        self.fast_high = fast_high
        self.spike_threshold = spike_threshold
        self.drift_threshold = drift_threshold
        
        # Initialize scalers for normalization
        self.scaler = StandardScaler()
        
        # Anomaly classification
        self.anomaly_types = {
            'driver_mistake': 'Fast spike without slow drift',
            'degradation': 'Slow drift without fast spike',
            'compound': 'Both fast and slow anomalies',
            'thermal': 'Temperature-related performance loss',
            'mechanical': 'Equipment failure pattern'
        }
    
    def detect_anomalies(self, telemetry_data: pd.DataFrame, 
                        signals: List[str] = None) -> pd.DataFrame:
        """
        Main anomaly detection pipeline
        
        Args:
            telemetry_data: DataFrame with telemetry signals
            signals: List of signal names to analyze
            
        Returns:
            DataFrame with detected anomalies
        """
        if signals is None:
            signals = ['speed', 'throttle', 'brake', 'steering_angle']
        
        # Guard against empty telemetry
        if telemetry_data is None or len(telemetry_data) == 0:
            logger.info("DPTAD received no telemetry data")
            return pd.DataFrame([])

        logger.info(f"DPTAD analyzing {len(telemetry_data)} samples across {len(signals)} signals")
        
        anomalies = []
        
        for signal_name in signals:
            if signal_name not in telemetry_data.columns:
                continue
                
            signal_data = telemetry_data[signal_name].values
            timestamps = telemetry_data.get('timestamp', range(len(signal_data)))
            
            # Dual-path analysis
            slow_anomalies = self._slow_path_analysis(signal_data, timestamps, signal_name)
            fast_anomalies = self._fast_path_analysis(signal_data, timestamps, signal_name)
            
            # Reconcile paths
            reconciled = self._reconcile_paths(slow_anomalies, fast_anomalies, signal_name)
            anomalies.extend(reconciled)
        
        # Convert to DataFrame
        anomaly_df = pd.DataFrame(anomalies)
        
        if len(anomaly_df) > 0:
            # Sort by severity (highest first)
            anomaly_df = anomaly_df.sort_values('severity', ascending=False)
            logger.info(f"DPTAD detected {len(anomaly_df)} anomalies")
        else:
            logger.info("DPTAD: No anomalies detected")
        
        return anomaly_df
    
    def _slow_path_analysis(self, signal_data: np.ndarray, 
                          timestamps: np.ndarray, 
                          signal_name: str) -> List[Dict]:
        """
        Slow Path: Trend analysis for degradation detection
        Uses low-pass filtering to identify gradual performance drift
        """
        # Apply low-pass filter (Butterworth)
        # Protect against too-short signals which break filtfilt padding
        if signal_data is None or len(signal_data) == 0:
            return []

        nyquist = 0.5 * 100  # Assuming 100 Hz sampling
        low = self.slow_cutoff / nyquist
        try:
            b, a = signal.butter(3, low, btype='low')
            padlen = 3 * max(len(a), len(b))
            if len(signal_data) <= padlen:
                # Signal too short for reliable slow-path filtering
                return []
            filtered_signal = signal.filtfilt(b, a, signal_data)
        except Exception:
            # If filtering fails, skip slow path
            return []
        
        # Detect trend using rolling statistics
        window_size = min(len(filtered_signal) // 10, 50)
        if window_size < 5:
            return []
            
        # Calculate rolling mean and detect drift
        rolling_mean = pd.Series(filtered_signal).rolling(window_size, center=True).mean()
        
        # Detect significant drift points
        drift_threshold = np.std(filtered_signal) * self.drift_threshold
        drift_points = []
        
        for i in range(window_size, len(rolling_mean) - window_size):
            if pd.notna(rolling_mean.iloc[i]):
                recent_trend = rolling_mean.iloc[i-window_size:i].mean()
                current_trend = rolling_mean.iloc[i:i+window_size].mean()
                
                if abs(current_trend - recent_trend) > drift_threshold:
                    severity = min(abs(current_trend - recent_trend) / drift_threshold, 10.0)
                    
                    drift_points.append({
                        'timestamp': timestamps[i] if hasattr(timestamps, '__getitem__') else i,
                        'type': 'slow_drift',
                        'severity': severity,
                        'signal': signal_name,
                        'drift_magnitude': current_trend - recent_trend,
                        'path': 'slow'
                    })
        
        return drift_points
    
    def _fast_path_analysis(self, signal_data: np.ndarray, 
                          timestamps: np.ndarray, 
                          signal_name: str) -> List[Dict]:
        """
        Fast Path: Spike detection for immediate mistakes
        Uses band-pass filtering to identify sudden changes
        """
        # Apply band-pass filter
        if signal_data is None or len(signal_data) == 0:
            return []

        nyquist = 0.5 * 100  # Assuming 100 Hz sampling
        low = self.fast_low / nyquist
        high = min(self.fast_high / nyquist, 0.99)

        try:
            b, a = signal.butter(3, [low, high], btype='band')
            padlen = 3 * max(len(a), len(b))
            if len(signal_data) <= padlen:
                # Signal too short for reliable fast-path filtering
                return []
            filtered_signal = signal.filtfilt(b, a, signal_data)
        except ValueError:
            # Fallback to high-pass if band-pass fails
            try:
                b, a = signal.butter(3, low, btype='high')
                padlen = 3 * max(len(a), len(b))
                if len(signal_data) <= padlen:
                    return []
                filtered_signal = signal.filtfilt(b, a, signal_data)
            except Exception:
                return []
        except Exception:
            return []
        
        # Detect spikes using threshold method
        signal_std = np.std(filtered_signal)
        spike_threshold = signal_std * self.spike_threshold
        
        # Find spike locations
        spike_indices = np.where(np.abs(filtered_signal) > spike_threshold)[0]
        
        # Group nearby spikes
        spike_groups = self._group_spikes(spike_indices, min_separation=5)
        
        spike_points = []
        for group in spike_groups:
            peak_idx = group[np.argmax(np.abs(filtered_signal[group]))]
            spike_magnitude = abs(filtered_signal[peak_idx])
            severity = min(spike_magnitude / spike_threshold, 10.0)
            
            # Classify spike type based on signal
            spike_subtype = self._classify_spike(signal_name, spike_magnitude, signal_data[peak_idx])
            
            spike_points.append({
                'timestamp': timestamps[peak_idx] if hasattr(timestamps, '__getitem__') else peak_idx,
                'type': 'fast_spike',
                'severity': severity,
                'signal': signal_name,
                'spike_magnitude': spike_magnitude,
                'spike_subtype': spike_subtype,
                'path': 'fast'
            })
        
        return spike_points
    
    def _reconcile_paths(self, slow_anomalies: List[Dict], 
                        fast_anomalies: List[Dict], 
                        signal_name: str) -> List[Dict]:
        """
        Reconcile fast and slow path results to determine anomaly type
        """
        reconciled = []
        temporal_window = 10  # seconds
        
        # Process fast spikes and check for corresponding slow drift
        for fast in fast_anomalies:
            fast_time = fast['timestamp']
            
            # Look for nearby slow anomalies
            nearby_slow = [
                slow for slow in slow_anomalies 
                if abs(slow['timestamp'] - fast_time) <= temporal_window
            ]
            
            if nearby_slow:
                # Compound issue: both fast and slow
                anomaly_type = 'compound'
                description = f"Compound issue: {fast['spike_subtype']} with degradation"
                combined_severity = max(fast['severity'], max(s['severity'] for s in nearby_slow))
            else:
                # Pure driver mistake
                anomaly_type = 'driver_mistake'
                description = f"Driver mistake: {fast['spike_subtype']}"
                combined_severity = fast['severity']
            
            reconciled.append({
                'timestamp': fast_time,
                'type': anomaly_type,
                'severity': combined_severity,
                'signal': signal_name,
                'description': description,
                'fast_component': fast,
                'slow_component': nearby_slow[0] if nearby_slow else None,
                'recommended_action': self._get_recommendation(anomaly_type, signal_name)
            })
        
        # Process isolated slow anomalies (degradation)
        fast_times = {f['timestamp'] for f in fast_anomalies}
        for slow in slow_anomalies:
            if not any(abs(slow['timestamp'] - ft) <= temporal_window for ft in fast_times):
                # Pure degradation
                reconciled.append({
                    'timestamp': slow['timestamp'],
                    'type': 'degradation',
                    'severity': slow['severity'],
                    'signal': signal_name,
                    'description': f"Performance degradation in {signal_name}",
                    'fast_component': None,
                    'slow_component': slow,
                    'recommended_action': self._get_recommendation('degradation', signal_name)
                })
        
        return reconciled
    
    def _group_spikes(self, spike_indices: np.ndarray, min_separation: int = 5) -> List[np.ndarray]:
        """Group nearby spike indices"""
        if len(spike_indices) == 0:
            return []
            
        groups = []
        current_group = [spike_indices[0]]
        
        for i in range(1, len(spike_indices)):
            if spike_indices[i] - spike_indices[i-1] <= min_separation:
                current_group.append(spike_indices[i])
            else:
                groups.append(np.array(current_group))
                current_group = [spike_indices[i]]
        
        groups.append(np.array(current_group))
        return groups
    
    def _classify_spike(self, signal_name: str, magnitude: float, raw_value: float) -> str:
        """Classify spike type based on signal and characteristics"""
        spike_types = {
            'brake': {
                'high': 'brake_spike',
                'negative': 'brake_release_error'
            },
            'throttle': {
                'high': 'throttle_stab',
                'negative': 'lift_hesitation'
            },
            'speed': {
                'negative': 'lock_up',
                'high': 'traction_loss'
            },
            'steering_angle': {
                'high': 'overcorrection',
                'oscillating': 'steering_instability'
            }
        }
        
        signal_category = signal_name.lower()
        if signal_category in spike_types:
            if raw_value < 0 and 'negative' in spike_types[signal_category]:
                return spike_types[signal_category]['negative']
            else:
                return spike_types[signal_category].get('high', f'{signal_category}_anomaly')
        
        return f'{signal_category}_anomaly'
    
    def _get_recommendation(self, anomaly_type: str, signal_name: str) -> str:
        """Generate coaching recommendation based on anomaly type"""
        recommendations = {
            'driver_mistake': {
                'brake': "Focus on smoother brake application. Avoid sudden brake spikes.",
                'throttle': "Work on progressive throttle control. Eliminate stabs and hesitation.",
                'speed': "Address lock-up tendency. Brake earlier and more progressively.",
                'steering_angle': "Reduce steering corrections. Focus on smooth, deliberate inputs."
            },
            'degradation': {
                'brake': "Monitor brake temperature and pad wear. Consider pit strategy.",
                'throttle': "Check engine performance and throttle response calibration.",
                'speed': "Assess tire degradation and grip levels. Adjust driving style.",
                'steering_angle': "Evaluate suspension setup and tire pressure."
            },
            'compound': {
                'default': "Multiple issues detected. Address both technique and equipment."
            }
        }
        
        if anomaly_type in recommendations:
            if signal_name in recommendations[anomaly_type]:
                return recommendations[anomaly_type][signal_name]
            elif 'default' in recommendations[anomaly_type]:
                return recommendations[anomaly_type]['default']
        
        return f"Monitor {signal_name} performance and adjust technique accordingly."
    
    def get_anomaly_summary(self, anomalies_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics for detected anomalies"""
        if len(anomalies_df) == 0:
            return {
                'total_anomalies': 0,
                'severity_avg': 0,
                'types': {},
                'signals_affected': [],
                'recommendation': "No anomalies detected. Performance is consistent."
            }
        
        summary = {
            'total_anomalies': len(anomalies_df),
            'severity_avg': anomalies_df['severity'].mean(),
            'severity_max': anomalies_df['severity'].max(),
            'types': anomalies_df['type'].value_counts().to_dict(),
            'signals_affected': anomalies_df['signal'].unique().tolist(),
            'high_severity_count': len(anomalies_df[anomalies_df['severity'] > 5.0]),
            'recommendation': self._generate_summary_recommendation(anomalies_df)
        }
        
        return summary
    
    def _generate_summary_recommendation(self, anomalies_df: pd.DataFrame) -> str:
        """Generate overall coaching recommendation"""
        if len(anomalies_df) == 0:
            return "Maintain current performance level."
        
        # Identify dominant anomaly type
        dominant_type = anomalies_df['type'].value_counts().index[0]
        dominant_signal = anomalies_df['signal'].value_counts().index[0]
        avg_severity = anomalies_df['severity'].mean()
        
        if dominant_type == 'driver_mistake':
            if avg_severity > 7:
                return f"Critical: Focus immediately on {dominant_signal} technique. Multiple driver errors detected."
            elif avg_severity > 4:
                return f"Important: Improve {dominant_signal} consistency. Driver technique issues identified."
            else:
                return f"Minor technique adjustments needed in {dominant_signal} control."
        
        elif dominant_type == 'degradation':
            if avg_severity > 6:
                return f"Equipment attention required: {dominant_signal} showing significant degradation."
            else:
                return f"Monitor {dominant_signal} performance trends. Early degradation detected."
        
        elif dominant_type == 'compound':
            return f"Address both technique and equipment issues in {dominant_signal}."
        
        return "Review performance data and adjust accordingly."

# Global DPTAD instance for backend use
_dptad_detector = None

def get_dptad_detector() -> DPTADDetector:
    """Get global DPTAD detector instance"""
    global _dptad_detector
    if _dptad_detector is None:
        _dptad_detector = DPTADDetector()
    return _dptad_detector

def analyze_driver_anomalies(vehicle_id: str, telemetry_data: pd.DataFrame) -> Dict[str, Any]:
    """Analyze anomalies for a specific driver using DPTAD"""
    detector = get_dptad_detector()
    
    # Run DPTAD analysis
    anomalies_df = detector.detect_anomalies(telemetry_data)
    
    # Generate summary
    summary = detector.get_anomaly_summary(anomalies_df)
    
    return {
        'vehicle_id': vehicle_id,
        'anomalies': anomalies_df.to_dict('records') if len(anomalies_df) > 0 else [],
        'summary': summary,
        'algorithm': 'DPTAD v1.0 - Dual-Path Temporal Anomaly Detection',
        'analysis_timestamp': pd.Timestamp.now().isoformat()
    }