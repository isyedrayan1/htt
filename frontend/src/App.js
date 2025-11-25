import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Layout/Navbar';
import Dashboard from './components/Dashboard/Dashboard';
import CoachingCards from './components/Coaching/CoachingCards';
import EvidenceExplorer from './components/Evidence/EvidenceExplorer';
import DriverAnalysis from './components/DriverAnalysis/DriverAnalysis';
import Compare from './components/Compare/Compare';
import LiveRace from './components/LiveRace/LiveRace';
import Strategy from './components/Strategy/Strategy';
import AIChat from './components/AI/AIChat';
import { ApiService } from './services/apiService';

function App() {
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  const [raceData, setRaceData] = useState(null);

  useEffect(() => {
    // Check backend connection on app start
    const checkBackend = async () => {
      console.log('Attempting to connect to backend...');
      try {
        const response = await ApiService.healthCheck();
        console.log('Backend health check success:', response);
        setIsBackendConnected(true);
        
        // Immediately fetch initial race data
        try {
          const data = await ApiService.getLiveSummary();
          console.log('Initial race data loaded:', data);
          setRaceData(data);
        } catch (dataError) {
          console.error('Failed to fetch initial race data:', dataError);
        }
      } catch (error) {
        console.error('Backend connection failed:', error);
        setIsBackendConnected(false);
        // Retry connection every 3 seconds
        setTimeout(checkBackend, 3000);
      }
    };

    checkBackend();
    
    // Set up periodic data refresh
    const interval = setInterval(async () => {
      if (isBackendConnected) {
        try {
          const data = await ApiService.getLiveSummary();
          setRaceData(data);
        } catch (error) {
          console.error('Failed to fetch race data:', error);
          // If we lose connection, reset and try to reconnect
          setIsBackendConnected(false);
          checkBackend();
        }
      }
    }, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!isBackendConnected) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-racing-black">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-racing-red mx-auto mb-8"></div>
          <h1 className="text-racing text-2xl font-bold text-racing-red mb-4">
            🏁 Racing Analytics Platform
          </h1>
          <p className="text-racing-silver mb-4">Connecting to race control...</p>
          <p className="text-sm text-racing-silver/70">
            Make sure the backend API is running on localhost:8000
          </p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-racing-black text-white">
        <Navbar />
        <main className="pt-16">
          <Routes>
            <Route path="/" element={<Dashboard raceData={raceData} />} />
            <Route path="/coaching" element={<CoachingCards />} />
            <Route path="/evidence" element={<EvidenceExplorer />} />
            <Route path="/compare" element={<Compare />} />
            <Route path="/live" element={<LiveRace raceData={raceData} />} />
            <Route path="/drivers/:driverId?" element={<DriverAnalysis />} />
            <Route path="/strategy" element={<Strategy />} />
          </Routes>
        </main>
        <AIChat />
      </div>
    </Router>
  );
}

export default App;