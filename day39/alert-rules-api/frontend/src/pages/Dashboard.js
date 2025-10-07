import React from 'react';
import { useQuery } from 'react-query';
import { useNavigate } from 'react-router-dom';
import { 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  TrendingUp, 
  Plus, 
  FileText, 
  TestTube, 
  BarChart3,
  Activity,
  Shield,
  Zap,
  ArrowRight,
  AlertCircle,
  CheckCircle2,
  XCircle
} from 'lucide-react';
import { rulesAPI } from '../services/api';

const Dashboard = () => {
  const navigate = useNavigate();
  const { data: rules = [], isLoading } = useQuery('rules', () => rulesAPI.getRules().then(res => res.data));
  
  const stats = {
    totalRules: rules.length,
    enabledRules: rules.filter(rule => rule.enabled).length,
    disabledRules: rules.filter(rule => !rule.enabled).length,
    criticalRules: rules.filter(rule => rule.severity === 'critical').length,
  };
  
  const StatCard = ({ title, value, icon: Icon, color, trend, description }) => {
    const colorClasses = {
      primary: 'bg-gradient-to-br from-slate-700 to-slate-600 text-slate-200',
      success: 'bg-gradient-to-br from-emerald-800 to-emerald-700 text-emerald-200', 
      warning: 'bg-gradient-to-br from-amber-800 to-amber-700 text-amber-200',
      danger: 'bg-gradient-to-br from-red-800 to-red-700 text-red-200',
      accent: 'bg-gradient-to-br from-slate-600 to-slate-500 text-slate-200'
    };
    
    return (
      <div className="stat-card group">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className={`p-3 rounded-xl ${colorClasses[color]} shadow-lg`}>
              <Icon className="h-6 w-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-black">{title}</p>
              <p className="text-3xl font-bold text-black">{value}</p>
              {description && (
                <p className="text-xs text-gray-800 mt-1">{description}</p>
              )}
            </div>
          </div>
          {trend && (
            <div className="flex items-center text-sm text-black">
              <TrendingUp className="h-4 w-4 mr-1" />
              <span>{trend}</span>
            </div>
          )}
        </div>
      </div>
    );
  };
  
  const QuickActionCard = ({ title, description, icon: Icon, onClick, color = 'primary' }) => {
    const colorClasses = {
      primary: 'bg-gradient-to-br from-slate-700 to-slate-600 text-slate-200 hover:from-slate-600 hover:to-slate-500',
      success: 'bg-gradient-to-br from-emerald-800 to-emerald-700 text-emerald-200 hover:from-emerald-700 hover:to-emerald-600',
      warning: 'bg-gradient-to-br from-amber-800 to-amber-700 text-amber-200 hover:from-amber-700 hover:to-amber-600',
      danger: 'bg-gradient-to-br from-red-800 to-red-700 text-red-200 hover:from-red-700 hover:to-red-600',
      accent: 'bg-gradient-to-br from-slate-600 to-slate-500 text-slate-200 hover:from-slate-500 hover:to-slate-400'
    };
    
    return (
      <button
        onClick={onClick}
        className="card-interactive p-4 text-left group w-full"
      >
        <div className="flex items-center">
          <div className={`p-3 rounded-lg ${colorClasses[color]} group-hover:scale-110 transition-transform duration-200`}>
            <Icon className="h-5 w-5" />
          </div>
          <div className="ml-4 flex-1">
            <h3 className="font-semibold text-black group-hover:text-gray-900 transition-colors">
              {title}
            </h3>
            <p className="text-sm text-gray-800 mt-1 group-hover:text-gray-700 transition-colors">{description}</p>
          </div>
          <ArrowRight className="h-4 w-4 text-gray-800 group-hover:text-black group-hover:translate-x-1 transition-all duration-200" />
        </div>
      </button>
    );
  };
  
  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical': return <AlertCircle className="h-4 w-4 text-danger-500" />;
      case 'warning': return <AlertTriangle className="h-4 w-4 text-warning-500" />;
      case 'info': return <CheckCircle2 className="h-4 w-4 text-primary-500" />;
      default: return <XCircle className="h-4 w-4 text-gray-500" />;
    }
  };
  
  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'critical': return 'badge-danger';
      case 'warning': return 'badge-warning';
      case 'info': return 'badge-info';
      default: return 'badge-gray';
    }
  };
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }
  
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">Dashboard</h1>
          <p className="mt-2 text-slate-400">Monitor and manage your alert rules system</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center text-sm text-slate-400">
            <div className="w-2 h-2 bg-emerald-500 rounded-full mr-2 animate-pulse-soft"></div>
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Total Rules" 
          value={stats.totalRules} 
          icon={AlertTriangle} 
          color="primary"
          trend="+12%"
          description="Active monitoring rules"
        />
        <StatCard 
          title="Enabled Rules" 
          value={stats.enabledRules} 
          icon={CheckCircle} 
          color="success"
          trend="+5%"
          description="Currently active"
        />
        <StatCard 
          title="Disabled Rules" 
          value={stats.disabledRules} 
          icon={Clock} 
          color="warning"
          description="Temporarily inactive"
        />
        <StatCard 
          title="Critical Rules" 
          value={stats.criticalRules} 
          icon={TrendingUp} 
          color="danger"
          trend="+2"
          description="High priority alerts"
        />
      </div>
      
      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Rules */}
        <div className="lg:col-span-2">
          <div className="card p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-slate-100">Recent Rules</h3>
              <button 
                onClick={() => navigate('/rules')}
                className="text-sm text-slate-400 hover:text-slate-200 font-medium"
              >
                View all
              </button>
            </div>
            <div className="space-y-4">
              {rules.slice(0, 5).map((rule, index) => (
                <div 
                  key={rule.id} 
                  className="flex items-center justify-between p-4 bg-slate-700 rounded-lg hover:bg-slate-600 transition-colors group"
                >
                  <div className="flex items-center space-x-3">
                    {getSeverityIcon(rule.severity)}
                    <div>
                      <p className="font-medium text-slate-100 group-hover:text-slate-50 transition-colors">
                        {rule.name}
                      </p>
                      <p className="text-sm text-slate-400">{rule.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className={getSeverityBadge(rule.severity)}>
                      {rule.severity}
                    </span>
                    <div className={`w-2 h-2 rounded-full ${
                      rule.enabled ? 'bg-emerald-500' : 'bg-slate-500'
                    }`}></div>
                  </div>
                </div>
              ))}
              {rules.length === 0 && (
                <div className="text-center py-8 text-slate-400">
                  <AlertTriangle className="h-8 w-8 mx-auto mb-2 text-slate-500" />
                  <p>No rules found. Create your first rule to get started.</p>
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Quick Actions */}
        <div className="space-y-6">
          <div className="card p-6">
            <h3 className="text-lg font-bold text-black mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <QuickActionCard
                title="Create New Rule"
                description="Set up a new alert rule"
                icon={Plus}
                onClick={() => navigate('/rules')}
                color="primary"
              />
              <QuickActionCard
                title="Browse Templates"
                description="Use pre-built rule templates"
                icon={FileText}
                onClick={() => navigate('/templates')}
                color="success"
              />
              <QuickActionCard
                title="Test Rules"
                description="Validate rule expressions"
                icon={TestTube}
                onClick={() => navigate('/testing')}
                color="warning"
              />
              <QuickActionCard
                title="View Analytics"
                description="Monitor rule performance"
                icon={BarChart3}
                onClick={() => navigate('/rules')}
                color="accent"
              />
            </div>
          </div>
          
          {/* System Status */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-black mb-4">System Status</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-gradient-to-r from-emerald-400 to-green-500 rounded-full mr-3 animate-pulse-soft"></div>
                  <span className="text-sm font-medium text-black">API Server</span>
                </div>
                <span className="text-sm text-emerald-400 font-medium">Online</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-gradient-to-r from-emerald-400 to-green-500 rounded-full mr-3 animate-pulse-soft"></div>
                  <span className="text-sm font-medium text-black">Database</span>
                </div>
                <span className="text-sm text-emerald-400 font-medium">Connected</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-gradient-to-r from-emerald-400 to-green-500 rounded-full mr-3 animate-pulse-soft"></div>
                  <span className="text-sm font-medium text-black">Monitoring</span>
                </div>
                <span className="text-sm text-emerald-400 font-medium">Active</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
