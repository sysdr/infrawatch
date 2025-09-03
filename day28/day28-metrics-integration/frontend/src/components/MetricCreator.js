import React, { useState } from 'react';
import { X } from 'lucide-react';

const MetricCreator = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    value: '',
    source: '',
    tags: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError(''); // Clear error when user types
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      // Parse tags if provided
      let tags = null;
      if (formData.tags.trim()) {
        try {
          tags = JSON.parse(formData.tags);
        } catch {
          // If not valid JSON, treat as key-value pairs
          const tagPairs = formData.tags.split(',').map(pair => pair.trim());
          tags = {};
          tagPairs.forEach(pair => {
            const [key, value] = pair.split(':').map(s => s.trim());
            if (key && value) {
              tags[key] = value;
            }
          });
        }
      }

      const metric = {
        name: formData.name.trim(),
        value: parseFloat(formData.value),
        source: formData.source.trim(),
        tags
      };

      // Basic validation
      if (!metric.name || !metric.source || isNaN(metric.value)) {
        throw new Error('Please fill in all required fields with valid values');
      }

      await onSubmit(metric);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h3>Create New Metric</h3>
          <button className="modal-close" onClick={onCancel}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="metric-form">
          {error && (
            <div className="alert alert-error">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="name">Metric Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="e.g., cpu_usage, response_time"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="value">Value *</label>
            <input
              type="number"
              id="value"
              name="value"
              value={formData.value}
              onChange={handleInputChange}
              placeholder="e.g., 75.5"
              step="any"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="source">Source *</label>
            <input
              type="text"
              id="source"
              name="source"
              value={formData.source}
              onChange={handleInputChange}
              placeholder="e.g., server-01, web-app"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="tags">Tags (optional)</label>
            <input
              type="text"
              id="tags"
              name="tags"
              value={formData.tags}
              onChange={handleInputChange}
              placeholder='{"environment": "prod"} or env:prod,region:us-east'
            />
            <small>JSON format or key:value pairs separated by commas</small>
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onCancel}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={submitting}
            >
              {submitting ? 'Creating...' : 'Create Metric'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default MetricCreator;
