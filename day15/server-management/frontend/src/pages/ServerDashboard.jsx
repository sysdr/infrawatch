import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { PlusIcon, ServerIcon, CpuChipIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell } from 'recharts';
import { serverService } from '../services/api';

const COLORS = ['#10B981', '#F59E0B', '#EF4444', '#6B7280'];

function ServerDashboard() {
  const [servers, setServers] = useState([]);
  const [tags, setTags] = useState([]);
  const [filters, setFilters] = useState({
    environment: '',
    region: '',
    status: '',
    server_type: '',
    health_status: ''
  });
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    hostname: '',
    ip_address: '',
    port: 22,
    environment: '',
    region: '',
    server_type: '',
    cpu_cores: '',
    memory_gb: '',
    storage_gb: '',
    os_type: '',
    os_version: ''
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadServers();
    loadTags();
  }, [filters]);

  const loadServers = async () => {
    try {
      const data = await serverService.getServers(filters);
      setServers(data);
    } catch (error) {
      console.error('Failed to load servers:', error);
    } finally {
      setLoading(false);
    }
  };

  // Apply client-side filtering for better UX
  const getFilteredServers = () => {
    return servers.filter(server => {
      if (filters.environment && server.environment !== filters.environment) return false;
      if (filters.status && server.status !== filters.status) return false;
      if (filters.region && server.region !== filters.region) return false;
      if (filters.server_type && server.server_type !== filters.server_type) return false;
      if (filters.health_status && server.health_status !== filters.health_status) return false;
      return true;
    });
  };

  const loadTags = async () => {
    try {
      const data = await serverService.getTags();
      setTags(data);
    } catch (error) {
      console.error('Failed to load tags:', error);
    }
  };

  const handleAddServer = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      // Convert empty strings to null for optional fields
      const serverData = {
        ...formData,
        cpu_cores: formData.cpu_cores ? parseInt(formData.cpu_cores) : null,
        memory_gb: formData.memory_gb ? parseInt(formData.memory_gb) : null,
        storage_gb: formData.storage_gb ? parseInt(formData.storage_gb) : null,
        port: parseInt(formData.port)
      };
      
      await serverService.createServer(serverData);
      setShowAddModal(false);
      setFormData({
        name: '',
        hostname: '',
        ip_address: '',
        port: 22,
        environment: '',
        region: '',
        server_type: '',
        cpu_cores: '',
        memory_gb: '',
        storage_gb: '',
        os_type: '',
        os_version: ''
      });
      loadServers(); // Refresh the server list
    } catch (error) {
      console.error('Failed to create server:', error);
      alert('Failed to create server. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const getStatusStats = () => {
    const stats = servers.reduce((acc, server) => {
      acc[server.status] = (acc[server.status] || 0) + 1;
      return acc;
    }, {});
    
    return Object.entries(stats).map(([status, count]) => ({
      name: status,
      value: count
    }));
  };

  const getRegionStats = () => {
    const stats = servers.reduce((acc, server) => {
      if (server.region) {
        acc[server.region] = (acc[server.region] || 0) + 1;
      }
      return acc;
    }, {});
    
    return Object.entries(stats).map(([region, count]) => ({
      region,
      count
    }));
  };

  const getHealthStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-50';
      case 'degraded': return 'text-yellow-600 bg-yellow-50';
      case 'failed': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const statusStats = getStatusStats();
  const regionStats = getRegionStats();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Server Management</h1>
          <p className="text-gray-600">Monitor and manage your infrastructure</p>
        </div>
        <button 
          onClick={() => setShowAddModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <PlusIcon className="h-5 w-5" />
          <span>Add Server</span>
        </button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <ServerIcon className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Servers</p>
              <p className="text-2xl font-bold text-gray-900">{servers.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <CpuChipIcon className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Healthy Servers</p>
              <p className="text-2xl font-bold text-gray-900">
                {servers.filter(s => s.health_status === 'healthy').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Status Distribution</h3>
          <PieChart width={200} height={150}>
            <Pie
              data={statusStats}
              cx={100}
              cy={75}
              innerRadius={30}
              outerRadius={60}
              dataKey="value"
            >
              {statusStats.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Servers by Region</h3>
          <BarChart width={400} height={250} data={regionStats}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="region" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#3B82F6" />
          </BarChart>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Filters</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <select
              value={filters.environment}
              onChange={(e) => setFilters({...filters, environment: e.target.value})}
              className="input"
            >
              <option value="">All Environments</option>
              <option value="dev">Development</option>
              <option value="staging">Staging</option>
              <option value="prod">Production</option>
              <option value="demo">Demo</option>
              <option value="test">Test</option>
              <option value="frontend-test">Frontend Test</option>
            </select>
            
            <select
              value={filters.status}
              onChange={(e) => setFilters({...filters, status: e.target.value})}
              className="input"
            >
              <option value="">All Statuses</option>
              <option value="active">Active</option>
              <option value="provisioning">Provisioning</option>
              <option value="draining">Draining</option>
              <option value="terminated">Terminated</option>
            </select>

            <select
              value={filters.health_status}
              onChange={(e) => setFilters({...filters, health_status: e.target.value})}
              className="input"
            >
              <option value="">All Health Statuses</option>
              <option value="healthy">Healthy</option>
              <option value="degraded">Degraded</option>
              <option value="failed">Failed</option>
              <option value="unknown">Unknown</option>
            </select>

            <select
              value={filters.region}
              onChange={(e) => setFilters({...filters, region: e.target.value})}
              className="input"
            >
              <option value="">All Regions</option>
              <option value="us-east-1">US East 1</option>
              <option value="us-west-1">US West 1</option>
              <option value="eu-west-1">EU West 1</option>
            </select>
          </div>
          <div className="mt-4 flex justify-between items-center">
            <span className="text-sm text-gray-600">
              Showing {getFilteredServers().length} of {servers.length} servers
            </span>
            <button
              onClick={() => setFilters({environment: '', region: '', status: '', server_type: '', health_status: ''})}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Server List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Servers</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Server
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Health
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Environment
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Region
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tags
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {getFilteredServers().map((server) => (
                <tr key={server.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <Link
                        to={`/servers/${server.id}`}
                        className="text-sm font-medium text-blue-600 hover:text-blue-500"
                      >
                        {server.name}
                      </Link>
                      <div className="text-sm text-gray-500">{server.hostname}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                      {server.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getHealthStatusColor(server.health_status)}`}>
                      {server.health_status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {server.environment}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {server.region}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex flex-wrap gap-1">
                      {server.tags?.slice(0, 3).map((tag) => (
                        <span
                          key={tag.id}
                          className="px-2 py-1 text-xs rounded"
                          style={{ backgroundColor: tag.color + '20', color: tag.color }}
                        >
                          {tag.name}
                        </span>
                      ))}
                      {server.tags?.length > 3 && (
                        <span className="px-2 py-1 text-xs rounded bg-gray-100 text-gray-600">
                          +{server.tags.length - 3}
                        </span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Server Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">Add New Server</h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
            
            <form onSubmit={handleAddServer} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Server Name *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    className="input"
                    placeholder="Enter server name"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Hostname *
                  </label>
                  <input
                    type="text"
                    name="hostname"
                    value={formData.hostname}
                    onChange={handleInputChange}
                    required
                    className="input"
                    placeholder="Enter hostname"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    IP Address *
                  </label>
                  <input
                    type="text"
                    name="ip_address"
                    value={formData.ip_address}
                    onChange={handleInputChange}
                    required
                    className="input"
                    placeholder="Enter IP address"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Port
                  </label>
                  <input
                    type="number"
                    name="port"
                    value={formData.port}
                    onChange={handleInputChange}
                    className="input"
                    placeholder="22"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Environment
                  </label>
                  <select
                    name="environment"
                    value={formData.environment}
                    onChange={handleInputChange}
                    className="input"
                  >
                    <option value="">Select environment</option>
                    <option value="dev">Development</option>
                    <option value="staging">Staging</option>
                    <option value="prod">Production</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Region
                  </label>
                  <input
                    type="text"
                    name="region"
                    value={formData.region}
                    onChange={handleInputChange}
                    className="input"
                    placeholder="Enter region"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Server Type
                  </label>
                  <select
                    name="server_type"
                    value={formData.server_type}
                    onChange={handleInputChange}
                    className="input"
                  >
                    <option value="">Select server type</option>
                    <option value="web">Web Server</option>
                    <option value="database">Database</option>
                    <option value="cache">Cache</option>
                    <option value="worker">Worker</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    CPU Cores
                  </label>
                  <input
                    type="number"
                    name="cpu_cores"
                    value={formData.cpu_cores}
                    onChange={handleInputChange}
                    className="input"
                    placeholder="Enter CPU cores"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Memory (GB)
                  </label>
                  <input
                    type="number"
                    name="memory_gb"
                    value={formData.memory_gb}
                    onChange={handleInputChange}
                    className="input"
                    placeholder="Enter memory in GB"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Storage (GB)
                  </label>
                  <input
                    type="number"
                    name="storage_gb"
                    value={formData.storage_gb}
                    onChange={handleInputChange}
                    className="input"
                    placeholder="Enter storage in GB"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    OS Type
                  </label>
                  <input
                    type="text"
                    name="os_type"
                    value={formData.os_type}
                    onChange={handleInputChange}
                    className="input"
                    placeholder="e.g., Ubuntu, CentOS"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    OS Version
                  </label>
                  <input
                    type="text"
                    name="os_version"
                    value={formData.os_version}
                    onChange={handleInputChange}
                    className="input"
                    placeholder="e.g., 20.04, 7"
                  />
                </div>
              </div>
              
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {submitting ? 'Creating...' : 'Create Server'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default ServerDashboard;
