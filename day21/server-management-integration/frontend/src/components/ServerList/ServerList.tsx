import React, { useState, useEffect } from 'react';
import { Server, serverApi } from '../../services/api';
import { useWebSocket } from '../../hooks/useWebSocket';
import { ServerCard } from './ServerCard';
import { CreateServerModal } from './CreateServerModal';
import { Plus, RefreshCw, Activity } from 'lucide-react';

export const ServerList: React.FC = () => {
  const [servers, setServers] = useState<Server[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  const { sendMessage } = useWebSocket(
    (message) => {
      if (message.type === 'server_update' || message.type === 'server_created') {
        setServers(prev => {
          const existingIndex = prev.findIndex(s => s.id === message.data.id);
          if (existingIndex >= 0) {
            const updated = [...prev];
            updated[existingIndex] = message.data;
            return updated;
          } else {
            return [...prev, message.data];
          }
        });
      } else if (message.type === 'server_deleted') {
        setServers(prev => prev.filter(s => s.id !== message.data.id));
      }
    },
    () => setIsConnected(true),
    () => setIsConnected(false)
  );

  const fetchServers = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await serverApi.getServers();
      setServers(data);
    } catch (err) {
      setError('Failed to fetch servers');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateServer = async (serverData: any) => {
    try {
      await serverApi.createServer(serverData);
      setShowCreateModal(false);
      // Server will be added via WebSocket update
    } catch (err) {
      console.error('Failed to create server:', err);
    }
  };

  const handleServerAction = async (id: number, action: string) => {
    try {
      let status: string;
      switch (action) {
        case 'start':
          status = 'starting';
          break;
        case 'stop':
          status = 'stopping';
          break;
        case 'restart':
          status = 'starting';
          break;
        default:
          return;
      }
      
      await serverApi.updateServerStatus(id, status);
      // Status will be updated via WebSocket
    } catch (err) {
      console.error(`Failed to ${action} server:`, err);
    }
  };

  const handleDeleteServer = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this server?')) {
      try {
        await serverApi.deleteServer(id);
        // Server will be removed via WebSocket update
      } catch (err) {
        console.error('Failed to delete server:', err);
      }
    }
  };

  useEffect(() => {
    fetchServers();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-primary-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <h1 className="text-2xl font-bold text-gray-900">Server Management</h1>
          <div className="flex items-center space-x-2">
            <Activity className={`w-4 h-4 ${isConnected ? 'text-success-500' : 'text-danger-500'}`} />
            <span className={`text-xs font-medium ${isConnected ? 'text-success-600' : 'text-danger-600'}`}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={fetchServers}
            className="btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Create Server</span>
          </button>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-danger-50 border border-danger-200 rounded-md p-4">
          <p className="text-danger-600">{error}</p>
        </div>
      )}

      {/* Servers Grid */}
      {servers.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No servers found</p>
          <p className="text-gray-400">Create your first server to get started</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {servers.map((server) => (
            <ServerCard
              key={server.id}
              server={server}
              onAction={handleServerAction}
              onDelete={handleDeleteServer}
            />
          ))}
        </div>
      )}

      {/* Create Server Modal */}
      {showCreateModal && (
        <CreateServerModal
          onClose={() => setShowCreateModal(false)}
          onCreate={handleCreateServer}
        />
      )}
    </div>
  );
};
