import React, { useState, useEffect } from 'react';
import { alertAPI } from '../../services/api';
import websocketService from '../../services/websocket';
import AlertList from '../alerts/AlertList';
import AlertStats from '../alerts/AlertStats';
import MetricSimulator from '../alerts/MetricSimulator';
import '../../styles/Dashboard.css';

function AlertDashboard() {
    const [alerts, setAlerts] = useState([]);
    const [rules, setRules] = useState([]);
    const [loading, setLoading] = useState(true);
    const [connected, setConnected] = useState(false);

    useEffect(() => {
        loadInitialData();
        connectWebSocket();

        return () => {
            websocketService.disconnect();
        };
    }, []);

    const loadInitialData = async () => {
        try {
            const [alertsRes, rulesRes] = await Promise.all([
                alertAPI.getAllAlerts(),
                alertAPI.getRules()
            ]);
            setAlerts(alertsRes.data.alerts || []);
            setRules(rulesRes.data.rules || []);
        } catch (error) {
            console.error('Error loading data:', error);
        } finally {
            setLoading(false);
        }
    };

    const connectWebSocket = () => {
        websocketService.connect();
        websocketService.subscribe(handleWebSocketMessage);
        setConnected(true);
    };

    const handleWebSocketMessage = (data) => {
        if (data.type === 'alert_update') {
            updateAlert(data.alert);
        } else if (data.type === 'initial_state') {
            setAlerts(data.alerts || []);
        }
    };

    const updateAlert = (updatedAlert) => {
        setAlerts(prevAlerts => {
            const index = prevAlerts.findIndex(a => a.id === updatedAlert.id);
            if (index >= 0) {
                const newAlerts = [...prevAlerts];
                newAlerts[index] = updatedAlert;
                return newAlerts;
            } else {
                return [...prevAlerts, updatedAlert];
            }
        });
    };

    const firingAlerts = alerts.filter(a => a.state === 'firing');
    const pendingAlerts = alerts.filter(a => a.state === 'pending');
    const resolvedAlerts = alerts.filter(a => a.state === 'resolved');

    if (loading) {
        return <div className="loading">Loading dashboard...</div>;
    }

    return (
        <div className="dashboard">
            <header className="dashboard-header">
                <h1>Alert System Integration</h1>
                <div className="connection-status">
                    <span className={`status-dot ${connected ? 'connected' : 'disconnected'}`}></span>
                    <span>{connected ? 'Connected' : 'Disconnected'}</span>
                </div>
            </header>

            <AlertStats 
                firing={firingAlerts.length}
                pending={pendingAlerts.length}
                resolved={resolvedAlerts.length}
                totalRules={rules.length}
            />

            <div className="dashboard-content">
                <div className="dashboard-section">
                    <MetricSimulator />
                </div>

                <div className="dashboard-section">
                    <AlertList 
                        alerts={alerts}
                        title="All Alerts"
                    />
                </div>
            </div>
        </div>
    );
}

export default AlertDashboard;
