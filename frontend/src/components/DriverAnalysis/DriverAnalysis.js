import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { User } from 'lucide-react';
import { ApiService } from '../../services/apiService';
import DriverSelector from './DriverSelector';
import PerformanceChart from './PerformanceChart';
import CoachingInsights from './CoachingInsights';

const DriverAnalysis = () => {
  const { driverId } = useParams();
  const [selectedDriver, setSelectedDriver] = useState(driverId || null);
  const [drivers, setDrivers] = useState([]);
  const [driverData, setDriverData] = useState(null);
  const [coachingData, setCoachingData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch list of drivers
  useEffect(() => {
    const fetchDrivers = async () => {
      try {
        const data = await ApiService.getDrivers();
        setDrivers(data);
        if (!selectedDriver && data.length > 0) {
          setSelectedDriver(data[0].vehicle_id);
        }
      } catch (error) {
        console.error('Failed to fetch drivers:', error);
      }
    };
    fetchDrivers();
  }, [selectedDriver]);

  // Fetch detailed driver data
  useEffect(() => {
    if (selectedDriver) {
      const fetchDriverData = async () => {
        setLoading(true);
        try {
          // Fetch comprehensive ML analysis
          const comp = await ApiService.getComprehensiveML(selectedDriver);

          // Fetch real AI coaching
          const coaching = await ApiService.getDriverCoaching(selectedDriver);

          // Normalize lap data
          const lapRows = comp.laps || [];
          const mappedLaps = lapRows.map(r => ({
            lap_number: r.lap_number,
            lap_time: r.lap_time_ms ? r.lap_time_ms / 1000 : 0
          }));

          // Use real AI coaching if available, otherwise build from ML analysis
          let coachingPayload;
          
          if (coaching && coaching.summary) {
            // Use real AI coaching from backend
            coachingPayload = {
              coaching_summary: {
                primary_recommendation: coaching.summary.executive_summary || 'Focus on consistency and sector optimization',
                improvement_areas: coaching.cards?.map(card => card.content || card.summary).slice(0, 3) || []
              },
              siwtl: {
                target_lap_time: coaching.cards?.find(c => c.potential_gain)?.potential_gain || null,
                theoretical_best: null
              },
              sector_analysis: {},
              action_items: coaching.cards?.flatMap(card => card.recommendations || card.action_items || []).slice(0, 4) || []
            };
          } else {
            // Fallback to ML analysis
            const siwtl = comp.comprehensive_analysis?.siwtl_targets || {};
            const combined = comp.comprehensive_analysis?.combined_insights || {};
            
            coachingPayload = {
              coaching_summary: {
                primary_recommendation: combined.primary_focus || combined.recommendation || 'Focus on consistency and sector optimization',
                improvement_areas: combined.specific_recommendations || []
              },
              siwtl: {
                target_lap_time: siwtl.siwtl_lap || (siwtl.target && siwtl.target.lap_time) || null,
                theoretical_best: siwtl.theoretical_best || null
              },
              sector_analysis: siwtl.sector_analysis || {},
              action_items: combined.specific_recommendations || []
            };
          }

          setDriverData({ laps: mappedLaps });
          setCoachingData(coachingPayload);
        } catch (error) {
          console.error('Failed to fetch driver data:', error);
        } finally {
          setLoading(false);
        }
      };
      fetchDriverData();
    }
  }, [selectedDriver]);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div>
          <h1 className="text-racing text-3xl font-bold text-white mb-2">
            👤 Driver Performance Analysis
          </h1>
          <p className="text-racing-silver">
            Detailed performance insights and AI coaching
          </p>
        </div>
        
        <DriverSelector 
          drivers={drivers}
          selectedDriver={selectedDriver}
          onDriverChange={setSelectedDriver}
        />
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-racing-red"></div>
        </div>
      ) : selectedDriver ? (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* Performance Charts */}
          <div className="xl:col-span-2">
            <PerformanceChart driverData={driverData} driverId={selectedDriver} />
          </div>
          
          {/* Coaching Insights */}
          <div className="xl:col-span-1">
            <CoachingInsights coachingData={coachingData} driverId={selectedDriver} />
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          <User className="w-16 h-16 text-racing-silver/50 mx-auto mb-4" />
          <p className="text-racing-silver">Select a driver to view analysis</p>
        </div>
      )}
    </div>
  );
};

export default DriverAnalysis;