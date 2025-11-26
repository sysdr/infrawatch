import React from 'react';

const CircuitBreakerStatus = ({ circuitBreakers }) => {
  const getStateColor = (state) => {
    switch (state) {
      case 'CLOSED': return '#10b981';
      case 'HALF_OPEN': return '#f59e0b';
      case 'OPEN': return '#ef4444';
      default: return '#6b7280';
    }
  };

  return (
    <div className="metrics-card">
      <h3>🔧 Circuit Breakers</h3>
      
      {Object.entries(circuitBreakers).map(([name, state]) => (
        <div key={name} className="circuit-breaker-item">
          <span className="cb-name">{name}</span>
          <span 
            className="cb-state" 
            style={{ 
              backgroundColor: getStateColor(state),
              color: 'white',
              padding: '4px 12px',
              borderRadius: '4px',
              fontSize: '0.85em'
            }}
          >
            {state}
          </span>
        </div>
      ))}

      {Object.keys(circuitBreakers).length === 0 && (
        <p>No circuit breakers registered</p>
      )}
    </div>
  );
};

export default CircuitBreakerStatus;
