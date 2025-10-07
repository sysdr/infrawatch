import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  AlertTriangle, 
  FileText, 
  TestTube,
  BarChart3,
  Activity,
  Shield,
  Zap
} from 'lucide-react';
import clsx from 'clsx';

const Sidebar = () => {
  const location = useLocation();
  
  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard, count: null },
    { name: 'Alert Rules', href: '/rules', icon: AlertTriangle, count: 3 },
    { name: 'Templates', href: '/templates', icon: FileText, count: 5 },
    { name: 'Testing', href: '/testing', icon: TestTube, count: null },
  ];
  
  const quickActions = [
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'Monitoring', href: '/monitoring', icon: Activity },
    { name: 'Security', href: '/security', icon: Shield },
    { name: 'Automation', href: '/automation', icon: Zap },
  ];
  
  return (
    <div className="w-72 bg-slate-800/90 backdrop-blur-sm border-r border-slate-700 h-screen sticky top-0 overflow-y-auto shadow-xl">
      <div className="p-6">
        {/* Navigation */}
        <nav className="space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={clsx(
                  'flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 group relative',
                  isActive 
                    ? 'bg-slate-700 text-slate-100 shadow-sm border border-slate-600' 
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-700/50'
                )}
              >
                <Icon size={20} className="mr-3 flex-shrink-0" />
                <span className="flex-1">{item.name}</span>
                {item.count && (
                  <span className={clsx(
                    'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium',
                    isActive 
                      ? 'bg-slate-600 text-slate-200' 
                      : 'bg-slate-700 text-slate-300'
                  )}>
                    {item.count}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>
        
        {/* Divider */}
        <div className="my-6 border-t border-slate-700"></div>
        
        {/* Quick Actions */}
        <div>
          <h3 className="px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
            Quick Actions
          </h3>
          <nav className="space-y-1">
            {quickActions.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className="flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 text-slate-400 hover:text-slate-100 hover:bg-slate-700/50 group"
                >
                  <Icon size={18} className="mr-3 flex-shrink-0" />
                  <span className="flex-1">{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>
        
        {/* System Status */}
        <div className="mt-8 p-4 bg-gradient-to-r from-slate-700 to-slate-600 rounded-xl border border-slate-600 shadow-lg">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-gradient-to-r from-emerald-400 to-green-500 rounded-full mr-2 animate-pulse-soft"></div>
            <span className="text-sm font-medium text-slate-100">System Online</span>
          </div>
          <p className="text-xs text-slate-300 mt-1">All services running normally</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
