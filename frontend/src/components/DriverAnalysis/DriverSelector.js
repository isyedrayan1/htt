import React from 'react';
import { ChevronDown } from 'lucide-react';

const DriverSelector = ({ drivers, selectedDriver, onDriverChange }) => {
  return (
    <div className="relative">
      <select
        value={selectedDriver || ''}
        onChange={(e) => onDriverChange(e.target.value)}
        className="appearance-none bg-racing-gray border border-racing-silver/30 rounded-lg px-4 py-2 pr-10 text-white focus:outline-none focus:ring-2 focus:ring-racing-red focus:border-transparent"
      >
        <option value="">Select Driver</option>
        {(drivers || []).map((driver) => (
          <option key={driver.vehicle_id} value={driver.vehicle_id}>
            {driver.vehicle_id}
          </option>
        ))}
      </select>
      <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-racing-silver pointer-events-none" />
    </div>
  );
};

export default DriverSelector;