import React from 'react';
import { Brain, Target, AlertTriangle, TrendingUp } from 'lucide-react';

const CoachingInsights = ({ coachingData, driverId }) => {
  if (!coachingData) {
    return (
      <div className="card-racing">
        <h3 className="text-xl font-bold text-racing mb-4">AI Coaching Insights</h3>
        <div className="text-center py-8 text-racing-silver">
          <Brain className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No coaching data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* AI Coaching Summary */}
      <div className="card-racing">
        <h3 className="text-xl font-bold text-racing mb-6 flex items-center space-x-2">
          <Brain className="w-5 h-5 text-racing-red" />
          <span>AI Coaching Report</span>
        </h3>
        
        {coachingData.coaching_summary && (
          <div className="space-y-4">
            <div className="bg-racing-red/10 border border-racing-red/30 rounded-lg p-4">
              <h4 className="font-bold text-racing-red mb-2">Key Insight</h4>
              <p className="text-white text-sm">
                {coachingData.coaching_summary.primary_recommendation || 'Focus on consistency and sector optimization'}
              </p>
            </div>
            
            {coachingData.coaching_summary.improvement_areas && coachingData.coaching_summary.improvement_areas.length > 0 && (
              <div>
                <h4 className="font-bold text-racing mb-3">Improvement Areas</h4>
                <div className="space-y-2">
                  {coachingData.coaching_summary.improvement_areas.slice(0, 3).map((area, index) => (
                    <div key={index} className="flex items-center space-x-3 bg-racing-black/30 rounded-lg p-3">
                      <AlertTriangle className="w-4 h-4 text-racing-yellow" />
                      <span className="text-white text-sm">{area}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Performance Targets */}
      <div className="card-racing">
        <h3 className="text-xl font-bold text-racing mb-6 flex items-center space-x-2">
          <Target className="w-5 h-5 text-racing-red" />
          <span>Performance Targets</span>
        </h3>
        
        {coachingData.siwtl && (
          <div className="space-y-4">
            {coachingData.siwtl.target_lap_time && (
              <div className="bg-racing-black/30 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-racing-silver">Target Lap Time</span>
                  <span className="text-racing-green font-bold">
                    {coachingData.siwtl.target_lap_time.toFixed(2)}s
                  </span>
                </div>
                <div className="w-full bg-racing-black rounded-full h-2">
                  <div className="bg-racing-green h-2 rounded-full" style={{width: '85%'}}></div>
                </div>
                <p className="text-xs text-racing-silver mt-1">Current progress towards optimal</p>
              </div>
            )}
            
            {coachingData.siwtl.theoretical_best && (
              <div className="bg-racing-black/30 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-racing-silver">Theoretical Best</span>
                  <span className="text-racing-yellow font-bold">
                    {coachingData.siwtl.theoretical_best.toFixed(2)}s
                  </span>
                </div>
                <p className="text-xs text-racing-silver">Based on best sector combinations</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Sector Analysis */}
      {coachingData.sector_analysis && Object.keys(coachingData.sector_analysis).length > 0 && (
        <div className="card-racing">
          <h3 className="text-xl font-bold text-racing mb-6">Sector Analysis</h3>
          
          <div className="space-y-3">
            {[1, 2, 3].map(sector => {
              const sectorData = coachingData.sector_analysis[`sector_${sector}`];
              const improvement = sectorData?.improvement_potential || 0;
              
              return (
                <div key={sector} className="bg-racing-black/30 rounded-lg p-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-white font-medium">Sector {sector}</span>
                    <span className={`text-sm font-bold ${
                      improvement > 0.5 ? 'text-racing-red' :
                      improvement > 0.2 ? 'text-racing-yellow' :
                      'text-racing-green'
                    }`}>
                      {improvement > 0 ? `+${improvement.toFixed(2)}s` : 'Optimal'}
                    </span>
                  </div>
                  
                  {sectorData?.recommendation && (
                    <p className="text-xs text-racing-silver">
                      {sectorData.recommendation}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Action Items */}
      <div className="card-racing">
        <h3 className="text-xl font-bold text-racing mb-6 flex items-center space-x-2">
          <TrendingUp className="w-5 h-5 text-racing-red" />
          <span>Action Items</span>
        </h3>
        
        <div className="space-y-3">
          {coachingData.action_items && coachingData.action_items.length > 0 ? (
            coachingData.action_items.slice(0, 4).map((item, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-racing-black/30 rounded-lg">
                <div className="w-6 h-6 bg-racing-red text-white rounded-full flex items-center justify-center text-xs font-bold mt-0.5">
                  {index + 1}
                </div>
                <p className="text-white text-sm flex-1">{item}</p>
              </div>
            ))
          ) : (
            <div className="text-center py-4 text-racing-silver">
              <Brain className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">AI is analyzing performance data...</p>
              <p className="text-xs mt-1">Personalized recommendations will appear here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CoachingInsights;