import React, { useState } from 'react';
import { echoMessage, getStatus } from '../services/api';

const ApiTester = () => {
  const [echoInput, setEchoInput] = useState('{"test": "data"}');
  const [echoResponse, setEchoResponse] = useState(null);
  const [statusResponse, setStatusResponse] = useState(null);
  const [loading, setLoading] = useState({ echo: false, status: false });
  const [error, setError] = useState(null);

  const handleEcho = async () => {
    setLoading({ ...loading, echo: true });
    setError(null);
    
    try {
      const data = JSON.parse(echoInput);
      const response = await echoMessage(data);
      setEchoResponse(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading({ ...loading, echo: false });
    }
  };

  const handleStatus = async () => {
    setLoading({ ...loading, status: true });
    setError(null);
    
    try {
      const response = await getStatus();
      setStatusResponse(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading({ ...loading, status: false });
    }
  };

  return (
    <div className="api-tester">
      <h2>API Integration Tester</h2>

      <div className="test-section">
        <h3>Echo Test (POST)</h3>
        <textarea
          value={echoInput}
          onChange={(e) => setEchoInput(e.target.value)}
          rows={4}
          cols={50}
          placeholder="Enter JSON data to echo"
        />
        <br />
        <button 
          onClick={handleEcho} 
          disabled={loading.echo}
          className="test-button"
        >
          {loading.echo ? 'Sending...' : 'Send Echo Request'}
        </button>
        
        {echoResponse && (
          <div className="response-card">
            <h4>Echo Response:</h4>
            <pre>{JSON.stringify(echoResponse, null, 2)}</pre>
          </div>
        )}
      </div>

      <div className="test-section">
        <h3>Status Test (GET)</h3>
        <button 
          onClick={handleStatus} 
          disabled={loading.status}
          className="test-button"
        >
          {loading.status ? 'Loading...' : 'Get Server Status'}
        </button>
        
        {statusResponse && (
          <div className="response-card">
            <h4>Status Response:</h4>
            <pre>{JSON.stringify(statusResponse, null, 2)}</pre>
          </div>
        )}
      </div>

      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}
    </div>
  );
};

export default ApiTester;
