import React, { useState, useEffect } from 'react';
import { Save, AlertCircle, CheckCircle, Settings as SettingsIcon } from 'lucide-react';

const Settings = () => {
  const [systemHealth, setSystemHealth] = useState(null);
  const [deliveryStats, setDeliveryStats] = useState(null);

  useEffect(() => {
    fetchSystemHealth();
    fetchDeliveryStats();
  }, []);

  const fetchSystemHealth = async () => {
    try {
      const response = await fetch('/api/metrics/health');
      const data = await response.json();
      setSystemHealth(data);
    } catch (error) {
      console.error('Failed to fetch system health:', error);
    }
  };

  const fetchDeliveryStats = async () => {
    try {
      const response = await fetch('/api/delivery/stats');
      const data = await response.json();
      setDeliveryStats(data);
    } catch (error) {
      console.error('Failed to fetch delivery stats:', error);
    }
  };

  const getServiceStatusIcon = (status) => {
    return status === 'healthy' ? 
      <CheckCircle className="h-5 w-5 text-green-500" /> : 
      <AlertCircle className="h-5 w-5 text-red-500" />;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">System Settings</h1>
      </div>

      {/* System Health */}
      {systemHealth && (
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <SettingsIcon className="h-5 w-5" />
            <span>System Health</span>
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-md font-medium text-gray-900 mb-3">Overview</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Status:</span>
                  <span className={`text-sm font-medium ${systemHealth.status === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
                    {systemHealth.status}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Uptime:</span>
                  <span className="text-sm font-medium text-gray-900">{systemHealth.uptime}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Processed:</span>
                  <span className="text-sm font-medium text-gray-900">{systemHealth.total_processed?.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Last Incident:</span>
                  <span className="text-sm font-medium text-gray-900">
                    {new Date(systemHealth.last_incident).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="text-md font-medium text-gray-900 mb-3">Service Status</h3>
              <div className="space-y-3">
                {Object.entries(systemHealth.services).map(([service, data]) => (
                  <div key={service} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      {getServiceStatusIcon(data.status)}
                      <span className="text-sm font-medium text-gray-900 capitalize">
                        {service.replace('_', ' ')}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500">
                      {Math.round(data.response_time)}ms
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delivery Configuration */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Delivery Configuration</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-md font-medium text-gray-900 mb-3">Rate Limits</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email per minute</label>
                <input 
                  type="number" 
                  defaultValue="10"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">SMS per minute</label>
                <input 
                  type="number" 
                  defaultValue="5"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Push per minute</label>
                <input 
                  type="number" 
                  defaultValue="20"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>
          
          <div>
            <h3 className="text-md font-medium text-gray-900 mb-3">Retry Settings</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Retry Attempts</label>
                <input 
                  type="number" 
                  defaultValue="3"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Base Delay (seconds)</label>
                <input 
                  type="number" 
                  defaultValue="1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Delay (seconds)</label>
                <input 
                  type="number" 
                  defaultValue="300"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>
        </div>
        
        <div className="mt-6">
          <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2">
            <Save className="h-4 w-4" />
            <span>Save Configuration</span>
          </button>
        </div>
      </div>

      {/* Performance Statistics */}
      {deliveryStats && (
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Performance Statistics</h2>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{deliveryStats.successful.toLocaleString()}</div>
              <div className="text-sm text-gray-600">Successful</div>
            </div>
            
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">{deliveryStats.failed_temporary.toLocaleString()}</div>
              <div className="text-sm text-gray-600">Temporary Failures</div>
            </div>
            
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">{deliveryStats.failed_permanent.toLocaleString()}</div>
              <div className="text-sm text-gray-600">Permanent Failures</div>
            </div>
            
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{Math.round(deliveryStats.success_rate)}%</div>
              <div className="text-sm text-gray-600">Success Rate</div>
            </div>
          </div>
        </div>
      )}

      {/* Channel Statistics */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Channel Performance</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
            <div>
              <div className="font-medium text-blue-900">Email</div>
              <div className="text-sm text-blue-600">Primary communication channel</div>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-blue-900">92.5%</div>
              <div className="text-sm text-blue-600">Success Rate</div>
            </div>
          </div>
          
          <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
            <div>
              <div className="font-medium text-green-900">SMS</div>
              <div className="text-sm text-green-600">High reliability channel</div>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-green-900">97.2%</div>
              <div className="text-sm text-green-600">Success Rate</div>
            </div>
          </div>
          
          <div className="flex items-center justify-between p-4 bg-purple-50 rounded-lg">
            <div>
              <div className="font-medium text-purple-900">Push</div>
              <div className="text-sm text-purple-600">Real-time notifications</div>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-purple-900">89.8%</div>
              <div className="text-sm text-purple-600">Success Rate</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
