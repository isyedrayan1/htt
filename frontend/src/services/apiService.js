import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Configure axios timeout
axios.defaults.timeout = 10000;

class ApiService {
  static async healthCheck() {
    try {
      const response = await axios.get(`http://localhost:8000/health`);
      console.log('Health check response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error.message);
      throw error;
    }
  }

  static async getLiveSummary() {
    try {
      const response = await axios.get(`${API_BASE_URL}/realtime/live/summary`);
      console.log('Live summary response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Live summary failed:', error.message);
      throw error;
    }
  }

  static async getDriverTelemetry(vehicleId) {
    const response = await axios.get(`${API_BASE_URL}/realtime/live/telemetry/${vehicleId}`);
    return response.data;
  }

  static async getPitStrategies() {
    const response = await axios.get(`${API_BASE_URL}/realtime/strategy/pit-optimizer`);
    return response.data;
  }

  static async advanceRace() {
    const response = await axios.post(`${API_BASE_URL}/realtime/live/advance`);
    return response.data;
  }

  static async getMLStatus() {
    const response = await axios.get(`${API_BASE_URL}/ml/status`);
    return response.data;
  }

  static async getDPTAD(vehicleId, sessionFilter = null) {
    const params = {};
    if (sessionFilter) params.session_filter = sessionFilter;
    const response = await axios.get(`${API_BASE_URL}/ml/dptad/analyze/${vehicleId}`, { params });
    return response.data;
  }

  static async getSIWTL(vehicleId, includeSectors = true, includeTelemetry = false) {
    const params = { include_sectors: includeSectors, include_telemetry: includeTelemetry };
    const response = await axios.get(`${API_BASE_URL}/ml/siwtl/calculate/${vehicleId}`, { params });
    return response.data;
  }

  static async getComprehensiveML(vehicleId) {
    const response = await axios.get(`${API_BASE_URL}/ml/comprehensive/${vehicleId}`);
    return response.data;
  }

  static async postAIChat(message, context = {}) {
    const response = await axios.post(`${API_BASE_URL}/ai/chat`, { message, context });
    return response.data;
  }

  static async getAIContext(vehicleId) {
    const response = await axios.get(`${API_BASE_URL}/ai/context/${vehicleId}`);
    return response.data;
  }

  static async getDrivers() {
    const response = await axios.get(`${API_BASE_URL}/drivers`);
    return response.data && response.data.drivers ? response.data.drivers : (Array.isArray(response.data) ? response.data : []);
  }

  static async getLaps(vehicleId) {
    const response = await axios.get(`${API_BASE_URL}/laps/${vehicleId}`);
    return response.data;
  }

  static async getTelemetryHistory(vehicleId) {
    // Use /laps endpoint to get lap history and sector times
    const response = await axios.get(`${API_BASE_URL}/laps/${vehicleId}`);
    return response.data;
  }

  static async getDriverCoaching(vehicleId) {
    const response = await axios.get(`${API_BASE_URL}/coaching/${vehicleId}`);
    return response.data;
  }

  static async getLapTelemetry(vehicleId, lapNumber) {
    const response = await axios.get(`${API_BASE_URL}/telemetry/${vehicleId}/${lapNumber}`);
    return response.data;
  }

  static async getComparison(vehicleId1, vehicleId2) {
    const response = await axios.get(`${API_BASE_URL}/compare/${vehicleId1}/${vehicleId2}`);
    return response.data;
  }

  static async getFleetSummary() {
    const response = await axios.get(`${API_BASE_URL}/fleet/summary`);
    return response.data;
  }
}

export { ApiService };