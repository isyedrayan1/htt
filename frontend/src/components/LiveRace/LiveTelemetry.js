import React from 'react';
import { Fuel, Thermometer, Activity, TrendingUp, TrendingDown, Minus } from 'lucide-react';

const LiveTelemetry = ({ driverData, driverId }) => {
  const { telemetry, predictions, insights } = driverData;

  const getTelemetryBarColor = (value, max = 1) => {
    const percentage = (value / max) * 100;
    if (percentage > 80) return 'bg-racing-red';
    if (percentage > 60) return 'bg-racing-yellow';
    return 'bg-racing-green';
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'IMPROVING': return <TrendingUp className="w-4 h-4 text-racing-green" />;
      case 'DECLINING': return <TrendingDown className="w-4 h-4 text-racing-red" />;
      default: return <Minus className="w-4 h-4 text-racing-silver" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Driver Header */}
      <div className="card-racing">
        <h3 className="text-xl font-bold text-racing mb-4 flex items-center space-x-2">
          <Activity className="w-5 h-5 text-racing-red" />
          <span>{driverId} - Live Telemetry</span>
        </h3>
        
        {/* Core Metrics */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-racing-red mb-1">
              {telemetry.speed?.toFixed(0)} km/h
            </div>
            <p className="text-racing-silver text-sm">Speed</p>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-racing-red mb-1">
              {telemetry.predicted_lap_time?.toFixed(2)}s
            </div>
            <p className="text-racing-silver text-sm">Predicted Lap</p>
          </div>
        </div>
      </div>

      {/* Telemetry Bars */}
      <div className="card-racing">
        <h4 className="text-lg font-bold text-racing mb-4">Telemetry Data</h4>
        
        <div className="space-y-4">
          {/* Throttle */}
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-racing-silver">Throttle</span>
              <span className="text-white">{(telemetry.throttle * 100).toFixed(0)}%</span>
            </div>
            <div className="telemetry-gauge">
              <div 
                className={`telemetry-fill ${getTelemetryBarColor(telemetry.throttle)}`}
                style={{ width: `${telemetry.throttle * 100}%` }}
              ></div>
            </div>
          </div>

          {/* Brake */}
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-racing-silver">Brake Pressure</span>
              <span className="text-white">{(telemetry.brake_pressure * 100).toFixed(0)}%</span>
            </div>
            <div className="telemetry-gauge">
              <div 
                className={`telemetry-fill ${getTelemetryBarColor(telemetry.brake_pressure)}`}
                style={{ width: `${telemetry.brake_pressure * 100}%` }}
              ></div>
            </div>
          </div>

          {/* Fuel */}
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-racing-silver">Fuel Remaining</span>
              <span className="text-white">{telemetry.fuel_remaining?.toFixed(1)}L</span>
            </div>
            <div className="telemetry-gauge">
              <div 
                className={`telemetry-fill ${getTelemetryBarColor(telemetry.fuel_remaining, 100)}`}
                style={{ width: `${Math.max(0, telemetry.fuel_remaining)}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Tire Temperatures */}
      <div className="card-racing">
        <h4 className="text-lg font-bold text-racing mb-4 flex items-center space-x-2">
          <Thermometer className="w-4 h-4 text-racing-red" />
          <span>Tire Temperatures</span>
        </h4>
        
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className={`text-xl font-bold mb-1 ${
              telemetry.tire_temp_front > 110 ? 'text-racing-red' :
              telemetry.tire_temp_front > 90 ? 'text-racing-yellow' :
              'text-racing-green'
            }`}>
              {telemetry.tire_temp_front?.toFixed(0)}°C
            </div>
            <p className="text-racing-silver text-sm">Front</p>
          </div>
          <div className="text-center">
            <div className={`text-xl font-bold mb-1 ${
              telemetry.tire_temp_rear > 110 ? 'text-racing-red' :
              telemetry.tire_temp_rear > 90 ? 'text-racing-yellow' :
              'text-racing-green'
            }`}>
              {telemetry.tire_temp_rear?.toFixed(0)}°C
            </div>
            <p className="text-racing-silver text-sm">Rear</p>
          </div>
        </div>
      </div>

      {/* Sector Performance */}
      <div className="card-racing">
        <h4 className="text-lg font-bold text-racing mb-4">Sector Performance</h4>
        
        <div className="space-y-3">
          {[1, 2, 3].map((sector) => {
            const sectorTime = telemetry[`sector_${sector}`];
            const sectorPerf = insights?.sector_performance?.find(s => s.sector === sector);
            const vsBest = sectorPerf?.vs_best || 0;
            
            return (
              <div key={sector} className="flex items-center justify-between p-3 bg-racing-black/30 rounded-lg">
                <span className="text-racing-silver">Sector {sector}</span>
                <div className="flex items-center space-x-4">
                  <span className="text-white font-mono">{sectorTime?.toFixed(2)}s</span>
                  <div className={`flex items-center space-x-1 text-sm ${
                    vsBest < 0 ? 'text-racing-green' :
                    vsBest > 0 ? 'text-racing-red' :
                    'text-racing-silver'
                  }`}>
                    {getTrendIcon(vsBest < 0 ? 'IMPROVING' : vsBest > 0 ? 'DECLINING' : 'STABLE')}
                    <span>{vsBest > 0 ? '+' : ''}{vsBest?.toFixed(2)}s</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Pit Strategy */}
      <div className="card-racing">
        <h4 className="text-lg font-bold text-racing mb-4 flex items-center space-x-2">
          <Fuel className="w-4 h-4 text-racing-red" />
          <span>Pit Strategy</span>
        </h4>
        
        <div className={`p-4 rounded-lg border-l-4 ${
          predictions.pit_window.urgency === 'HIGH' ? 'border-racing-red bg-red-900/20' :
          predictions.pit_window.urgency === 'MEDIUM' ? 'border-racing-yellow bg-yellow-900/20' :
          'border-racing-green bg-green-900/20'
        }`}>
          <div className="flex items-center justify-between mb-3">
            <span className="text-racing-silver">Urgency Level</span>
            <span className={`font-bold ${
              predictions.pit_window.urgency === 'HIGH' ? 'text-racing-red' :
              predictions.pit_window.urgency === 'MEDIUM' ? 'text-racing-yellow' :
              'text-racing-green'
            }`}>
              {predictions.pit_window.urgency}
            </span>
          </div>
          
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-racing-silver">Recommended Pit Lap:</span>
              <span className="text-white font-medium">
                {predictions.pit_window.recommended_pit_lap}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-racing-silver">Time to Pit:</span>
              <span className="text-white font-medium">
                {predictions.pit_window.time_to_pit?.toFixed(0)}s
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-racing-silver">Tire Strategy:</span>
              <span className="text-white font-medium">
                {predictions.tire_strategy}
              </span>
            </div>
          </div>
        </div>
        
        <div className="mt-4 p-3 bg-racing-black/30 rounded-lg">
          <p className="text-sm text-racing-silver mb-1">Strategy Recommendation:</p>
          <p className="text-white">{insights.strategy_recommendation}</p>
        </div>
      </div>

      {/* Lap Trend */}
      <div className="card-racing">
        <h4 className="text-lg font-bold text-racing mb-4">Performance Trend</h4>
        
        <div className="flex items-center justify-center space-x-4 p-4 bg-racing-black/30 rounded-lg">
          {getTrendIcon(predictions.lap_time_trend)}
          <span className={`font-medium ${
            predictions.lap_time_trend === 'IMPROVING' ? 'text-racing-green' :
            predictions.lap_time_trend === 'DECLINING' ? 'text-racing-red' :
            'text-racing-silver'
          }`}>
            {predictions.lap_time_trend}
          </span>
        </div>
      </div>
    </div>
  );
};

export default LiveTelemetry;