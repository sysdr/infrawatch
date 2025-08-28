import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  BarChart3, 
  Activity, 
  Calculator, 
  Database, 
  Settings,
  Home,
  TrendingUp
} from 'lucide-react';

const Sidebar = ({ currentPage, onPageChange, isConnected }) => {
  const location = useLocation();
  
  const navigation = [
    { name: 'Dashboard', icon: Home, href: '/', key: 'dashboard' },
    { name: 'Live Metrics', icon: Activity, href: '/metrics', key: 'metrics' },
    { name: 'Statistics', icon: Calculator, href: '/statistics', key: 'statistics' },
    { name: 'Rollups', icon: Database, href: '/rollups', key: 'rollups' },
  ];

  const isActive = (href) => {
    if (href === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(href);
  };

  return (
    <div className="h-full flex flex-col bg-white border-r border-gray-200">
      {/* Logo/Header */}
      <div className="flex items-center px-6 py-4 border-b border-gray-200">
        <div className="flex items-center">
          <BarChart3 className="h-8 w-8 text-blue-600" />
          <div className="ml-3">
            <h1 className="text-lg font-semibold text-gray-900">MetricsFlow</h1>
            <p className="text-xs text-gray-500">Aggregation System</p>
          </div>
        </div>
      </div>

      {/* Connection Status */}
      <div className="px-6 py-3 border-b border-gray-200">
        <div className="flex items-center">
          <div className={`w-2 h-2 rounded-full mr-3 ${
            isConnected ? 'bg-green-500' : 'bg-red-500'
          }`}></div>
          <span className={`text-sm font-medium ${
            isConnected ? 'text-green-600' : 'text-red-600'
          }`}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-4 space-y-1">
        {navigation.map((item) => {
          const isItemActive = isActive(item.href);
          return (
            <Link
              key={item.name}
              to={item.href}
              onClick={() => onPageChange(item.key)}
              className={`group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-150 ${
                isItemActive
                  ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600'
                  : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <item.icon
                className={`mr-3 h-5 w-5 ${
                  isItemActive ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-500'
                }`}
              />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-gray-200">
        <div className="text-xs text-gray-500">
          <p>Day 25: Metrics Aggregation</p>
          <p className="mt-1">Version 1.0.0</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
