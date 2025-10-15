import React from 'react';
import '../../styles/AlertStats.css';

function AlertStats({ firing, pending, resolved, totalRules }) {
    const stats = [
        { label: 'Firing', value: firing, color: '#e74c3c', icon: '🔥' },
        { label: 'Pending', value: pending, color: '#f39c12', icon: '⏳' },
        { label: 'Resolved', value: resolved, color: '#27ae60', icon: '✅' },
        { label: 'Total Rules', value: totalRules, color: '#3498db', icon: '📋' },
    ];

    return (
        <div className="alert-stats">
            {stats.map((stat, index) => (
                <div key={index} className="stat-card" style={{ borderLeftColor: stat.color }}>
                    <div className="stat-icon">{stat.icon}</div>
                    <div className="stat-content">
                        <div className="stat-value">{stat.value}</div>
                        <div className="stat-label">{stat.label}</div>
                    </div>
                </div>
            ))}
        </div>
    );
}

export default AlertStats;
