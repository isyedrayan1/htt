import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Brain, TrendingUp, Clock, Target, AlertCircle, ChevronRight } from 'lucide-react';
import { ApiService } from '../../services/apiService';

const CoachingCards = () => {
  const navigate = useNavigate();
  const [coachingData, setCoachingData] = useState(null);
  const [drivers, setDrivers] = useState([]);
  const [selectedDriver, setSelectedDriver] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch drivers list
  useEffect(() => {
    const fetchDrivers = async () => {
      try {
        const data = await ApiService.getDrivers();
        setDrivers(data);
        if (data.length > 0 && !selectedDriver) {
          setSelectedDriver(data[0].vehicle_id);
        }
      } catch (error) {
        console.error('Failed to fetch drivers:', error);
      }
    };
    fetchDrivers();
  }, []);

  // Fetch coaching data for selected driver
  useEffect(() => {
    if (selectedDriver) {
      const fetchCoachingData = async () => {
        setLoading(true);
        try {
          const coaching = await ApiService.getDriverCoaching(selectedDriver);
          setCoachingData(coaching);
        } catch (error) {
          console.error('Failed to fetch coaching data:', error);
          setCoachingData(null);
        } finally {
          setLoading(false);
        }
      };
      fetchCoachingData();
    }
  }, [selectedDriver]);

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'Braking':
        return <Target className="w-5 h-5" />;
      case 'Throttle':
        return <TrendingUp className="w-5 h-5" />;
      case 'Line Choice':
        return <AlertCircle className="w-5 h-5" />;
      case 'Consistency':
        return <Clock className="w-5 h-5" />;
      default:
        return <Brain className="w-5 h-5" />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'HIGH':
        return 'border-red-500 bg-red-500/10';
      case 'MEDIUM':
        return 'border-yellow-500 bg-yellow-500/10';
      case 'LOW':
        return 'border-green-500 bg-green-500/10';
      default:
        return 'border-racing-silver bg-racing-silver/10';
    }
  };

  if (loading && !coachingData) {
    return (
      <div className="p-8 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-racing-red mx-auto mb-4" />
          <p className="text-racing-silver">Generating AI coaching insights...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="racing-gradient rounded-xl p-8 text-center">
        <h1 className="text-racing text-4xl font-bold mb-4">🧠 AI Coaching Cards</h1>
        <p className="text-xl text-white/90">Personalized Performance Recommendations</p>
        <p className="text-white/70 mt-2">Driver {selectedDriver} • Toyota Gazoo Racing COTA Analysis</p>
      </div>

      {/* Driver Selector */}
      <div className="card-racing">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-racing">Select Driver</h2>
          <select
            value={selectedDriver || ''}
            onChange={(e) => setSelectedDriver(e.target.value)}
            className="bg-racing-gray text-white rounded-lg px-4 py-2 border border-racing-silver/30"
          >
            <option value="">Select Driver</option>
            {drivers.map((driver) => (
              <option key={driver.vehicle_id} value={driver.vehicle_id}>
                {driver.vehicle_id}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Coaching Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {coachingData?.cards?.length ? (
          coachingData.cards.map((card, idx) => (
            <div
              key={card.id || idx}
              className={`card-racing border-l-4 ${getPriorityColor(card.priority)} hover:scale-[1.02] transition-all duration-200`}
            >
              {/* Card Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-racing-red/20 rounded-lg flex items-center justify-center text-racing-red">
                    {getCategoryIcon(card.category)}
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white">{card.title}</h3>
                    <span className="text-sm text-racing-silver">{card.category}</span>
                  </div>
                </div>
                {card.potential_gain && (
                  <div className="text-right">
                    <div className="text-2xl font-bold text-racing-red">+{card.potential_gain}s</div>
                    <div className="text-sm text-racing-silver">Potential Gain</div>
                  </div>
                )}
              </div>

              {/* Summary */}
              <p className="text-racing-silver mb-4">{card.summary || card.content}</p>

              {/* Evidence */}
              {card.evidence && (
                <div className="bg-racing-black/50 rounded-lg p-4 mb-4">
                  <h4 className="text-sm font-semibold text-racing mb-2">Evidence</h4>
                  <div className="space-y-1">
                    {Object.entries(card.evidence).map(([key, value]) => (
                      <div key={key} className="flex justify-between text-sm">
                        <span className="text-racing-silver capitalize">{key.replace('_', ' ')}:</span>
                        <span className="text-white">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              <div className="mb-4">
                <h4 className="text-sm font-semibold text-racing mb-2">Recommendations</h4>
                <ul className="space-y-1">
                  {(card.recommendations || card.action_items || []).map((rec, index) => (
                    <li key={index} className="text-sm text-racing-silver flex items-start">
                      <span className="w-2 h-2 bg-racing-red rounded-full mt-2 mr-2 flex-shrink-0" />
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                  <span className="text-sm text-racing-silver">{card.confidence || 'AI'}% confidence</span>
                </div>
                <button 
                  onClick={() => navigate('/evidence', { state: { driverId: selectedDriver } })}
                  className="btn-secondary text-sm"
                >
                  View Evidence
                  <ChevronRight className="w-4 h-4 ml-1" />
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-12">
            <p className="text-racing-silver">No coaching data available for this driver.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CoachingCards;