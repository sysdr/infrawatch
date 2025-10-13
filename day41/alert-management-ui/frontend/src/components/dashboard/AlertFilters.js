import React from 'react';

const AlertFilters = ({ filters, onChange }) => {
  const handleFilterChange = (field, value) => {
    onChange({ ...filters, [field]: value });
  };

  return (
    <div className="filters">
      <div className="filter-group">
        <label>Severity</label>
        <select 
          value={filters.severity} 
          onChange={(e) => handleFilterChange('severity', e.target.value)}
        >
          <option value="">All</option>
          <option value="critical">Critical</option>
          <option value="warning">Warning</option>
          <option value="info">Info</option>
        </select>
      </div>
      <div className="filter-group">
        <label>Status</label>
        <select 
          value={filters.status} 
          onChange={(e) => handleFilterChange('status', e.target.value)}
        >
          <option value="">All</option>
          <option value="active">Active</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="resolved">Resolved</option>
        </select>
      </div>
      <div className="filter-group">
        <label>Search</label>
        <input 
          type="text"
          placeholder="Search alerts..."
          value={filters.search}
          onChange={(e) => handleFilterChange('search', e.target.value)}
        />
      </div>
    </div>
  );
};

export default AlertFilters;
