import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import AlertService from '../services/AlertService';

function AlertDetail() {
  const { id } = useParams();
  const [alert, setAlert] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAlertDetails();
  }, [id]);

  const loadAlertDetails = async () => {
    try {
      const [alertData, historyData] = await Promise.all([
        AlertService.getAlert(id),
        AlertService.getAlertHistory(id)
      ]);
      setAlert(alertData);
      setHistory(historyData.history);
    } catch (error) {
      console.error('Error loading alert details:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading alert details...</div>;
  if (!alert) return <div className="error">Alert not found</div>;

  return (
    <div className="alert-detail">
      <div className="page-header">
        <h2>{alert.title}</h2>
        <span className={`state-badge ${alert.state.toLowerCase()}`}>
          {alert.state}
        </span>
      </div>

      <div className="detail-grid">
        <div className="detail-section">
          <h3>Alert Information</h3>
          <div className="detail-item">
            <label>Service:</label>
            <span>{alert.service_name}</span>
          </div>
          <div className="detail-item">
            <label>Metric:</label>
            <span>{alert.metric_name}</span>
          </div>
          <div className="detail-item">
            <label>Current Value:</label>
            <span>{alert.current_value}</span>
          </div>
          <div className="detail-item">
            <label>Threshold:</label>
            <span>{alert.threshold_value}</span>
          </div>
          <div className="detail-item">
            <label>Severity:</label>
            <span className={`severity-badge ${alert.severity.toLowerCase()}`}>
              {alert.severity}
            </span>
          </div>
        </div>

        <div className="detail-section">
          <h3>Timeline</h3>
          <div className="timeline">
            {history.map((event, index) => (
              <div key={index} className="timeline-item">
                <div className="timeline-time">
                  {new Date(event.timestamp).toLocaleString()}
                </div>
                <div className="timeline-content">
                  <strong>{event.event}</strong>
                  {event.user && <span> by {event.user}</span>}
                  <p>{event.details}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AlertDetail;
