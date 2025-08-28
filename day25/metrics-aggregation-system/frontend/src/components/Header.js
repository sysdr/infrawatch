import React from 'react';
import { Bell, Search, User, RefreshCw } from 'lucide-react';

const Header = ({ isConnected, systemStats, currentPage }) => {
  const getPageTitle = () => {
    switch (currentPage) {
      case 'metrics': return 'Live Metrics';
      case 'statistics': return 'Statistical Analysis';
      case 'rollups': return 'Data Rollups';
      default: return 'Dashboard';
    }
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Page Title */}
        <div>
          <h1 className="text-xl font-semibold text-gray-900">
            {getPageTitle()}
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Real-time metrics aggregation and analysis
          </p>
        </div>

        {/* Header Actions */}
        <div className="flex items-center space-x-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search metrics..."
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Refresh Button */}
          <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors">
            <RefreshCw className="h-5 w-5" />
          </button>

          {/* Notifications */}
          <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors relative">
            <Bell className="h-5 w-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          {/* User Menu */}
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">Admin User</p>
              <p className="text-xs text-gray-500">System Operator</p>
            </div>
            <div className="p-2 bg-gray-100 rounded-full">
              <User className="h-5 w-5 text-gray-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="mt-4 flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center space-x-6">
          <span>Last updated: {new Date().toLocaleTimeString()}</span>
          <span>Uptime: 99.9%</span>
          <span>Latency: &lt; 100ms</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></span>
          <span>{isConnected ? 'System Healthy' : 'Connection Issues'}</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
