import React from 'react';
import { BarChart3, Clock, TrendingUp } from 'lucide-react';

const PerformanceChart = ({ driverData, driverId }) => {
  if (!driverData || !driverData.laps) {
    return (
      <div className="card-racing">
        <h3 className="text-xl font-bold text-racing mb-4">Performance Chart</h3>
        <div className="text-center py-8 text-racing-silver">
          <BarChart3 className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No lap data available</p>
        </div>
      </div>
    );
  }

  const laps = driverData.laps.slice(0, 10); // Show last 10 laps
  const bestLap = Math.min(...laps.map(lap => lap.lap_time));
  const averageLap = laps.reduce((sum, lap) => sum + lap.lap_time, 0) / laps.length;

  return (
    <div className="space-y-6">
      {/* Performance Summary */}
      <div className="card-racing">
        <h3 className="text-xl font-bold text-racing mb-6">Performance Summary</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-racing-red mb-2">
              {bestLap.toFixed(2)}s
            </div>
            <p className="text-racing-silver">Best Lap</p>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-racing-red mb-2">
              {averageLap.toFixed(2)}s
            </div>
            <p className="text-racing-silver">Average Lap</p>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-racing-red mb-2">
              {laps.length}
            </div>
            <p className="text-racing-silver">Total Laps</p>
          </div>
        </div>
      </div>

      {/* Lap Times Chart */}
      <div className="card-racing">
        <h3 className="text-xl font-bold text-racing mb-6 flex items-center space-x-2">
          <Clock className="w-5 h-5 text-racing-red" />
          <span>Recent Lap Times</span>
        </h3>
        
        <div className="space-y-3">
          {laps.map((lap, index) => {
            const isPersonalBest = lap.lap_time === bestLap;
            const percentageFromBest = ((lap.lap_time - bestLap) / bestLap) * 100;
            
            return (
              <div key={index} className="flex items-center space-x-4">
                <div className="w-12 text-racing-silver text-sm">
                  Lap {lap.lap_number}
                </div>
                <div className="flex-1 bg-racing-black/50 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className={`font-bold ${
                      isPersonalBest ? 'text-racing-green' : 'text-white'
                    }`}>
                      {lap.lap_time.toFixed(2)}s
                      {isPersonalBest && ' 🏆'}
                    </span>
                    <span className={`text-sm ${
                      percentageFromBest === 0 ? 'text-racing-green' :
                      percentageFromBest < 2 ? 'text-racing-yellow' :
                      'text-racing-red'
                    }`}>
                      +{percentageFromBest.toFixed(1)}%
                    </span>
                  </div>
                  {/* Visual bar */}
                  <div className="w-full bg-racing-black rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        percentageFromBest === 0 ? 'bg-racing-green' :
                        percentageFromBest < 2 ? 'bg-racing-yellow' :
                        'bg-racing-red'
                      }`}
                      style={{ width: `${Math.min(100, 80 + percentageFromBest * 2)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Performance Trends */}
      <div className="card-racing">
        <h3 className="text-xl font-bold text-racing mb-6 flex items-center space-x-2">
          <TrendingUp className="w-5 h-5 text-racing-red" />
          <span>Performance Trends</span>
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-racing-black/30 rounded-lg p-4">
            <div className="text-lg font-bold text-racing-green mb-2">
              Consistency
            </div>
            <div className="text-sm text-racing-silver">
              Lap time variance: ±{((Math.max(...laps.map(l => l.lap_time)) - bestLap) / 2).toFixed(2)}s
            </div>
          </div>
          <div className="bg-racing-black/30 rounded-lg p-4">
            <div className="text-lg font-bold text-racing-yellow mb-2">
              Improvement
            </div>
            <div className="text-sm text-racing-silver">
              {laps.length >= 5 ? (
                laps.slice(-3).every((lap, i, arr) => i === 0 || lap.lap_time <= arr[i-1].lap_time) ?
                'Improving trend' : 'Mixed performance'
              ) : 'Need more data'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceChart;