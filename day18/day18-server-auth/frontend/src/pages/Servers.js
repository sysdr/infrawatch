import React, { useState, useEffect } from 'react';
import { Plus, Play, AlertCircle } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const Servers = () => {
  const [servers, setServers] = useState([]);
  const [sshKeys, setSshKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [testingConnection, setTestingConnection] = useState(null);
  const [newServer, setNewServer] = useState({
    name: '',
    hostname: '',
    port: 22,
    username: '',
    ssh_key_id: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [serversResponse, keysResponse] = await Promise.all([
        axios.get('/servers/'),
        axios.get('/ssh-keys/')
      ]);
      setServers(serversResponse.data);
      setSshKeys(keysResponse.data);
    } catch (error) {
      toast.error('Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const createServer = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/servers/', newServer);
      toast.success('Server added successfully');
      setShowCreateModal(false);
      setNewServer({ name: '', hostname: '', port: 22, username: '', ssh_key_id: '' });
      fetchData();
    } catch (error) {
      toast.error('Failed to add server');
    }
  };

  const testConnection = async (serverId) => {
    setTestingConnection(serverId);
    try {
      const response = await axios.post('/test-connection/', { server_id: serverId });
      if (response.data.success) {
        toast.success('Connection test successful');
      } else {
        toast.error(`Connection failed: ${response.data.message}`);
      }
      fetchData(); // Refresh to update status
    } catch (error) {
      toast.error('Connection test failed');
    } finally {
      setTestingConnection(null);
    }
  };

  if (loading) return <div className="loading">Loading servers...</div>;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Servers</h1>
        <p className="page-subtitle">Manage server connections and authentication</p>
      </div>

      <div className="content-card">
        <div className="card-header">
          <h2 className="card-title">Server Management</h2>
          <button 
            className="btn btn-primary"
            onClick={() => setShowCreateModal(true)}
          >
            <Plus size={16} style={{ marginRight: '8px' }} />
            Add Server
          </button>
        </div>

        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Hostname</th>
              <th>Port</th>
              <th>Username</th>
              <th>SSH Key</th>
              <th>Status</th>
              <th>Last Check</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {servers.map((server) => {
              const sshKey = sshKeys.find(key => key.id === server.ssh_key_id);
              return (
                <tr key={server.id}>
                  <td>{server.name}</td>
                  <td>{server.hostname}</td>
                  <td>{server.port}</td>
                  <td>{server.username}</td>
                  <td>{sshKey ? sshKey.name : 'Unknown'}</td>
                  <td>
                    <span className={`status-badge ${
                      server.status === 'connected' ? 'status-connected' : 
                      server.status === 'failed' ? 'status-failed' : 'status-expiring'
                    }`}>
                      {server.status}
                    </span>
                  </td>
                  <td>
                    {server.last_check ? new Date(server.last_check).toLocaleString() : 'Never'}
                  </td>
                  <td>
                    <button 
                      className="btn btn-secondary"
                      onClick={() => testConnection(server.id)}
                      disabled={testingConnection === server.id}
                      title="Test Connection"
                    >
                      {testingConnection === server.id ? (
                        <AlertCircle size={16} className="animate-spin" />
                      ) : (
                        <Play size={16} />
                      )}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Create Server Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Add Server</h3>
            </div>
            <form onSubmit={createServer}>
              <div className="form-group">
                <label className="form-label">Server Name</label>
                <input
                  type="text"
                  className="form-input"
                  value={newServer.name}
                  onChange={(e) => setNewServer({ ...newServer, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Hostname</label>
                <input
                  type="text"
                  className="form-input"
                  value={newServer.hostname}
                  onChange={(e) => setNewServer({ ...newServer, hostname: e.target.value })}
                  placeholder="example.com or 192.168.1.100"
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Port</label>
                <input
                  type="number"
                  className="form-input"
                  value={newServer.port}
                  onChange={(e) => setNewServer({ ...newServer, port: parseInt(e.target.value) })}
                  min="1"
                  max="65535"
                />
              </div>
              <div className="form-group">
                <label className="form-label">Username</label>
                <input
                  type="text"
                  className="form-input"
                  value={newServer.username}
                  onChange={(e) => setNewServer({ ...newServer, username: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">SSH Key</label>
                <select
                  className="form-input"
                  value={newServer.ssh_key_id}
                  onChange={(e) => setNewServer({ ...newServer, ssh_key_id: e.target.value })}
                  required
                >
                  <option value="">Select SSH Key</option>
                  {sshKeys.filter(key => key.status === 'active').map(key => (
                    <option key={key.id} value={key.id}>{key.name}</option>
                  ))}
                </select>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Add Server
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Servers;
