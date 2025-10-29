import React, { useState, useEffect } from 'react';
import { Search, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

const Tracking = () => {
  const [trackingId, setTrackingId] = useState('');
  const [trackingData, setTrackingData] = useState(null);
  const [recentTracking, setRecentTracking] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchRecentTracking();
  }, []);

  const fetchRecentTracking = async () => {
    try {
      const response = await fetch('/api/tracking/');
      const data = await response.json();
      setRecentTracking(data.tracking_entries || []);
    } catch (error) {
      console.error('Failed to fetch recent tracking:', error);
    }
  };

  const searchTracking = async () => {
    if (!trackingId.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`/api/tracking/${trackingId}`);
      if (response.ok) {
        const data = await response.json();
        setTrackingData(data);
      } else {
        alert('Tracking ID not found');
        setTrackingData(null);
      }
    } catch (error) {
      alert('Failed to fetch tracking data: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const getEventIcon = (eventType) => {
    switch (eventType) {
      case 'queued':
        return <Clock className="h-5 w-5 text-blue-500" />;
      case 'processing':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      case 'delivered':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'read':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'delivered': return 'text-green-600 bg-green-100';
      case 'read': return 'text-green-700 bg-green-200';
      case 'failed': return 'text-red-600 bg-red-100';
      case 'processing': return 'text-blue-600 bg-blue-100';
      case 'queued': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Notification Tracking</h1>
      </div>

      {/* Search */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Track Notification</h2>
        <div className="flex space-x-4">
          <div className="flex-1">
            <input
              type="text"
              value={trackingId}
              onChange={(e) => setTrackingId(e.target.value)}
              placeholder="Enter tracking ID (e.g., track_0001)"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              onKeyPress={(e) => e.key === 'Enter' && searchTracking()}
            />
          </div>
          <button
            onClick={searchTracking}
            disabled={loading || !trackingId.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
          >
            <Search className="h-4 w-4" />
            <span>{loading ? 'Searching...' : 'Track'}</span>
          </button>
        </div>
      </div>

      {/* Tracking Results */}
      {trackingData && (
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                Tracking: {trackingData.tracking_id}
              </h2>
              <p className="text-sm text-gray-500">
                Notification ID: {trackingData.notification_id}
              </p>
            </div>
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium capitalize ${getStatusColor(trackingData.current_status)}`}>
              {trackingData.current_status}
            </span>
          </div>

          {/* Timeline */}
          <div className="space-y-4">
            <h3 className="text-md font-medium text-gray-900">Delivery Timeline</h3>
            <div className="space-y-4">
              {trackingData.events.map((event, index) => (
                <div key={index} className="flex items-start space-x-4">
                  <div className="flex-shrink-0 mt-1">
                    {getEventIcon(event.event_type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900 capitalize">
                        {event.event_type.replace('_', ' ')}
                      </p>
                      <p className="text-sm text-gray-500">
                        {new Date(event.timestamp).toLocaleString()}
                      </p>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {event.description}
                    </p>
                    {event.metadata && (
                      <div className="mt-2 text-xs text-gray-500 bg-gray-50 p-2 rounded">
                        {Object.entries(event.metadata).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="capitalize">{key.replace('_', ' ')}:</span>
                            <span>{typeof value === 'object' ? JSON.stringify(value) : value}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Recent Tracking Entries */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h2 className="text-lg font-semibold text-gray-900">Recent Tracking Entries</h2>
          <p className="text-sm text-gray-600 mt-1">
            Click on any tracking ID to view detailed timeline
          </p>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tracking ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Channel
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Updated
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentTracking.map((entry) => (
                <tr 
                  key={entry.tracking_id} 
                  className="hover:bg-gray-50 cursor-pointer"
                  onClick={() => {
                    setTrackingId(entry.tracking_id);
                    searchTracking();
                  }}
                >
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-blue-600 hover:text-blue-800">
                      {entry.tracking_id}
                    </div>
                    <div className="text-xs text-gray-500">
                      {entry.notification_id}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
                      {entry.channel}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${getStatusColor(entry.status)}`}>
                      {entry.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(entry.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(entry.last_updated).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {recentTracking.length === 0 && (
            <div className="text-center py-12">
              <div className="text-gray-500">No tracking entries found</div>
              <div className="text-sm text-gray-400 mt-1">
                Send some notifications to see tracking data
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Tracking;
