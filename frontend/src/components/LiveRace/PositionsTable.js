import React from 'react';
import { AlertTriangle, Clock, Fuel } from 'lucide-react';

const PositionsTable = ({ positions, onDriverSelect, selectedDriver }) => {
  const getPositionBadgeClass = (position) => {
    if (position === 1) return 'position-1';
    if (position === 2) return 'position-2';
    if (position === 3) return 'position-3';
    return 'position-other';
  };

  const getPitUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'HIGH': return 'text-red-400 bg-red-400/10 border-red-400/30';
      case 'MEDIUM': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30';
      case 'LOW': return 'text-green-400 bg-green-400/10 border-green-400/30';
      default: return 'text-racing-silver bg-racing-silver/10 border-racing-silver/30';
    }
  };

  return (
    <div className="card-racing">
      <h2 className="text-2xl font-bold text-racing mb-6">Live Positions</h2>
      
      <div className="space-y-3">
        {positions?.map((driver) => (
          <div
            key={driver.vehicle_id}
            onClick={() => onDriverSelect(driver.vehicle_id)}
            className={`p-4 rounded-lg border-2 transition-all duration-200 cursor-pointer hover:border-racing-red/50 ${
              selectedDriver === driver.vehicle_id
                ? 'border-racing-red bg-racing-red/10'
                : 'border-racing-silver/20 bg-racing-black/30 hover:bg-racing-black/50'
            }`}
          >
            <div className="flex items-center justify-between">
              {/* Position and Driver */}
              <div className="flex items-center space-x-4">
                <div className={`position-badge ${getPositionBadgeClass(driver.position)}`}>
                  {driver.position}
                </div>
                <div>
                  <h4 className="font-bold text-white text-lg">{driver.vehicle_id}</h4>
                  <div className="flex items-center space-x-4 text-sm text-racing-silver">
                    <div className="flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>Lap {driver.current_lap}</span>
                    </div>
                    {driver.on_track && (
                      <span className="text-racing-green">● ON TRACK</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Performance Metrics */}
              <div className="flex items-center space-x-6">
                <div className="text-right">
                  <div className="text-white font-bold">
                    {driver.last_lap_time?.toFixed(2)}s
                  </div>
                  <div className="text-xs text-racing-silver">Last Lap</div>
                </div>
                
                <div className="text-right">
                  <div className="text-white font-bold">
                    +{driver.gap_to_leader?.toFixed(2)}s
                  </div>
                  <div className="text-xs text-racing-silver">Gap</div>
                </div>

                {/* Pit Strategy Indicator */}
                <div className={`px-3 py-1 rounded-full border text-xs font-medium ${getPitUrgencyColor(driver.pit_window?.urgency)}`}>
                  <div className="flex items-center space-x-1">
                    {driver.pit_window?.urgency === 'HIGH' && <AlertTriangle className="w-3 h-3" />}
                    {driver.pit_window?.urgency === 'MEDIUM' && <Fuel className="w-3 h-3" />}
                    <span>{driver.pit_window?.urgency || 'LOW'}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Additional Details for Selected Driver */}
            {selectedDriver === driver.vehicle_id && (
              <div className="mt-4 pt-4 border-t border-racing-silver/20">
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-racing-silver">Recommended Pit:</span>
                    <div className="text-white font-medium">
                      Lap {driver.pit_window?.recommended_pit_lap || 'N/A'}
                    </div>
                  </div>
                  <div>
                    <span className="text-racing-silver">Fuel Remaining:</span>
                    <div className="text-white font-medium">
                      {driver.pit_window?.fuel_laps_remaining?.toFixed(1) || 'N/A'} laps
                    </div>
                  </div>
                  <div>
                    <span className="text-racing-silver">Tire Degradation:</span>
                    <div className="text-white font-medium">
                      {driver.pit_window?.tire_degradation_pct?.toFixed(0) || 'N/A'}%
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {!positions?.length && (
        <div className="text-center py-8 text-racing-silver">
          <AlertTriangle className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No position data available</p>
        </div>
      )}
    </div>
  );
};

export default PositionsTable;