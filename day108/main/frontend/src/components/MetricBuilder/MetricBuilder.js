import React, { useState } from 'react';
import { metricsAPI } from '../../services/api';
import FormulaEditor from '../FormulaEditor/FormulaEditor';
import './MetricBuilder.css';

const MetricBuilder = ({ onMetricCreated }) => {
    const [formData, setFormData] = useState({
        name: '',
        display_name: '',
        description: '',
        formula: '',
        variables: [],
        category: 'custom',
        unit: '',
        aggregation_type: 'sum',
    });
    
    const [newVariable, setNewVariable] = useState('');
    const [isFormulaValid, setIsFormulaValid] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState('');

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const addVariable = () => {
        if (newVariable && !formData.variables.includes(newVariable)) {
            setFormData(prev => ({
                ...prev,
                variables: [...prev.variables, newVariable]
            }));
            setNewVariable('');
        }
    };

    const removeVariable = (variable) => {
        setFormData(prev => ({
            ...prev,
            variables: prev.variables.filter(v => v !== variable)
        }));
    };

    const handleFormulaChange = (formula, isValid) => {
        setFormData(prev => ({ ...prev, formula }));
        setIsFormulaValid(isValid);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!isFormulaValid) {
            setError('Please fix formula errors before submitting');
            return;
        }

        setIsSubmitting(true);
        setError('');

        try {
            const result = await metricsAPI.createMetric(formData);
            if (onMetricCreated) {
                onMetricCreated(result);
            }
            // Reset form
            setFormData({
                name: '',
                display_name: '',
                description: '',
                formula: '',
                variables: [],
                category: 'custom',
                unit: '',
                aggregation_type: 'sum',
            });
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to create metric');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="metric-builder">
            <div className="builder-header">
                <h2>Create Custom Metric</h2>
                <p>Define your metric formula and configuration</p>
            </div>

            <form onSubmit={handleSubmit}>
                <div className="form-section">
                    <h3>Basic Information</h3>
                    
                    <div className="form-row">
                        <div className="form-group">
                            <label>Metric Name *</label>
                            <input
                                type="text"
                                name="name"
                                value={formData.name}
                                onChange={handleInputChange}
                                placeholder="e.g., profit_margin"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>Display Name *</label>
                            <input
                                type="text"
                                name="display_name"
                                value={formData.display_name}
                                onChange={handleInputChange}
                                placeholder="e.g., Profit Margin"
                                required
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Description</label>
                        <textarea
                            name="description"
                            value={formData.description}
                            onChange={handleInputChange}
                            placeholder="Describe what this metric measures"
                            rows="2"
                        />
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label>Category</label>
                            <select
                                name="category"
                                value={formData.category}
                                onChange={handleInputChange}
                            >
                                <option value="custom">Custom</option>
                                <option value="financial">Financial</option>
                                <option value="operational">Operational</option>
                                <option value="performance">Performance</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label>Unit</label>
                            <input
                                type="text"
                                name="unit"
                                value={formData.unit}
                                onChange={handleInputChange}
                                placeholder="e.g., %, $, units"
                            />
                        </div>
                    </div>
                </div>

                <div className="form-section">
                    <h3>Variables</h3>
                    
                    <div className="variable-input">
                        <input
                            type="text"
                            value={newVariable}
                            onChange={(e) => setNewVariable(e.target.value)}
                            placeholder="Variable name (e.g., revenue, cost)"
                            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addVariable())}
                        />
                        <button type="button" onClick={addVariable} className="add-btn">
                            Add Variable
                        </button>
                    </div>

                    <div className="variables-list">
                        {formData.variables.map(variable => (
                            <div key={variable} className="variable-tag">
                                <span>{variable}</span>
                                <button
                                    type="button"
                                    onClick={() => removeVariable(variable)}
                                    className="remove-btn"
                                >
                                    ×
                                </button>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="form-section">
                    <FormulaEditor
                        onFormulaChange={handleFormulaChange}
                        initialFormula={formData.formula}
                        variables={formData.variables}
                    />
                </div>

                {error && <div className="error-message">{error}</div>}

                <div className="form-actions">
                    <button
                        type="submit"
                        className="submit-btn"
                        disabled={isSubmitting || !isFormulaValid}
                    >
                        {isSubmitting ? 'Creating...' : 'Create Metric'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default MetricBuilder;
