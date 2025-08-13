import React from 'react';
import { Server } from '../../services/api';
import { Server as ServerIcon, Play, Square, RotateCcw, Trash2, Circle } from 'lucide-react';

interface ServerCardProps {
  server: Server;
  onAction: (id: number, action: string) => void;
  onDelete: (id: number) => void;
}

export const ServerCard: React.FC<ServerCardProps> = ({ server, onAction, onDelete }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'text-success-500';
      case 'creating':
      case 'starting':
      case 'stopping':
        return 'text-warning-500';
      case 'stopped':
        return 'text-gray-500';
      case 'error':
        return 'text-danger-500';
      default:
        return 'text-gray-500';
    }
  };

  const getStatusBadgeClass = (status: string) => {
    return `status-badge status-${status}`;
  };

  const isActionable = (action: string) => {
    switch (action) {
      case 'start':
        return ['stopped', 'error'].includes(server.status);
      case 'stop':
        return server.status === 'running';
      case 'restart':
        return server.status === 'running';
      default:
        return false;
    }
  };

  return (
    <div className="card p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-primary-50 rounded-lg">
            <ServerIcon className="w-6 h-6 text-primary-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{server.name}</h3>
            <div className="flex items-center space-x-2">
              <Circle className={`w-2 h-2 fill-current ${getStatusColor(server.status)}`} />
              <span className={getStatusBadgeClass(server.status)}>
                {server.status.charAt(0).toUpperCase() + server.status.slice(1)}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-2 mb-4">
        {server.description && (
          <p className="text-sm text-gray-600">{server.description}</p>
        )}
        {server.ip_address && (
          <p className="text-sm text-gray-500">IP: {server.ip_address}</p>
        )}
        {server.port && (
          <p className="text-sm text-gray-500">Port: {server.port}</p>
        )}
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <div className="flex space-x-2">
          <button
            onClick={() => onAction(server.id, 'start')}
            disabled={!isActionable('start')}
            className={`p-2 rounded-md transition-colors ${
              isActionable('start')
                ? 'bg-success-50 text-success-600 hover:bg-success-100'
                : 'bg-gray-50 text-gray-400 cursor-not-allowed'
            }`}
          >
            <Play className="w-4 h-4" />
          </button>
          <button
            onClick={() => onAction(server.id, 'stop')}
            disabled={!isActionable('stop')}
            className={`p-2 rounded-md transition-colors ${
              isActionable('stop')
                ? 'bg-warning-50 text-warning-600 hover:bg-warning-100'
                : 'bg-gray-50 text-gray-400 cursor-not-allowed'
            }`}
          >
            <Square className="w-4 h-4" />
          </button>
          <button
            onClick={() => onAction(server.id, 'restart')}
            disabled={!isActionable('restart')}
            className={`p-2 rounded-md transition-colors ${
              isActionable('restart')
                ? 'bg-primary-50 text-primary-600 hover:bg-primary-100'
                : 'bg-gray-50 text-gray-400 cursor-not-allowed'
            }`}
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
        
        <button
          onClick={() => onDelete(server.id)}
          className="p-2 bg-danger-50 text-danger-600 hover:bg-danger-100 rounded-md transition-colors"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
