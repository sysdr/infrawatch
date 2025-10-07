import React from 'react';
import { Bell, Settings, User, Search, Menu } from 'lucide-react';

const Header = () => {
  return (
    <header className="bg-slate-800/90 backdrop-blur-md border-b border-slate-700 shadow-xl sticky top-0 z-50">
      <div className="px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-slate-600 to-slate-700 rounded-xl flex items-center justify-center shadow-lg border border-slate-600">
              <span className="text-white font-bold text-sm">AR</span>
            </div>
            <div>
              <h1 className="text-xl font-semibold text-slate-100">Alert Rules</h1>
              <p className="text-sm text-slate-400">Management Dashboard</p>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Search Bar */}
          <div className="hidden md:block relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-slate-400" />
            </div>
            <input
              type="text"
              placeholder="Search rules, templates..."
              className="bg-slate-700 border-slate-600 text-black placeholder-gray-600 focus:border-slate-500 focus:ring-slate-500 block w-full px-3 py-2 pl-10 border rounded-lg shadow-sm focus:outline-none focus:ring-2 transition-colors duration-200"
            />
          </div>
          
          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            <button className="btn-ghost p-2 relative">
              <Bell size={20} />
              <span className="absolute -top-1 -right-1 h-3 w-3 bg-danger-500 rounded-full"></span>
            </button>
            <button className="btn-ghost p-2">
              <Settings size={20} />
            </button>
            <div className="flex items-center space-x-2 pl-2 border-l border-slate-600">
              <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center border border-slate-600">
                <User size={16} className="text-slate-300" />
              </div>
              <div className="hidden md:block">
                <p className="text-sm font-medium text-slate-100">Admin User</p>
                <p className="text-xs text-slate-400">admin@company.com</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
