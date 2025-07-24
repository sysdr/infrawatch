import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeftIcon, ServerIcon, CpuChipIcon, CircleStackIcon, WifiIcon } from '@heroicons/react/24/outline';

const ServerDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [server, setServer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchServer = async () => {
      try {
        setLoading(true);
        const response = await fetch(`http://localhost:8000/api/servers/${id}`);
        if (!response.ok) {
          throw new Error('Server not found');
        }
        const data = await response.json();
        setServer(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchServer();
  }, [id]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'text-green-600 bg-green-100';
      case 'provisioning':
        return 'text-yellow-600 bg-yellow-100';
      case 'draining':
        return 'text-orange-600 bg-orange-100';
      case 'terminated':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getHealthColor = (health) => {
    switch (health) {
      case 'healthy':
        return 'text-green-600 bg-green-100';
      case 'degraded':
        return 'text-yellow-600 bg-yellow-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Server Not Found</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!server) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/')}
            className="flex items-center text-gray-600 hover:text-gray-900 mb-4 transition-colors"
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            Back to Dashboard
          </button>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{server.name}</h1>
              <p className="text-gray-600 mt-1">{server.hostname}</p>
            </div>
            <div className="flex items-center space-x-4">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(server.status)}`}>
                {server.status}
              </span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getHealthColor(server.health_status)}`}>
                {server.health_status}
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Server Information */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Server Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">IP Address</label>
                  <p className="text-gray-900">{server.ip_address}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Port</label>
                  <p className="text-gray-900">{server.port}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Environment</label>
                  <p className="text-gray-900">{server.environment || 'Not specified'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Region</label>
                  <p className="text-gray-900">{server.region || 'Not specified'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Availability Zone</label>
                  <p className="text-gray-900">{server.availability_zone || 'Not specified'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Server Type</label>
                  <p className="text-gray-900">{server.server_type || 'Not specified'}</p>
                </div>
              </div>
            </div>

            {/* Specifications */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Specifications</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center">
                  <CpuChipIcon className="h-8 w-8 text-blue-600 mr-3" />
                  <div>
                    <label className="text-sm font-medium text-gray-500">CPU Cores</label>
                    <p className="text-gray-900">{server.cpu_cores || 'Not specified'}</p>
                  </div>
                </div>
                <div className="flex items-center">
                  <CircleStackIcon className="h-8 w-8 text-green-600 mr-3" />
                  <div>
                    <label className="text-sm font-medium text-gray-500">Memory</label>
                    <p className="text-gray-900">{server.memory_gb ? `${server.memory_gb} GB` : 'Not specified'}</p>
                  </div>
                </div>
                <div className="flex items-center">
                  <ServerIcon className="h-8 w-8 text-purple-600 mr-3" />
                  <div>
                    <label className="text-sm font-medium text-gray-500">Storage</label>
                    <p className="text-gray-900">{server.storage_gb ? `${server.storage_gb} GB` : 'Not specified'}</p>
                  </div>
                </div>
              </div>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">OS Type</label>
                  <p className="text-gray-900">{server.os_type || 'Not specified'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">OS Version</label>
                  <p className="text-gray-900">{server.os_version || 'Not specified'}</p>
                </div>
              </div>
            </div>

            {/* Tags */}
            {server.tags && server.tags.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Tags</h2>
                <div className="flex flex-wrap gap-2">
                  {server.tags.map((tag) => (
                    <span
                      key={tag.id}
                      className="px-3 py-1 rounded-full text-sm font-medium"
                      style={{
                        backgroundColor: tag.color + '20',
                        color: tag.color,
                        border: `1px solid ${tag.color}40`
                      }}
                    >
                      {tag.name}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <button className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                  Connect via SSH
                </button>
                <button className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors">
                  Restart Server
                </button>
                <button className="w-full bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700 transition-colors">
                  Update Server
                </button>
                <button className="w-full bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors">
                  Terminate Server
                </button>
              </div>
            </div>

            {/* Server Details */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Details</h2>
              <div className="space-y-3">
                <div>
                  <label className="text-sm font-medium text-gray-500">Server ID</label>
                  <p className="text-gray-900 text-sm font-mono">{server.id}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Created</label>
                  <p className="text-gray-900 text-sm">
                    {new Date(server.created_at).toLocaleDateString()}
                  </p>
                </div>
                {server.updated_at && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Last Updated</label>
                    <p className="text-gray-900 text-sm">
                      {new Date(server.updated_at).toLocaleDateString()}
                    </p>
                  </div>
                )}
                {server.created_by && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Created By</label>
                    <p className="text-gray-900 text-sm">{server.created_by}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ServerDetail; 