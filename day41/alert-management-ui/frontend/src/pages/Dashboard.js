import React, { useState, useEffect } from 'react';
import AlertList from '../components/dashboard/AlertList';
import AlertStats from '../components/dashboard/AlertStats';
import AlertFilters from '../components/dashboard/AlertFilters';
import BulkActions from '../components/dashboard/BulkActions';
import { useWebSocket } from '../hooks/useWebSocket';
import { alertService } from '../services/api';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({});
  const [selectedAlerts, setSelectedAlerts] = useState(new Set());
  const [filters, setFilters] = useState({
    severity: '',
    status: '',
    search: ''
  });
  const [loading, setLoading] = useState(true);

  // WebSocket connection
  const { messages } = useWebSocket('ws://localhost:8000/ws');

  useEffect(() => {
    loadAlerts();
    loadStats();
  }, [filters]);

  useEffect(() => {
    if (messages.length > 0) {
      const latestMessage = messages[messages.length - 1];
      if (latestMessage.type === 'new_alert') {
        setAlerts(prev => [latestMessage.alert, ...prev]);
        toast.success('New alert received!');
      }
    }
  }, [messages]);

  const loadAlerts = async () => {
    try {
      const response = await alertService.getAlerts(filters);
      setAlerts(response.alerts);
    } catch (error) {
      toast.error('Failed to load alerts');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await alertService.getStats();
      setStats(response);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleBulkAction = async (action) => {
    const alertIds = Array.from(selectedAlerts);
    try {
      await alertService.bulkAction(action, alertIds);
      toast.success(`Successfully ${action}d ${alertIds.length} alerts`);
      setSelectedAlerts(new Set());
      loadAlerts();
      loadStats();
    } catch (error) {
      toast.error(`Failed to ${action} alerts`);
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Alert Dashboard</h1>
        <div className="dashboard-actions">
          <BulkActions
            selectedCount={selectedAlerts.size}
            onAction={handleBulkAction}
          />
        </div>
      </div>

      <AlertStats stats={stats} />
      
      <AlertFilters filters={filters} onChange={setFilters} />

      <AlertList
        alerts={alerts}
        loading={loading}
        selectedAlerts={selectedAlerts}
        onSelectionChange={setSelectedAlerts}
      />
    </div>
  );
};

export default Dashboard;
