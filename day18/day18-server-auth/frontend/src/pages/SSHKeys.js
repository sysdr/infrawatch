import React, { useState, useEffect } from 'react';
import { Plus, Eye, RotateCcw, Trash2 } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const SSHKeys = () => {
  const [keys, setKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showPublicKey, setShowPublicKey] = useState(null);
  const [newKey, setNewKey] = useState({
    name: '',
    key_type: 'rsa',
    expires_days: 90
  });

  useEffect(() => {
    fetchKeys();
  }, []);

  const fetchKeys = async () => {
    try {
      const response = await axios.get('/ssh-keys/');
      setKeys(response.data);
    } catch (error) {
      toast.error('Failed to fetch SSH keys');
    } finally {
      setLoading(false);
    }
  };

  const createKey = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/ssh-keys/', newKey);
      toast.success('SSH key created successfully');
      setShowCreateModal(false);
      setNewKey({ name: '', key_type: 'rsa', expires_days: 90 });
      fetchKeys();
    } catch (error) {
      toast.error('Failed to create SSH key');
    }
  };

  const rotateKey = async (keyId) => {
    try {
      await axios.post(`/ssh-keys/${keyId}/rotate`);
      toast.success('SSH key rotated successfully');
      fetchKeys();
    } catch (error) {
      toast.error('Failed to rotate SSH key');
    }
  };

  const viewPublicKey = async (keyId) => {
    try {
      const response = await axios.get(`/ssh-keys/${keyId}`);
      setShowPublicKey(response.data);
    } catch (error) {
      toast.error('Failed to fetch key details');
    }
  };

  const getStatusColor = (status, expiresAt) => {
    if (status === 'expired') return 'status-expired';
    if (new Date(expiresAt) < new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)) {
      return 'status-expiring';
    }
    return 'status-active';
  };

  if (loading) return <div className="loading">Loading SSH keys...</div>;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">SSH Keys</h1>
        <p className="page-subtitle">Manage SSH key pairs for server authentication</p>
      </div>

      <div className="content-card">
        <div className="card-header">
          <h2 className="card-title">SSH Key Management</h2>
          <button 
            className="btn btn-primary"
            onClick={() => setShowCreateModal(true)}
          >
            <Plus size={16} style={{ marginRight: '8px' }} />
            Create Key
          </button>
        </div>

        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Status</th>
              <th>Created</th>
              <th>Expires</th>
              <th>Last Used</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {keys.map((key) => (
              <tr key={key.id}>
                <td>{key.name}</td>
                <td>{key.key_type.toUpperCase()}</td>
                <td>
                  <span className={`status-badge ${getStatusColor(key.status, key.expires_at)}`}>
                    {key.status}
                  </span>
                </td>
                <td>{new Date(key.created_at).toLocaleDateString()}</td>
                <td>{key.expires_at ? new Date(key.expires_at).toLocaleDateString() : 'Never'}</td>
                <td>{key.last_used ? new Date(key.last_used).toLocaleDateString() : 'Never'}</td>
                <td>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button 
                      className="btn btn-secondary"
                      onClick={() => viewPublicKey(key.id)}
                      title="View Public Key"
                    >
                      <Eye size={16} />
                    </button>
                    <button 
                      className="btn btn-secondary"
                      onClick={() => rotateKey(key.id)}
                      title="Rotate Key"
                    >
                      <RotateCcw size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Create Key Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Create SSH Key</h3>
            </div>
            <form onSubmit={createKey}>
              <div className="form-group">
                <label className="form-label">Key Name</label>
                <input
                  type="text"
                  className="form-input"
                  value={newKey.name}
                  onChange={(e) => setNewKey({ ...newKey, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Key Type</label>
                <select
                  className="form-input"
                  value={newKey.key_type}
                  onChange={(e) => setNewKey({ ...newKey, key_type: e.target.value })}
                >
                  <option value="rsa">RSA</option>
                  <option value="ed25519">Ed25519</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Expires in (days)</label>
                <input
                  type="number"
                  className="form-input"
                  value={newKey.expires_days}
                  onChange={(e) => setNewKey({ ...newKey, expires_days: parseInt(e.target.value) })}
                  min="1"
                  max="365"
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create Key
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Public Key Modal */}
      {showPublicKey && (
        <div className="modal-overlay" onClick={() => setShowPublicKey(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Public Key: {showPublicKey.name}</h3>
            </div>
            <div className="form-group">
              <label className="form-label">Public Key</label>
              <textarea
                className="form-input"
                value={showPublicKey.public_key}
                readOnly
                rows="6"
                style={{ fontFamily: 'monospace', fontSize: '12px' }}
              />
            </div>
            <div className="modal-actions">
              <button 
                className="btn btn-secondary" 
                onClick={() => {
                  navigator.clipboard.writeText(showPublicKey.public_key);
                  toast.success('Public key copied to clipboard');
                }}
              >
                Copy to Clipboard
              </button>
              <button className="btn btn-primary" onClick={() => setShowPublicKey(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SSHKeys;
