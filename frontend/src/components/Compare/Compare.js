import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Users, Zap, Target, Activity, BarChart2 } from 'lucide-react';
import Plot from 'react-plotly.js';
import { ApiService } from '../../services/apiService';
import DriverSelector from '../DriverAnalysis/DriverSelector';

const Compare = () => {
  const [drivers, setDrivers] = useState([]);
  const [selectedDriver1, setSelectedDriver1] = useState('GR86-063-113');
  const [selectedDriver2, setSelectedDriver2] = useState('GR86-065-5');
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch drivers on mount
  useEffect(() => {
    const fetchDrivers = async () => {
      try {
        const data = await ApiService.getDrivers();
        setDrivers(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error('Failed to fetch drivers:', error);
      }
    };
    fetchDrivers();
  }, []);

  // Fetch comparison data when both drivers selected
  useEffect(() => {
    if (selectedDriver1 && selectedDriver2 && selectedDriver1 !== selectedDriver2) {
      const fetchComparison = async () => {
        setLoading(true);
        try {
          const data = await ApiService.getComparison(selectedDriver1, selectedDriver2);
          console.log('Comparison data:', data);
          setComparisonData(data);
        } catch (error) {
          console.error('Failed to fetch comparison:', error);
          setComparisonData(null);
        } finally {
          setLoading(false);
        }
      };
      fetchComparison();
    }
  }, [selectedDriver1, selectedDriver2]);

  const getComparisonColor = (value1, value2, lowerIsBetter = false) => {
    if (lowerIsBetter) {
      return value1 < value2 ? 'text-green-400' : value1 > value2 ? 'text-red-400' : 'text-white';
    } else {
      return value1 > value2 ? 'text-green-400' : value1 < value2 ? 'text-red-400' : 'text-white';
    }
  };

  const getComparisonIcon = (value1, value2, lowerIsBetter = false) => {
    if (lowerIsBetter) {
      return value1 < value2 ? <TrendingUp className="inline w-5 h-5 ml-2" /> : value1 > value2 ? <TrendingDown className="inline w-5 h-5 ml-2" /> : null;
    } else {
      return value1 > value2 ? <TrendingUp className="inline w-5 h-5 ml-2" /> : value1 < value2 ? <TrendingDown className="inline w-5 h-5 ml-2" /> : null;
    }
  };

  // Lap progression chart
  const lapProgressionChart = comparisonData ? {
    data: [
      {
        x: comparisonData.lap_progression.driver1.lap_numbers,
        y: comparisonData.lap_progression.driver1.lap_times,
        type: 'scatter',
        mode: 'lines+markers',
        name: selectedDriver1,
        line: { color: '#3b82f6', width: 2 },
        marker: { size: 6 }
      },
      {
        x: comparisonData.lap_progression.driver2.lap_numbers,
        y: comparisonData.lap_progression.driver2.lap_times,
        type: 'scatter',
        mode: 'lines+markers',
        name: selectedDriver2,
        line: { color: '#ef4444', width: 2 },
        marker: { size: 6 }
      }
    ],
    layout: {
      title: { text: 'Lap Time Progression', font: { color: '#fff', size: 16 } },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: { color: '#9CA3AF', size: 11 },
      xaxis: { title: 'Lap Number', gridcolor: '#374151' },
      yaxis: { title: 'Lap Time (s)', gridcolor: '#374151' },
      legend: { orientation: 'h', y: 1.1 },
      margin: { t: 50, r: 20, l: 50, b: 40 },
      height: 350
    },
    config: { displayModeBar: false }
  } : null;

  // Sector comparison chart
  const sectorChart = comparisonData && comparisonData.sector_comparison ? {
    data: [
      {
        x: ['Sector 1', 'Sector 2', 'Sector 3'],
        y: [
          comparisonData.sector_comparison.sector_1_time?.driver1_avg || 0,
          comparisonData.sector_comparison.sector_2_time?.driver1_avg || 0,
          comparisonData.sector_comparison.sector_3_time?.driver1_avg || 0
        ],
        type: 'bar',
        name: selectedDriver1,
        marker: { color: '#3b82f6' }
      },
      {
        x: ['Sector 1', 'Sector 2', 'Sector 3'],
        y: [
          comparisonData.sector_comparison.sector_1_time?.driver2_avg || 0,
          comparisonData.sector_comparison.sector_2_time?.driver2_avg || 0,
          comparisonData.sector_comparison.sector_3_time?.driver2_avg || 0
        ],
        type: 'bar',
        name: selectedDriver2,
        marker: { color: '#ef4444' }
      }
    ],
    layout: {
      title: { text: 'Average Sector Times', font: { color: '#fff', size: 16 } },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: { color: '#9CA3AF', size: 11 },
      barmode: 'group',
      xaxis: { gridcolor: '#374151' },
      yaxis: { title: 'Time (s)', gridcolor: '#374151' },
      legend: { orientation: 'h', y: 1.1 },
      margin: { t: 50, r: 20, l: 50, b: 40 },
      height: 300
    },
    config: { displayModeBar: false }
  } : null;

  const ComparisonMetricCard = ({ title, value1, value2, unit = 's', lowerIsBetter = false, icon: Icon }) => (
    <div className="card-racing">
      <div className="flex items-center gap-2 mb-3">
        {Icon && <Icon className="w-5 h-5 text-racing-red" />}
        <h3 className="text-lg font-bold text-racing">{title}</h3>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="text-center">
          <div className={`text-2xl font-bold mb-1 ${getComparisonColor(value1, value2, lowerIsBetter)}`}>
            {value1?.toFixed(3)}{unit}
            {getComparisonIcon(value1, value2, lowerIsBetter)}
          </div>
          <p className="text-sm text-racing-silver">{selectedDriver1}</p>
        </div>
        <div className="text-center">
          <div className={`text-2xl font-bold mb-1 ${getComparisonColor(value2, value1, lowerIsBetter)}`}>
            {value2?.toFixed(3)}{unit}
            {getComparisonIcon(value2, value1, lowerIsBetter)}
          </div>
          <p className="text-sm text-racing-silver">{selectedDriver2}</p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="racing-gradient rounded-xl p-6 text-center">
        <h1 className="text-racing text-3xl font-bold mb-2 flex items-center justify-center gap-3">
          <Users className="w-8 h-8" />
          Driver Comparison
        </h1>
        <p className="text-lg text-white/90">Head-to-Head Performance Analysis</p>
        <p className="text-white/70 mt-1">Compare lap times, consistency, and sector performance</p>
      </div>

      {/* Driver Selectors */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card-racing">
          <h2 className="text-xl font-bold text-racing mb-3">Select Driver 1</h2>
          <DriverSelector
            drivers={drivers}
            selectedDriver={selectedDriver1}
            onDriverChange={setSelectedDriver1}
          />
        </div>
        <div className="card-racing">
          <h2 className="text-xl font-bold text-racing mb-3">Select Driver 2</h2>
          <DriverSelector
            drivers={drivers.filter(d => d.vehicle_id !== selectedDriver1)}
            selectedDriver={selectedDriver2}
            onDriverChange={setSelectedDriver2}
          />
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-racing-red"></div>
        </div>
      )}

      {/* Comparison Results */}
      {!loading && comparisonData && (
        <div className="space-y-6">
          {/* Head-to-Head Summary */}
          <div className="card-racing">
            <h2 className="text-2xl font-bold text-racing mb-4">Head-to-Head Summary</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-sm text-racing-silver mb-1">Faster Best Lap</p>
                <p className="text-xl font-bold text-racing">{comparisonData.head_to_head.faster_best_lap}</p>
                <p className="text-xs text-racing-silver mt-1">+{comparisonData.head_to_head.best_lap_delta.toFixed(3)}s advantage</p>
              </div>
              <div>
                <p className="text-sm text-racing-silver mb-1">Better Average</p>
                <p className="text-xl font-bold text-racing">{comparisonData.head_to_head.faster_avg_lap}</p>
                <p className="text-xs text-racing-silver mt-1">+{comparisonData.head_to_head.avg_lap_delta.toFixed(3)}s advantage</p>
              </div>
              <div>
                <p className="text-sm text-racing-silver mb-1">More Consistent</p>
                <p className="text-xl font-bold text-racing">{comparisonData.head_to_head.more_consistent}</p>
              </div>
            </div>
          </div>

          {/* Comparison Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <ComparisonMetricCard
              title="Best Lap"
              value1={comparisonData.driver1_metrics.best_lap}
              value2={comparisonData.driver2_metrics.best_lap}
              lowerIsBetter={true}
              icon={Zap}
            />
            <ComparisonMetricCard
              title="Average Lap"
              value1={comparisonData.driver1_metrics.avg_lap}
              value2={comparisonData.driver2_metrics.avg_lap}
              lowerIsBetter={true}
              icon={Activity}
            />
            <ComparisonMetricCard
              title="Consistency"
              value1={comparisonData.driver1_metrics.consistency_score}
              value2={comparisonData.driver2_metrics.consistency_score}
              unit="%"
              lowerIsBetter={false}
              icon={Target}
            />
            <ComparisonMetricCard
              title="Std Deviation"
              value1={comparisonData.driver1_metrics.std_dev}
              value2={comparisonData.driver2_metrics.std_dev}
              lowerIsBetter={true}
              icon={BarChart2}
            />
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {lapProgressionChart && (
              <div className="card-racing">
                <Plot
                  data={lapProgressionChart.data}
                  layout={lapProgressionChart.layout}
                  config={lapProgressionChart.config}
                  style={{width: "100%", height: "350px"}}
                />
              </div>
            )}
            {sectorChart && Object.keys(comparisonData.sector_comparison).length > 0 && (
              <div className="card-racing">
                <Plot
                  data={sectorChart.data}
                  layout={sectorChart.layout}
                  config={sectorChart.config}
                  style={{width: "100%", height: "300px"}}
                />
              </div>
            )}
          </div>

          {/* AI Summary */}
          {comparisonData.ai_summary && (
            <div className="card-racing">
              <h3 className="text-2xl font-bold text-racing mb-4">AI Analysis</h3>
              <div className="bg-racing-gray/30 rounded-lg p-4 mb-4">
                <p className="text-white/90 leading-relaxed">{comparisonData.ai_summary.text}</p>
                <p className="text-xs text-racing-silver/70 mt-3">Generated by: {comparisonData.ai_summary.generated_by}</p>
              </div>
              <div className="space-y-2">
                <h4 className="text-sm font-semibold text-racing mb-2">Key Findings:</h4>
                {comparisonData.ai_summary.key_findings.map((finding, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <span className="text-racing-red mt-1">•</span>
                    <p className="text-sm text-white/80">{finding}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Detailed Statistics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="card-racing">
              <h3 className="text-xl font-bold text-racing mb-3">{selectedDriver1} Statistics</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-racing-silver">Best Lap:</span>
                  <span className="text-white font-semibold">{comparisonData.driver1_metrics.best_lap.toFixed(3)}s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-racing-silver">Average Lap:</span>
                  <span className="text-white font-semibold">{comparisonData.driver1_metrics.avg_lap.toFixed(3)}s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-racing-silver">Median Lap:</span>
                  <span className="text-white font-semibold">{comparisonData.driver1_metrics.median_lap.toFixed(3)}s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-racing-silver">Worst Lap:</span>
                  <span className="text-white font-semibold">{comparisonData.driver1_metrics.worst_lap.toFixed(3)}s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-racing-silver">Total Laps:</span>
                  <span className="text-white font-semibold">{comparisonData.driver1_metrics.lap_count}</span>
                </div>
              </div>
            </div>

            <div className="card-racing">
              <h3 className="text-xl font-bold text-racing mb-3">{selectedDriver2} Statistics</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-racing-silver">Best Lap:</span>
                  <span className="text-white font-semibold">{comparisonData.driver2_metrics.best_lap.toFixed(3)}s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-racing-silver">Average Lap:</span>
                  <span className="text-white font-semibold">{comparisonData.driver2_metrics.avg_lap.toFixed(3)}s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-racing-silver">Median Lap:</span>
                  <span className="text-white font-semibold">{comparisonData.driver2_metrics.median_lap.toFixed(3)}s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-racing-silver">Worst Lap:</span>
                  <span className="text-white font-semibold">{comparisonData.driver2_metrics.worst_lap.toFixed(3)}s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-racing-silver">Total Laps:</span>
                  <span className="text-white font-semibold">{comparisonData.driver2_metrics.lap_count}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && !comparisonData && selectedDriver1 && selectedDriver2 && selectedDriver1 !== selectedDriver2 && (
        <div className="text-center py-12">
          <Users className="w-16 h-16 text-racing-silver/50 mx-auto mb-4" />
          <p className="text-racing-silver text-xl">No comparison data available</p>
          <p className="text-racing-silver/70 text-sm mt-2">Try selecting different drivers</p>
        </div>
      )}

      {!loading && (!selectedDriver1 || !selectedDriver2 || selectedDriver1 === selectedDriver2) && (
        <div className="text-center py-12">
          <Users className="w-16 h-16 text-racing-silver/50 mx-auto mb-4" />
          <p className="text-racing-silver text-xl">Select two different drivers to compare</p>
        </div>
      )}
    </div>
  );
};

export default Compare;