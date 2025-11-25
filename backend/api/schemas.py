from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class Anomaly(BaseModel):
    timestamp: Any = Field(..., example=123456789)
    type: str = Field(..., example="driver_mistake")
    severity: float = Field(..., example=4.2)
    signal: str = Field(..., example="brake")
    description: Optional[str] = Field(None, example="Driver mistake: brake_spike")
    recommended_action: Optional[str] = Field(None, example="Focus on smoother brake application.")


class DPTADSummary(BaseModel):
    total_anomalies: int = Field(..., example=3)
    severity_avg: float = Field(..., example=2.5)
    severity_max: float = Field(..., example=6.3)
    high_severity_count: int = Field(..., example=1)
    signals_affected: List[str] = Field(..., example=["brake", "throttle"])
    recommendation: str = Field(..., example="Improve braking consistency.")


class DPTADResponse(BaseModel):
    vehicle_id: str
    anomalies: List[Anomaly]
    summary: DPTADSummary
    algorithm: str
    analysis_timestamp: str


class SIWTLResult(BaseModel):
    siwtl_lap: Optional[float] = Field(None, example=142.35)
    potential_gain_sec: Optional[float] = Field(0.0, example=3.2)
    achievability_score: Optional[float] = Field(0.75, example=0.78)
    # sector_weights may be nested structure with component scores; accept Any for flexibility
    sector_weights: Optional[Dict[str, Any]] = Field(None, example={"s1": 0.9, "s2": 0.8, "s3": 0.95})


class SIWTLResponse(BaseModel):
    vehicle_id: str
    algorithm: str
    result: SIWTLResult
    analysis_settings: Dict[str, Any]


class ComprehensiveAnalysis(BaseModel):
    dptad_anomalies: Optional[Dict[str, Any]]
    siwtl_targets: Optional[Dict[str, Any]]
    combined_insights: Optional[Dict[str, Any]]


class ComprehensiveResponse(BaseModel):
    vehicle_id: str
    laps: List[Dict[str, Any]]
    comprehensive_analysis: ComprehensiveAnalysis
    algorithms_used: List[str]
    data_summary: Dict[str, Any]


# Request models / query param models
class DPTADParams(BaseModel):
    session_filter: Optional[str] = Field(None, description="Filter by session (practice, qualifying, race)")


class SIWTLParams(BaseModel):
    include_sectors: bool = Field(True, description="Include sector-based analysis")
    include_telemetry: bool = Field(False, description="Include telemetry smoothness analysis")
