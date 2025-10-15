import React from 'react';
import { format } from 'date-fns';
import '../../styles/AlertList.css';

function AlertList({ alerts, title }) {
    const getStateColor = (state) => {
        const colors = {
            firing: '#e74c3c',
            pending: '#f39c12',
            resolved: '#27ae60',
            ok: '#95a5a6'
        };
        return colors[state] || '#95a5a6';
    };

    const getSeverityBadge = (severity) => {
        const badges = {
            critical: { color: '#e74c3c', label: 'CRITICAL' },
            warning: { color: '#f39c12', label: 'WARNING' },
            info: { color: '#3498db', label: 'INFO' }
        };
        return badges[severity] || badges.info;
    };

    const sortedAlerts = [...alerts].sort((a, b) => {
        const stateOrder = { firing: 0, pending: 1, resolved: 2, ok: 3 };
        return stateOrder[a.state] - stateOrder[b.state];
    });

    return (
        <div className="alert-list">
            <h2>{title}</h2>
            {sortedAlerts.length === 0 ? (
                <div className="no-alerts">No alerts to display</div>
            ) : (
                <div className="alerts-container">
                    {sortedAlerts.map(alert => {
                        const severity = getSeverityBadge(alert.severity);
                        return (
                            <div key={alert.id} className="alert-card">
                                <div className="alert-header">
                                    <span 
                                        className="state-badge"
                                        style={{ backgroundColor: getStateColor(alert.state) }}
                                    >
                                        {alert.state.toUpperCase()}
                                    </span>
                                    <span 
                                        className="severity-badge"
                                        style={{ backgroundColor: severity.color }}
                                    >
                                        {severity.label}
                                    </span>
                                </div>
                                
                                <h3 className="alert-title">{alert.rule_name}</h3>
                                <p className="alert-message">{alert.message}</p>
                                
                                <div className="alert-details">
                                    <div className="detail-row">
                                        <span className="detail-label">Current Value:</span>
                                        <span className="detail-value">{alert.current_value.toFixed(2)}</span>
                                    </div>
                                    <div className="detail-row">
                                        <span className="detail-label">Threshold:</span>
                                        <span className="detail-value">{alert.threshold.toFixed(2)}</span>
                                    </div>
                                    <div className="detail-row">
                                        <span className="detail-label">Started:</span>
                                        <span className="detail-value">
                                            {format(new Date(alert.started_at), 'MMM dd, HH:mm:ss')}
                                        </span>
                                    </div>
                                    {alert.resolved_at && (
                                        <div className="detail-row">
                                            <span className="detail-label">Resolved:</span>
                                            <span className="detail-value">
                                                {format(new Date(alert.resolved_at), 'MMM dd, HH:mm:ss')}
                                            </span>
                                        </div>
                                    )}
                                </div>

                                {Object.keys(alert.labels).length > 0 && (
                                    <div className="alert-labels">
                                        {Object.entries(alert.labels).map(([key, value]) => (
                                            <span key={key} className="label-tag">
                                                {key}: {value}
                                            </span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}

export default AlertList;
