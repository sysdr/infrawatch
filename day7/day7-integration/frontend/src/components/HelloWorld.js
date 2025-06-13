import React, { useState } from 'react';
import { getHelloWorld } from '../services/api';

const HelloWorld = () => {
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleClick = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await getHelloWorld();
      setResponse(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="hello-world">
      <h2>Hello World Integration Test</h2>
      
      <button 
        onClick={handleClick} 
        disabled={loading}
        className="hello-button"
      >
        {loading ? 'Loading...' : 'Say Hello to Backend'}
      </button>

      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}

      {response && (
        <div className="response-card">
          <h3>Backend Response:</h3>
          <div className="response-content">
            <p><strong>Message:</strong> {response.message}</p>
            <p><strong>Count:</strong> {response.count}</p>
            <p><strong>Timestamp:</strong> {new Date(response.timestamp).toLocaleString()}</p>
            
            <div className="server-info">
              <h4>Server Info:</h4>
              <p>Uptime: {Math.floor(response.server_info.uptime_seconds / 60)} minutes</p>
              <p>Total Requests: {response.server_info.total_requests}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HelloWorld;
