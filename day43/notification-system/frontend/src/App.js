import React, { useState, useEffect } from 'react';
import axios from 'axios';
import NotificationForm from './components/NotificationForm';
import NotificationList from './components/NotificationList';
import Dashboard from './components/Dashboard';
import ChannelTester from './components/ChannelTester';
import { Bell, Settings, Activity, TestTube } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [notifications, setNotifications] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchNotifications();
    fetchStats();
    
    // Refresh data every 5 seconds
    const interval = setInterval(() => {
      fetchNotifications();
      fetchStats();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const fetchNotifications = async () => {
    try {
      const response = await axios.get(`${API_BASE}/notifications`);
      setNotifications(response.data);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const sendNotification = async (notificationData) => {
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/notifications`, notificationData);
      await fetchNotifications();
      await fetchStats();
      return { success: true };
    } catch (error) {
      console.error('Failed to send notification:', error);
      return { success: false, error: error.response?.data?.detail || 'Failed to send' };
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'dashboard', name: 'Dashboard', icon: Activity },
    { id: 'send', name: 'Send Notification', icon: Bell },
    { id: 'history', name: 'History', icon: Settings },
    { id: 'test', name: 'Test Channels', icon: TestTube }
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white shadow-lg border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-2 rounded-lg mr-4">
                <Bell className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-slate-900">
                  Notification System
                </h1>
                <p className="text-sm text-slate-600 font-medium">
                  Enterprise Multi-Channel Communication Platform
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-6">
              <div className="text-sm text-slate-600 bg-slate-100 px-4 py-2 rounded-lg">
                {stats && (
                  <span className="font-semibold">
                    {stats.total_notifications} total • {stats.total_delivered} delivered
                  </span>
                )}
              </div>
              <div className="flex items-center space-x-2">
                <div className="h-3 w-3 bg-emerald-500 rounded-full animate-pulse" title="System Online"></div>
                <span className="text-sm font-medium text-slate-700">Online</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center px-4 py-4 text-sm font-semibold border-b-2 transition-all duration-200 ${
                    activeTab === tab.id
                      ? 'border-indigo-600 text-indigo-700 bg-indigo-50'
                      : 'border-transparent text-slate-600 hover:text-slate-800 hover:border-slate-300 hover:bg-slate-50'
                  }`}
                >
                  <Icon className="h-5 w-5 mr-2" />
                  {tab.name}
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && (
          <Dashboard 
            stats={stats} 
            notifications={notifications.slice(0, 10)} 
            onRefresh={() => {
              fetchNotifications();
              fetchStats();
            }}
          />
        )}
        
        {activeTab === 'send' && (
          <NotificationForm 
            onSend={sendNotification} 
            loading={loading} 
          />
        )}
        
        {activeTab === 'history' && (
          <NotificationList 
            notifications={notifications} 
            onRefresh={fetchNotifications}
          />
        )}
        
        {activeTab === 'test' && (
          <ChannelTester />
        )}
      </main>
    </div>
  );
}

export default App;
