import React from 'react';
import { Zap, Brain, Trophy, Rocket, Timer, Flag } from 'lucide-react';

const LiveRace = ({ raceData }) => {
  if (!raceData) {
    return (
      <div className="p-8 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-racing-red mx-auto mb-4"></div>
          <p className="text-racing-silver">Loading live telemetry...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="racing-gradient rounded-xl p-8 text-center">
        <div className="flex items-center justify-center mb-4">
          <Zap className="w-12 h-12 text-yellow-400 mr-4" />
          <h1 className="text-racing text-4xl font-bold">
            Live Race Intelligence
          </h1>
          <Zap className="w-12 h-12 text-yellow-400 ml-4" />
        </div>
        <div className="flex justify-center space-x-8 mt-4">
          <div className="text-center">
            <p className="text-racing-silver text-sm">Race Time</p>
            <p className="text-2xl font-bold font-mono text-white">{raceData.race_time}</p>
          </div>
          <div className="text-center">
            <p className="text-racing-silver text-sm">Lap</p>
            <p className="text-2xl font-bold font-mono text-white">{raceData.current_lap} / {raceData.total_laps}</p>
          </div>
          <div className="text-center">
            <p className="text-racing-silver text-sm">Status</p>
            <p className="text-2xl font-bold font-mono text-green-400">{raceData.race_status}</p>
          </div>
        </div>
      </div>

      {/* Live Leaderboard */}
      <div className="card-racing">
        <h2 className="text-2xl font-bold text-racing mb-6 flex items-center">
          <Flag className="w-6 h-6 text-racing-red mr-2" />
          Live Leaderboard
        </h2>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="text-racing-silver border-b border-racing-gray/30">
                <th className="p-4">Pos</th>
                <th className="p-4">Driver</th>
                <th className="p-4">Last Lap</th>
                <th className="p-4">Gap</th>
                <th className="p-4">Pit Window</th>
                <th className="p-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-racing-gray/20">
              {raceData.positions?.map((driver) => (
                <tr key={driver.vehicle_id} className="hover:bg-racing-gray/10 transition-colors">
                  <td className="p-4">
                    <span className={`
                      inline-flex items-center justify-center w-8 h-8 rounded-full font-bold
                      ${driver.position === 1 ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500' : 
                        driver.position === 2 ? 'bg-gray-400/20 text-gray-300 border border-gray-400' :
                        driver.position === 3 ? 'bg-orange-700/20 text-orange-400 border border-orange-700' :
                        'text-racing-silver'}
                    `}>
                      {driver.position}
                    </span>
                  </td>
                  <td className="p-4 font-bold text-white">{driver.vehicle_id}</td>
                  <td className="p-4 font-mono text-racing-silver">{driver.last_lap_time?.toFixed(2)}s</td>
                  <td className="p-4 font-mono text-racing-silver">+{driver.gap_to_leader?.toFixed(2)}s</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      driver.pit_window?.urgency === 'HIGH' ? 'bg-red-500/20 text-red-400' :
                      driver.pit_window?.urgency === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-green-500/20 text-green-400'
                    }`}>
                      {driver.pit_window?.urgency || 'LOW'}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className="text-green-400 text-sm flex items-center">
                      <div className="w-2 h-2 rounded-full bg-green-400 mr-2 animate-pulse"></div>
                      On Track
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Technology Stack & Info */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="card-racing">
          <h2 className="text-xl font-bold text-racing mb-4 flex items-center">
            <Brain className="w-6 h-6 text-racing-red mr-2" />
            System Intelligence
          </h2>
          <div className="space-y-4">
             <div className="bg-racing-gray/20 rounded-lg p-4">
               <h4 className="font-bold text-white mb-1">AI Strategy Engine</h4>
               <p className="text-sm text-racing-silver">Processing real-time telemetry for pit window optimization.</p>
             </div>
             <div className="bg-racing-gray/20 rounded-lg p-4">
               <h4 className="font-bold text-white mb-1">Anomaly Detection</h4>
               <p className="text-sm text-racing-silver">Monitoring 9 signal channels for performance irregularities.</p>
             </div>
          </div>
        </div>

        <div className="card-racing">
          <h2 className="text-xl font-bold text-racing mb-4 flex items-center">
            <Rocket className="w-6 h-6 text-racing-red mr-2" />
            Backend Performance
          </h2>
          <div className="space-y-4">
             <div className="flex justify-between items-center border-b border-racing-gray/20 pb-2">
               <span className="text-racing-silver">Data Source</span>
               <span className="text-white font-mono">DuckDB (COTA Dataset)</span>
             </div>
             <div className="flex justify-between items-center border-b border-racing-gray/20 pb-2">
               <span className="text-racing-silver">Latency</span>
               <span className="text-green-400 font-mono">&lt; 50ms</span>
             </div>
             <div className="flex justify-between items-center">
               <span className="text-racing-silver">Update Rate</span>
               <span className="text-white font-mono">5Hz</span>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveRace;