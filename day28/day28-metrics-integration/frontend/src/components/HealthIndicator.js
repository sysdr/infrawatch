import React from 'react';
import { CheckCircle, AlertTriangle, XCircle, Loader } from 'lucide-react';

const HealthIndicator = ({ health }) => {
  if (!health) {
    return (
      <div className="health-indicator loading">
        <Loader className="icon spin" size={16} />
        <span>Checking...</span>
      </div>
    );
  }

  const getStatusIcon = () => {
    switch (health.status) {
      case 'healthy':
        return <CheckCircle className="icon healthy" size={16} />;
      case 'degraded':
        return <AlertTriangle className="icon degraded" size={16} />;
      default:
        return <XCircle className="icon unhealthy" size={16} />;
    }
  };

  const getStatusText = () => {
    if (health.status === 'healthy') return 'All Systems Operational';
    if (health.status === 'degraded') return 'Some Issues Detected';
    return 'System Unavailable';
  };

  return (
    <div className={`health-indicator ${health.status}`}>
      {getStatusIcon()}
      <div className="health-details">
        <div className="health-status">{getStatusText()}</div>
        <div className="health-components">
          <span className={health.database ? 'healthy' : 'unhealthy'}>
            DB: {health.database ? 'OK' : 'Down'}
          </span>
          <span className={health.redis ? 'healthy' : 'unhealthy'}>
            Cache: {health.redis ? 'OK' : 'Down'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default HealthIndicator;
