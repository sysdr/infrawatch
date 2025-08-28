import React, { useState, useEffect } from 'react';
import { Database, Clock, Play, CheckCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

const Rollups = ({ isConnected }) => {
  const [rollupStatus, setRollupStatus] = useState({});
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);

  useEffect(() => {
    if (isConnected) {
      fetchRollupStatus();
      const interval = setInterval(fetchRollupStatus, 30000);
      return () => clearInterval(interval);
    }
  }, [isConnected]);

  const fetchRollupStatus = async () => {
    try {
      const response = await axios.get('/rollups/status');
      setRollupStatus(response.data.data || {});
      setLoading(false);
    } catch (error) {
      console.error('Error fetching rollup status:', error);
      setLoading(false);
    }
  };

  const triggerRollup = async () => {
    setTriggering(true);
    try {
      await axios.post('/rollups/trigger');
      setTimeout(fetchRollupStatus, 2000); // Refresh after 2 seconds
    } catch (error) {
      console.error('Error triggering rollup:', error);
    }
    setTriggering(false);
  };

  const ResolutionCard = ({ resolution, description, retention }) => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{resolution}</h3>
        <Database className="h-5 w-5 text-blue-600" />
      </div>
      <p className="text-sm text-gray-600 mb-2">{description}</p>
      <p className="text-xs text-gray-500">Retention: {retention}</p>
      <div className="mt-4 flex items-center">
        <CheckCircle className="h-4 w-4 text-green-600 mr-2" />
        <span className="text-sm text-green-600">Active</span>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Loading rollup status...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Data Rollups</h1>
          <p className="text-gray-600 mt-1">Automated data aggregation and retention management</p>
        </div>
        <button
          onClick={triggerRollup}
          disabled={triggering}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 flex items-center"
        >
          <Play className="h-4 w-4 mr-2" />
          {triggering ? 'Triggering...' : 'Trigger Rollup'}
        </button>
      </div>

      {/* Status Overview */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Rollup Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center">
            <Clock className="h-5 w-5 text-gray-400 mr-3" />
            <div>
              <p className="text-sm text-gray-600">Last Rollup</p>
              <p className="font-medium text-gray-900">
                {rollupStatus.last_rollup?.timestamp 
                  ? new Date(rollupStatus.last_rollup.timestamp).toLocaleString()
                  : 'Never'
                }
              </p>
            </div>
          </div>
          
          <div className="flex items-center">
            {rollupStatus.last_rollup?.status === 'success' ? (
              <CheckCircle className="h-5 w-5 text-green-600 mr-3" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-600 mr-3" />
            )}
            <div>
              <p className="text-sm text-gray-600">Status</p>
              <p className={`font-medium ${
                rollupStatus.last_rollup?.status === 'success' 
                  ? 'text-green-600' 
                  : 'text-red-600'
              }`}>
                {rollupStatus.last_rollup?.status || 'Unknown'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center">
            <Database className="h-5 w-5 text-blue-600 mr-3" />
            <div>
              <p className="text-sm text-gray-600">Next Rollup</p>
              <p className="font-medium text-gray-900">
                {rollupStatus.next_rollup 
                  ? new Date(rollupStatus.next_rollup).toLocaleString()
                  : 'Scheduled'
                }
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Resolution Configurations */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Rollup Configurations</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <ResolutionCard
            resolution="1 Minute"
            description="High-resolution data for real-time monitoring"
            retention="6 hours"
          />
          <ResolutionCard
            resolution="5 Minutes"
            description="Short-term operational metrics"
            retention="1 day"
          />
          <ResolutionCard
            resolution="1 Hour"
            description="Medium-term trend analysis"
            retention="7 days"
          />
          <ResolutionCard
            resolution="1 Day"
            description="Long-term historical data"
            retention="1 year"
          />
        </div>
      </div>

      {/* Rollup Process Details */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Rollup Process</h2>
        <div className="space-y-4">
          <div className="flex items-start">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-4">
              <span className="text-sm font-medium text-blue-600">1</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Data Collection</h4>
              <p className="text-sm text-gray-600">Raw metrics are collected and stored at 1-second resolution</p>
            </div>
          </div>
          
          <div className="flex items-start">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-4">
              <span className="text-sm font-medium text-blue-600">2</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Aggregation</h4>
              <p className="text-sm text-gray-600">Data is aggregated into larger time windows with statistical calculations</p>
            </div>
          </div>
          
          <div className="flex items-start">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-4">
              <span className="text-sm font-medium text-blue-600">3</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Storage Optimization</h4>
              <p className="text-sm text-gray-600">Older high-resolution data is replaced with aggregated summaries</p>
            </div>
          </div>
          
          <div className="flex items-start">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-4">
              <span className="text-sm font-medium text-blue-600">4</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Cleanup</h4>
              <p className="text-sm text-gray-600">Data beyond retention periods is automatically removed</p>
            </div>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {rollupStatus.last_rollup?.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
            <h3 className="text-sm font-medium text-red-800">Last Rollup Error</h3>
          </div>
          <p className="text-sm text-red-700 mt-2">{rollupStatus.last_rollup.error}</p>
        </div>
      )}
    </div>
  );
};

export default Rollups;
