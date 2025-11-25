import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Activity, BarChart, TrendingUp, AlertTriangle, Gauge, Target, Zap } from 'lucide-react';
import Plot from 'react-plotly.js';
import { ApiService } from '../../services/apiService';

const EvidenceExplorer = () => {
  const location = useLocation();
  const [drivers, setDrivers] = useState([]);
  const [selectedDriver, setSelectedDriver] = useState(location.state?.driverId || 'GR86-063-113');
  const [selectedLap, setSelectedLap] = useState(17);
  
  const [lapsData, setLapsData] = useState(null);
  const [telemetryTrace, setTelemetryTrace] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [siwtlData, setSiwtlData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [traceLoading, setTraceLoading] = useState(false);

  // Fetch drivers list
  useEffect(() => {
    const fetchDrivers = async () => {
      try {
        const data = await ApiService.getDrivers();
        setDrivers(data);
      } catch (error) {
        console.error('Failed to fetch drivers:', error);
      }
    };
    fetchDrivers();
  }, []);

  // Fetch session overview data
  useEffect(() => {
    if (selectedDriver) {
      const fetchSessionData = async () => {
        setLoading(true);
        try {
          const [laps, anomalyData, siwtl] = await Promise.allSettled([
            ApiService.getTelemetryHistory(selectedDriver),
            ApiService.getDPTAD(selectedDriver),
            ApiService.getSIWTL(selectedDriver)
          ]);

          if (laps.status === 'fulfilled') setLapsData(laps.value);
          if (anomalyData.status === 'fulfilled') setAnomalies(anomalyData.value?.anomalies || []);
          if (siwtl.status === 'fulfilled') setSiwtlData(siwtl.value?.result || siwtl.value);
          
        } catch (error) {
          console.error('Failed to fetch session data:', error);
        } finally {
          setLoading(false);
        }
      };
      fetchSessionData();
    }
  }, [selectedDriver]);

  // Fetch telemetry trace
  useEffect(() => {
    if (selectedDriver && selectedLap) {
      const fetchTrace = async () => {
        setTraceLoading(true);
        try {
          const trace = await ApiService.getLapTelemetry(selectedDriver, selectedLap);
          setTelemetryTrace(trace?.telemetry);
        } catch (error) {
          console.error('Failed to fetch telemetry trace:', error);
          setTelemetryTrace(null);
        } finally {
          setTraceLoading(false);
        }
      };
      fetchTrace();
    }
  }, [selectedDriver, selectedLap]);

  // Calculate sector performance
  const sectorPerformance = lapsData?.laps ? lapsData.laps.map(lap => ({
    lap: lap.lap_number,
    s1: lap.sector_1 || 0,
    s2: lap.sector_2 || 0,
    s3: lap.sector_3 || 0
  })).filter(l => l.s1 > 0 && l.s2 > 0 && l.s3 > 0) : [];

  // Calculate consistency metrics
  const lapTimes = lapsData?.laps?.map(l => l.lap_time) || [];
  const avgLapTime = lapTimes.length > 0 ? lapTimes.reduce((a, b) => a + b, 0) / lapTimes.length : 0;
  const lapTimeStd = lapTimes.length > 1 ? Math.sqrt(lapTimes.reduce((sum, t) => sum + Math.pow(t - avgLapTime, 2), 0) / lapTimes.length) : 0;
  const consistencyScore = avgLapTime > 0 ? Math.max(0, 100 - (lapTimeStd / avgLapTime * 100)) : 0;

  // Chart: Lap Time Progression
  const lapTimesChart = {
    data: [{
      x: lapsData?.laps?.map(l => l.lap_number) || [],
      y: lapsData?.laps?.map(l => l.lap_time) || [],
      type: 'scatter',
      mode: 'lines+markers',
      marker: { color: '#dc2626', size: 8 },
      line: { color: '#dc2626', width: 2 },
      name: 'Lap Times'
    }],
    layout: {
      title: { text: 'Lap Time Progression', font: { color: '#fff', size: 14 } },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: { color: '#9CA3AF', size: 10 },
      xaxis: { title: 'Lap', gridcolor: '#374151' },
      yaxis: { title: 'Time (s)', gridcolor: '#374151' },
      margin: { t: 40, r: 20, l: 50, b: 40 },
      height: 300
    },
    config: { displayModeBar: false }
  };

  // Chart: Telemetry Trace
  const traceChart = {
    data: [
      {
        x: telemetryTrace?.distance || [],
        y: telemetryTrace?.speed || [],
        type: 'scatter',
        mode: 'lines',
        name: 'Speed',
        line: { color: '#3b82f6', width: 1.5 },
        yaxis: 'y'
      },
      {
        x: telemetryTrace?.distance || [],
        y: telemetryTrace?.throttle || [],
        type: 'scatter',
        mode: 'lines',
        name: 'Throttle',
        line: { color: '#10b981', width: 1 },
        yaxis: 'y2'
      },
      {
        x: telemetryTrace?.distance || [],
        y: telemetryTrace?.brake || [],
        type: 'scatter',
        mode: 'lines',
        name: 'Brake',
        line: { color: '#ef4444', width: 1 },
        yaxis: 'y2'
      }
    ],
    layout: {
      title: { text: `Telemetry - Lap ${selectedLap}`, font: { color: '#fff', size: 14 } },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: { color: '#9CA3AF', size: 10 },
      grid: { rows: 2, columns: 1, pattern: 'independent' },
      xaxis: { title: 'Distance (m)', gridcolor: '#374151' },
      yaxis: { title: 'Speed', gridcolor: '#374151', domain: [0.55, 1] },
      yaxis2: { title: 'Input %', gridcolor: '#374151', domain: [0, 0.45], range: [-5, 105] },
      legend: { orientation: 'h', y: 1.1, font: { size: 9 } },
      margin: { t: 50, r: 20, l: 50, b: 40 },
      height: 300
    },
    config: { displayModeBar: false }
  };

  // Chart: Sector Comparison
  const sectorChart = {
    data: [
      {
        x: sectorPerformance.map(s => s.lap),
        y: sectorPerformance.map(s => s.s1),
        type: 'bar',
        name: 'Sector 1',
        marker: { color: '#3b82f6' }
      },
      {
        x: sectorPerformance.map(s => s.lap),
        y: sectorPerformance.map(s => s.s2),
        type: 'bar',
        name: 'Sector 2',
        marker: { color: '#10b981' }
      },
      {
        x: sectorPerformance.map(s => s.lap),
        y: sectorPerformance.map(s => s.s3),
        type: 'bar',
        name: 'Sector 3',
        marker: { color: '#f59e0b' }
      }
    ],
    layout: {
      title: { text: 'Sector Times by Lap', font: { color: '#fff', size: 14 } },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: { color: '#9CA3AF', size: 10 },
      barmode: 'group',
      xaxis: { title: 'Lap', gridcolor: '#374151' },
      yaxis: { title: 'Time (s)', gridcolor: '#374151' },
      legend: { orientation: 'h', y: 1.1, font: { size: 9 } },
      margin: { t: 40, r: 20, l: 50, b: 40 },
      height: 250
    },
    config: { displayModeBar: false }
  };

  if (loading && !lapsData) {
    return (
      <div className="p-8 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-racing-red mx-auto mb-4" />
          <p className="text-racing-silver">Loading telemetry evidence...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="racing-gradient rounded-xl p-6 text-center">
        <h1 className="text-racing text-3xl font-bold mb-2">🔍 Evidence Explorer</h1>
        <p className="text-lg text-white/90">Deep Telemetry Analysis & Performance Evidence</p>
        <p className="text-white/70 mt-1">Driver {selectedDriver} • COTA Detailed Analytics</p>
      </div>

      {/* Controls */}
      <div className="card-racing">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold text-racing mb-2">Driver</label>
            <select 
              value={selectedDriver || ''} 
              onChange={(e) => setSelectedDriver(e.target.value)}
              className="w-full bg-racing-gray text-white rounded-lg px-4 py-2 border border-racing-silver/30"
            >
              {drivers.map((driver) => (
                <option key={driver.vehicle_id} value={driver.vehicle_id}>
                  {driver.vehicle_id}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-semibold text-racing mb-2">Focus Lap</label>
            <select 
              value={selectedLap} 
              onChange={(e) => setSelectedLap(Number(e.target.value))}
              className="w-full bg-racing-gray text-white rounded-lg px-4 py-2 border border-racing-silver/30"
            >
               {lapsData?.laps && lapsData.laps.length > 0 ? (
                  lapsData.laps.map((l) => (
                    <option key={l.lap_number} value={l.lap_number}>
                      Lap {l.lap_number} ({l.lap_time.toFixed(2)}s)
                    </option>
                  ))
               ) : (
                  <option value={17}>Lap 17</option>
               )}
            </select>
          </div>
        </div>
      </div>

      {/* Performance Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="metric-card">
          <div className="flex items-center justify-between mb-2">
            <Activity className="w-5 h-5 text-racing-red" />
            <span className="text-xl font-bold">{siwtlData?.siwtl_lap?.toFixed(2) || '--'}s</span>
          </div>
          <p className="text-sm text-racing-silver">Theoretical Best</p>
        </div>

        <div className="metric-card">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-5 h-5 text-racing-red" />
            <span className="text-xl font-bold">{Math.abs(siwtlData?.potential_gain_sec || 0).toFixed(2)}s</span>
          </div>
          <p className="text-sm text-racing-silver">Potential Gain</p>
        </div>

        <div className="metric-card">
          <div className="flex items-center justify-between mb-2">
            <Target className="w-5 h-5 text-racing-red" />
            <span className="text-xl font-bold">{consistencyScore.toFixed(1)}%</span>
          </div>
          <p className="text-sm text-racing-silver">Consistency</p>
        </div>

        <div className="metric-card">
          <div className="flex items-center justify-between mb-2">
            <AlertTriangle className="w-5 h-5 text-racing-red" />
            <span className="text-xl font-bold">{anomalies.length}</span>
          </div>
          <p className="text-sm text-racing-silver">Anomalies</p>
        </div>
      </div>

      {/* Main Graphs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card-racing">
            {traceLoading ? (
                <div className="h-[300px] flex items-center justify-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-racing-red"></div>
                </div>
            ) : telemetryTrace && telemetryTrace.speed?.length > 0 ? (
                <Plot
                    data={traceChart.data}
                    layout={traceChart.layout}
                    config={traceChart.config}
                    style={{width: "100%", height: "300px"}}
                />
            ) : (
                <div className="h-[300px] flex items-center justify-center text-racing-silver text-sm">
                    No telemetry data for this lap
                </div>
            )}
        </div>

        <div className="card-racing">
            <Plot
                data={lapTimesChart.data}
                layout={lapTimesChart.layout}
                config={lapTimesChart.config}
                style={{width: "100%", height: "300px"}}
            />
        </div>
      </div>

      {/* Sector Analysis */}
      {sectorPerformance.length > 0 && (
        <div className="card-racing">
          <Plot
              data={sectorChart.data}
              layout={sectorChart.layout}
              config={sectorChart.config}
              style={{width: "100%", height: "250px"}}
          />
        </div>
      )}

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="card-racing">
          <h3 className="text-lg font-bold text-racing mb-3 flex items-center gap-2">
            <Gauge className="w-5 h-5" />
            Lap Statistics
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-racing-silver">Average Lap Time:</span>
              <span className="text-white font-semibold">{avgLapTime.toFixed(2)}s</span>
            </div>
            <div className="flex justify-between">
              <span className="text-racing-silver">Std Deviation:</span>
              <span className="text-white font-semibold">{lapTimeStd.toFixed(2)}s</span>
            </div>
            <div className="flex justify-between">
              <span className="text-racing-silver">Best Lap:</span>
              <span className="text-white font-semibold">{Math.min(...lapTimes).toFixed(2)}s</span>
            </div>
            <div className="flex justify-between">
              <span className="text-racing-silver">Total Laps:</span>
              <span className="text-white font-semibold">{lapTimes.length}</span>
            </div>
          </div>
        </div>

        <div className="card-racing">
          <h3 className="text-lg font-bold text-racing mb-3 flex items-center gap-2">
            <Zap className="w-5 h-5" />
            SIWTL Insights
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-racing-silver">Achievability:</span>
              <span className="text-white font-semibold">{((siwtlData?.achievability_score || 0) * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-racing-silver">Algorithm:</span>
              <span className="text-white font-semibold text-xs">SIWTL v2.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-racing-silver">Analysis Status:</span>
              <span className="text-green-400 font-semibold">✓ Complete</span>
            </div>
          </div>
        </div>

        <div className="card-racing">
          <h3 className="text-lg font-bold text-racing mb-3 flex items-center gap-2">
            <BarChart className="w-5 h-5" />
            Session Summary
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-racing-silver">Track:</span>
              <span className="text-white font-semibold">COTA</span>
            </div>
            <div className="flex justify-between">
              <span className="text-racing-silver">Vehicle:</span>
              <span className="text-white font-semibold">{selectedDriver}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-racing-silver">Data Points:</span>
              <span className="text-white font-semibold">{telemetryTrace?.distance?.length || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Anomalies Table */}
      {anomalies.length > 0 && (
        <div className="card-racing">
          <h2 className="text-xl font-bold text-racing mb-4">Detected Anomalies</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead>
                <tr className="border-b border-racing-silver/30">
                  <th className="pb-2 text-racing">Lap</th>
                  <th className="pb-2 text-racing">Type</th>
                  <th className="pb-2 text-racing">Severity</th>
                  <th className="pb-2 text-racing">Description</th>
                </tr>
              </thead>
              <tbody>
                {anomalies.slice(0, 5).map((anomaly, index) => (
                  <tr key={index} className="border-b border-racing-silver/10">
                    <td className="py-2 text-white">{anomaly.lap_number || '--'}</td>
                    <td className="py-2 text-racing-silver capitalize text-xs">{anomaly.anomaly_type?.replace('_', ' ') || 'Unknown'}</td>
                    <td className="py-2">
                      <span className={`inline-block w-2 h-2 rounded-full mr-2 ${
                        anomaly.severity === 'high' ? 'bg-red-500' :
                        anomaly.severity === 'medium' ? 'bg-yellow-500' :
                        'bg-green-500'
                      }`}></span>
                      <span className="text-racing-silver capitalize text-xs">{anomaly.severity || 'Low'}</span>
                    </td>
                    <td className="py-2 text-racing-silver text-xs">{anomaly.description || 'No description'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default EvidenceExplorer;