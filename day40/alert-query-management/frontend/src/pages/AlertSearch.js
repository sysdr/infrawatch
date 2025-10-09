import React, { useState } from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';

const AlertSearch = () => {
  const [searchParams, setSearchParams] = useState({
    query: '',
    status: [],
    severity: [],
    source: [],
    service: [],
    start_time: '',
    end_time: '',
    limit: 100,
    offset: 0
  });

  const { data: filters } = useQuery('filter-options', async () => {
    const response = await axios.get('/api/alerts/filters');
    return response.data;
  });

  const { data: searchResults, isLoading, refetch } = useQuery(
    ['alert-search', searchParams],
    async () => {
      const response = await axios.post('/api/alerts/search', searchParams);
      return response.data;
    },
    { enabled: false }
  );

  const handleSearch = () => {
    refetch();
  };

  const handleExport = async (format) => {
    if (!searchResults?.alerts?.length) return;
    
    const alertIds = searchResults.alerts.map(alert => alert.id);
    
    try {
      const response = await axios.post('/api/alerts/export', alertIds, {
        params: { format },
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `alerts.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Alert Search</h1>
        <p className="page-subtitle">Advanced alert filtering and querying</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Search Filters</h2>
        </div>
        <div className="card-body">
          <div className="form-row">
            <div className="form-col">
              <label className="form-label">Search Query</label>
              <input
                type="text"
                className="form-control"
                placeholder="Search in title, description, source..."
                value={searchParams.query}
                onChange={(e) => setSearchParams({...searchParams, query: e.target.value})}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-col">
              <label className="form-label">Status</label>
              <select
                multiple
                className="form-control"
                value={searchParams.status}
                onChange={(e) => {
                  const values = Array.from(e.target.selectedOptions, option => option.value);
                  setSearchParams({...searchParams, status: values});
                }}
              >
                {filters?.statuses?.map(status => (
                  <option key={status} value={status}>{status}</option>
                ))}
              </select>
            </div>

            <div className="form-col">
              <label className="form-label">Severity</label>
              <select
                multiple
                className="form-control"
                value={searchParams.severity}
                onChange={(e) => {
                  const values = Array.from(e.target.selectedOptions, option => option.value);
                  setSearchParams({...searchParams, severity: values});
                }}
              >
                {filters?.severities?.map(severity => (
                  <option key={severity} value={severity}>{severity}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-col">
              <label className="form-label">Start Time</label>
              <input
                type="datetime-local"
                className="form-control"
                value={searchParams.start_time}
                onChange={(e) => setSearchParams({...searchParams, start_time: e.target.value})}
              />
            </div>

            <div className="form-col">
              <label className="form-label">End Time</label>
              <input
                type="datetime-local"
                className="form-control"
                value={searchParams.end_time}
                onChange={(e) => setSearchParams({...searchParams, end_time: e.target.value})}
              />
            </div>
          </div>

          <div style={{display: 'flex', gap: '10px', marginTop: '20px'}}>
            <button className="btn btn-primary" onClick={handleSearch}>
              Search Alerts
            </button>
            <button 
              className="btn btn-secondary"
              onClick={() => setSearchParams({
                query: '', status: [], severity: [], source: [], service: [],
                start_time: '', end_time: '', limit: 100, offset: 0
              })}
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {searchResults && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">
              Search Results ({searchResults.total_count} found)
            </h2>
            <div style={{marginLeft: 'auto', display: 'flex', gap: '10px'}}>
              <button 
                className="btn btn-secondary btn-sm"
                onClick={() => handleExport('csv')}
                disabled={!searchResults.alerts?.length}
              >
                Export CSV
              </button>
              <button 
                className="btn btn-secondary btn-sm"
                onClick={() => handleExport('json')}
                disabled={!searchResults.alerts?.length}
              >
                Export JSON
              </button>
            </div>
          </div>
          <div className="card-body">
            {isLoading ? (
              <div className="loading">Searching...</div>
            ) : searchResults.alerts?.length > 0 ? (
              <table className="table">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Status</th>
                    <th>Severity</th>
                    <th>Source</th>
                    <th>Service</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {searchResults.alerts.map(alert => (
                    <tr key={alert.id}>
                      <td>{alert.title}</td>
                      <td>
                        <span className={`status-badge status-${alert.status}`}>
                          {alert.status}
                        </span>
                      </td>
                      <td>
                        <span className={`status-badge severity-${alert.severity}`}>
                          {alert.severity}
                        </span>
                      </td>
                      <td>{alert.source}</td>
                      <td>{alert.service}</td>
                      <td>{new Date(alert.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="empty-state">No alerts found matching your criteria</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertSearch;
