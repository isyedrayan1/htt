import React, { useState, useEffect } from 'react';
import { Trophy, ChevronRight, Users, TrendingUp, Zap, Target, Activity } from 'lucide-react';
import { Link } from 'react-router-dom';
import { ApiService } from '../../services/apiService';

const Dashboard = () => {
  const [fleetData, setFleetData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFleetData = async () => {
      try {
        const data = await ApiService.getFleetSummary();
        console.log('Fleet data:', data);
        setFleetData(data);
      } catch (error) {
        console.error('Failed to fetch fleet data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchFleetData();
  }, []);

  if (loading) {
    return (
      <div className="p-8 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-racing-red mx-auto mb-4"></div>
          <p className="text-racing-silver">Loading fleet data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="racing-gradient rounded-xl p-6 text-center">
        <h1 className="text-racing text-3xl font-bold mb-2">
          🏎️ AI Driver Coaching Platform
        </h1>
        <p className="text-lg text-white/90">
          Toyota Gazoo Racing - COTA Performance Analysis
        </p>
        <p className="text-white/70 mt-1">
          AI-Powered Driver Intelligence: "Hack the Track" Challenge
        </p>
      </div>

      {/* Quick Actions / Navigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link to="/drivers" className="card-racing hover:bg-racing-gray/70 transition-all duration-200 group">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-racing mb-1">Driver Analysis</h3>
              <p className="text-sm text-racing-silver">Performance insights</p>
            </div>
            <ChevronRight className="w-6 h-6 text-racing-red group-hover:translate-x-1 transition-transform" />
          </div>
        </Link>

        <Link to="/compare" className="card-racing hover:bg-racing-gray/70 transition-all duration-200 group">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-racing mb-1">Compare Drivers</h3>
              <p className="text-sm text-racing-silver">Head-to-head analysis</p>
            </div>
            <ChevronRight className="w-6 h-6 text-racing-red group-hover:translate-x-1 transition-transform" />
          </div>
        </Link>

        <Link to="/evidence" className="card-racing hover:bg-racing-gray/70 transition-all duration-200 group">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-racing mb-1">Evidence Explorer</h3>
              <p className="text-sm text-racing-silver">Telemetry deep dive</p>
            </div>
            <ChevronRight className="w-6 h-6 text-racing-red group-hover:translate-x-1 transition-transform" />
          </div>
        </Link>

        <Link to="/strategy" className="card-racing hover:bg-racing-gray/70 transition-all duration-200 group">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-racing mb-1">Strategy Center</h3>
              <p className="text-sm text-racing-silver">Race strategy & pits</p>
            </div>
            <ChevronRight className="w-6 h-6 text-racing-red group-hover:translate-x-1 transition-transform" />
          </div>
        </Link>
      </div>

      {/* Fleet-Wide Metrics */}
      {fleetData && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="metric-card">
              <div className="flex items-center justify-between mb-2">
                <Users className="w-5 h-5 text-racing-red" />
                <span className="text-2xl font-bold">{fleetData.fleet_metrics.total_drivers}</span>
              </div>
              <p className="text-sm text-racing-silver">Total Drivers</p>
            </div>

            <div className="metric-card">
              <div className="flex items-center justify-between mb-2">
                <Activity className="w-5 h-5 text-racing-red" />
                <span className="text-2xl font-bold">{fleetData.fleet_metrics.total_laps}</span>
              </div>
              <p className="text-sm text-racing-silver">Total Laps</p>
            </div>

            <div className="metric-card">
              <div className="flex items-center justify-between mb-2">
                <Zap className="w-5 h-5 text-racing-red" />
                <span className="text-2xl font-bold">{fleetData.fleet_metrics.fastest_lap.toFixed(3)}s</span>
              </div>
              <p className="text-sm text-racing-silver">Fastest Lap</p>
              <p className="text-xs text-racing-silver/70 mt-1">{fleetData.fleet_metrics.fastest_driver}</p>
            </div>

            <div className="metric-card">
              <div className="flex items-center justify-between mb-2">
                <Target className="w-5 h-5 text-racing-red" />
                <span className="text-2xl font-bold">{fleetData.fleet_metrics.fleet_consistency.toFixed(1)}%</span>
              </div>
              <p className="text-sm text-racing-silver">Fleet Consistency</p>
            </div>
          </div>

          {/* AI Session Insights */}
          {fleetData.ai_insights && (
            <div className="card-racing">
              <h2 className="text-xl font-bold text-racing mb-3 flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                AI Session Insights
              </h2>
              <div className="bg-racing-gray/30 rounded-lg p-4 mb-3">
                <p className="text-white/90 leading-relaxed text-sm">{fleetData.ai_insights.summary}</p>
                <p className="text-xs text-racing-silver/70 mt-2">Generated by: {fleetData.ai_insights.generated_by}</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                {fleetData.ai_insights.highlights.map((highlight, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-sm">
                    <span className="text-racing-red mt-0.5">•</span>
                    <p className="text-white/80">{highlight}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Top Performers Leaderboard */}
          <div className="card-racing">
            <h2 className="text-xl font-bold text-racing mb-4 flex items-center gap-2">
              <Trophy className="w-5 h-5" />
              Top Performers
            </h2>
            <div className="space-y-3">
              {fleetData.top_performers.map((driver, index) => (
                <div key={driver.vehicle_id} className="bg-racing-gray/30 rounded-lg p-3 flex items-center gap-4">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                    index === 0 ? 'bg-yellow-500 text-black' :
                    index === 1 ? 'bg-gray-400 text-black' :
                    index === 2 ? 'bg-orange-600 text-white' :
                    'bg-racing-silver/30 text-white'
                  }`}>
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-bold text-white">{driver.vehicle_id}</h4>
                    <p className="text-xs text-racing-silver">
                      Best: {driver.best_lap.toFixed(3)}s • Avg: {driver.avg_lap.toFixed(3)}s • {driver.lap_count} laps
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-racing">{driver.consistency_score.toFixed(1)}%</p>
                    <p className="text-xs text-racing-silver">Consistency</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Session Info */}
          <div className="card-racing">
            <h2 className="text-xl font-bold text-racing mb-4">Session Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-racing-silver mb-1">Track</p>
                <p className="text-white font-semibold">{fleetData.session_info.track}</p>
              </div>
              <div>
                <p className="text-racing-silver mb-1">Session Type</p>
                <p className="text-white font-semibold">{fleetData.session_info.session_type}</p>
              </div>
              <div>
                <p className="text-racing-silver mb-1">Total Distance</p>
                <p className="text-white font-semibold">{fleetData.session_info.total_distance_km} km</p>
              </div>
            </div>
          </div>

          {/* Most Consistent Driver Highlight */}
          {fleetData.most_consistent && (
            <div className="card-racing bg-gradient-to-r from-racing-gray/50 to-racing-gray/30">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-racing mb-1">🎯 Most Consistent Driver</h3>
                  <p className="text-2xl font-bold text-white">{fleetData.most_consistent.vehicle_id}</p>
                  <p className="text-sm text-racing-silver mt-1">
                    Consistency Score: {fleetData.most_consistent.consistency_score.toFixed(1)}% • 
                    Avg Lap: {fleetData.most_consistent.avg_lap.toFixed(3)}s
                  </p>
                </div>
                <div className="text-6xl">🏆</div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Dashboard;