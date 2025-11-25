import React, { useState, useEffect } from 'react';
import { Target, Clock, TrendingUp, AlertTriangle, Users } from 'lucide-react';
import { ApiService } from '../../services/apiService';

const Strategy = () => {
  const [pitStrategies, setPitStrategies] = useState(null);
  const [raceData, setRaceData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [strategies, race] = await Promise.all([
          ApiService.getPitStrategies(),
          ApiService.getLiveSummary()
        ]);
        setPitStrategies(strategies);
        setRaceData(race);
      } catch (error) {
        console.error('Failed to fetch strategy data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getStrategyTypeColor = (type) => {
    switch (type) {
      case 'UNDERCUT': return 'text-racing-green bg-green-900/20 border-green-500/30';
      case 'OVERCUT': return 'text-racing-yellow bg-yellow-900/20 border-yellow-500/30';
      case 'AGGRESSIVE': return 'text-racing-red bg-red-900/20 border-red-500/30';
      default: return 'text-racing-silver bg-gray-900/20 border-gray-500/30';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence > 0.8) return 'text-racing-green';
    if (confidence > 0.6) return 'text-racing-yellow';
    return 'text-racing-red';
  };

  if (loading) {
    return (
      <div className="p-8 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-racing-red mx-auto mb-4"></div>
          <p className="text-racing-silver">Loading strategy analysis...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-racing text-3xl font-bold text-white mb-2">
          🎯 Race Strategy Center
        </h1>
        <p className="text-racing-silver">
          Advanced pit stop optimization and strategic intelligence
        </p>
      </div>

      {/* Race Conditions */}
      {pitStrategies?.race_conditions && (
        <div className="card-racing">
          <h2 className="text-2xl font-bold text-racing mb-6">Current Race Conditions</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="metric-card text-center">
              <div className="text-2xl font-bold text-racing-red mb-2">
                {(pitStrategies.race_conditions.safety_car_probability * 100).toFixed(0)}%
              </div>
              <p className="text-racing-silver">Safety Car Risk</p>
            </div>
            
            <div className="metric-card text-center">
              <div className="text-2xl font-bold text-racing-red mb-2">
                {(pitStrategies.race_conditions.weather_change_probability * 100).toFixed(0)}%
              </div>
              <p className="text-racing-silver">Weather Change</p>
            </div>
            
            <div className="metric-card text-center">
              <div className="text-2xl font-bold text-racing-red mb-2">
                {pitStrategies.race_conditions.track_evolution}
              </div>
              <p className="text-racing-silver">Track Evolution</p>
            </div>
          </div>
        </div>
      )}

      {/* Strategic Recommendations */}
      {pitStrategies?.recommendations && (
        <div className="card-racing">
          <h2 className="text-2xl font-bold text-racing mb-6 flex items-center space-x-2">
            <AlertTriangle className="w-6 h-6 text-racing-red" />
            <span>Strategic Recommendations</span>
          </h2>
          
          <div className="space-y-4">
            {pitStrategies.recommendations.map((recommendation, index) => (
              <div key={index} className="bg-racing-red/10 border border-racing-red/30 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-racing-red text-white rounded-full flex items-center justify-center text-sm font-bold mt-1">
                    {index + 1}
                  </div>
                  <p className="text-white flex-1">{recommendation}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Driver Strategies */}
      {pitStrategies?.strategies && (
        <div className="card-racing">
          <h2 className="text-2xl font-bold text-racing mb-6 flex items-center space-x-2">
            <Users className="w-6 h-6 text-racing-red" />
            <span>Driver Pit Strategies</span>
          </h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {pitStrategies.strategies.map((strategy, index) => (
              <div key={index} className="bg-racing-black/50 rounded-lg p-6 border border-racing-silver/20">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-white">{strategy.vehicle_id}</h3>
                    <p className="text-racing-silver">
                      Current Position: P{strategy.current_position}
                    </p>
                  </div>
                  <div className={`px-3 py-1 rounded-full border text-sm font-medium ${getStrategyTypeColor(strategy.strategy_type)}`}>
                    {strategy.strategy_type}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-racing-red mb-1">
                      {strategy.optimal_pit_lap}
                    </div>
                    <p className="text-racing-silver text-sm">Optimal Pit Lap</p>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-racing-red mb-1">
                      {strategy.predicted_time_loss.toFixed(1)}s
                    </div>
                    <p className="text-racing-silver text-sm">Time Loss</p>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-racing-silver">Predicted Position:</span>
                    <span className="text-white font-bold">P{strategy.predicted_track_position}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-racing-silver">Confidence:</span>
                    <span className={`font-bold ${getConfidenceColor(strategy.confidence)}`}>
                      {(strategy.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="w-full bg-racing-black rounded-full h-3">
                    <div 
                      className={`h-3 rounded-full transition-all duration-500 ${
                        strategy.confidence > 0.8 ? 'bg-racing-green' :
                        strategy.confidence > 0.6 ? 'bg-racing-yellow' :
                        'bg-racing-red'
                      }`}
                      style={{ width: `${strategy.confidence * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Strategic Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Pit Window Optimizer */}
        <div className="card-racing">
          <h3 className="text-xl font-bold text-racing mb-6 flex items-center space-x-2">
            <Target className="w-5 h-5 text-racing-red" />
            <span>Pit Window Analysis</span>
          </h3>
          
          <div className="space-y-4">
            <div className="bg-racing-black/30 rounded-lg p-4">
              <h4 className="font-bold text-white mb-2">Optimal Window</h4>
              <p className="text-racing-silver text-sm mb-3">
                Based on fuel consumption, tire degradation, and track position
              </p>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <div className="text-lg font-bold text-racing-green">
                    Lap {raceData?.current_lap + 3 || 'N/A'}
                  </div>
                  <p className="text-xs text-racing-silver">Window Opens</p>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-racing-red">
                    Lap {raceData?.current_lap + 8 || 'N/A'}
                  </div>
                  <p className="text-xs text-racing-silver">Window Closes</p>
                </div>
              </div>
            </div>

            <div className="bg-racing-black/30 rounded-lg p-4">
              <h4 className="font-bold text-white mb-2">Strategic Factors</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-racing-silver">Tire Degradation:</span>
                  <span className="text-racing-yellow">Medium</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-racing-silver">Fuel Critical:</span>
                  <span className="text-racing-green">No</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-racing-silver">Traffic Impact:</span>
                  <span className="text-racing-red">High</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Real-Time Insights */}
        <div className="card-racing">
          <h3 className="text-xl font-bold text-racing mb-6 flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-racing-red" />
            <span>Real-Time Insights</span>
          </h3>
          
          <div className="space-y-4">
            <div className="bg-racing-green/10 border border-racing-green/30 rounded-lg p-4">
              <h4 className="font-bold text-racing-green mb-2">Opportunity</h4>
              <p className="text-white text-sm">
                Gap between Car-1 and Car-2 is widening. Undercut opportunity available in 2 laps.
              </p>
            </div>
            
            <div className="bg-racing-yellow/10 border border-racing-yellow/30 rounded-lg p-4">
              <h4 className="font-bold text-racing-yellow mb-2">Warning</h4>
              <p className="text-white text-sm">
                Track temperature rising. Tire degradation increasing for all drivers.
              </p>
            </div>
            
            <div className="bg-racing-red/10 border border-racing-red/30 rounded-lg p-4">
              <h4 className="font-bold text-racing-red mb-2">Critical</h4>
              <p className="text-white text-sm">
                Car-3 fuel levels critical. Must pit within next 2 laps or risk retirement.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Strategy Timeline */}
      <div className="card-racing">
        <h2 className="text-2xl font-bold text-racing mb-6 flex items-center space-x-2">
          <Clock className="w-6 h-6 text-racing-red" />
          <span>Strategy Timeline</span>
        </h2>
        
        <div className="relative">
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-racing-red"></div>
          
          <div className="space-y-6">
            {[
              { lap: raceData?.current_lap + 2 || 5, event: 'Pit window opens for leaders', type: 'info' },
              { lap: raceData?.current_lap + 4 || 7, event: 'Optimal undercut opportunity', type: 'opportunity' },
              { lap: raceData?.current_lap + 6 || 9, event: 'Car-3 fuel critical point', type: 'warning' },
              { lap: raceData?.current_lap + 8 || 11, event: 'Pit window closes', type: 'critical' }
            ].map((item, index) => (
              <div key={index} className="relative flex items-center space-x-4">
                <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center text-sm font-bold ${
                  item.type === 'info' ? 'bg-racing-silver border-racing-silver text-black' :
                  item.type === 'opportunity' ? 'bg-racing-green border-racing-green text-white' :
                  item.type === 'warning' ? 'bg-racing-yellow border-racing-yellow text-black' :
                  'bg-racing-red border-racing-red text-white'
                }`}>
                  {item.lap}
                </div>
                <div className="flex-1 bg-racing-black/30 rounded-lg p-3">
                  <p className="text-white font-medium">{item.event}</p>
                  <p className="text-racing-silver text-sm">Lap {item.lap}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Strategy;