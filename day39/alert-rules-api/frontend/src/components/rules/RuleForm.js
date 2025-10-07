import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from 'react-query';
import { X, Save } from 'lucide-react';
import { rulesAPI } from '../../services/api';

const RuleForm = ({ rule, onClose, onSuccess }) => {
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  
  const { register, handleSubmit, watch, formState: { errors } } = useForm({
    defaultValues: rule || {
      name: '',
      description: '',
      expression: '',
      severity: 'warning',
      enabled: true,
      tags: [],
      thresholds: {}
    }
  });
  
  const createMutation = useMutation(rulesAPI.createRule, { onSuccess });
  const updateMutation = useMutation(
    (data) => rulesAPI.updateRule(rule.id, data),
    { onSuccess }
  );
  
  const onSubmit = (data) => {
    try {
      data.thresholds = JSON.parse(data.thresholdsJson || '{}');
      data.tags = data.tagsString ? data.tagsString.split(',').map(t => t.trim()) : [];
      
      if (rule) {
        updateMutation.mutate(data);
      } else {
        createMutation.mutate(data);
      }
    } catch (e) {
      alert('Invalid JSON in thresholds');
    }
  };
  
  const validateRule = async () => {
    const expression = watch('expression');
    const thresholdsJson = watch('thresholdsJson');
    
    if (!expression || !thresholdsJson) return;
    
    try {
      setIsValidating(true);
      const thresholds = JSON.parse(thresholdsJson);
      const response = await rulesAPI.validateSyntax(expression, thresholds);
      setValidationResult(response.data);
    } catch (error) {
      setValidationResult({ 
        overall_valid: false, 
        expression_message: 'Validation failed' 
      });
    } finally {
      setIsValidating(false);
    }
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-wp-text">
            {rule ? 'Edit Rule' : 'Create New Rule'}
          </h2>
          <button
            onClick={onClose}
            className="text-wp-text-light hover:text-wp-text"
          >
            <X size={24} />
          </button>
        </div>
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-wp-text mb-1">
              Rule Name
            </label>
            <input
              {...register('name', { required: 'Name is required' })}
              className="wp-input"
              placeholder="Enter rule name"
            />
            {errors.name && (
              <p className="text-red-600 text-sm mt-1">{errors.name.message}</p>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-wp-text mb-1">
              Description
            </label>
            <textarea
              {...register('description')}
              className="wp-input"
              rows={3}
              placeholder="Enter rule description"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-wp-text mb-1">
              Expression
            </label>
            <textarea
              {...register('expression', { required: 'Expression is required' })}
              className="wp-input font-mono"
              rows={3}
              placeholder="avg(cpu_usage_percent) > {threshold}"
            />
            {errors.expression && (
              <p className="text-red-600 text-sm mt-1">{errors.expression.message}</p>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-wp-text mb-1">
              Thresholds (JSON)
            </label>
            <textarea
              {...register('thresholdsJson', { required: 'Thresholds are required' })}
              className="wp-input font-mono"
              rows={3}
              placeholder='{"threshold": 85}'
              defaultValue={rule ? JSON.stringify(rule.thresholds, null, 2) : ''}
            />
            {errors.thresholdsJson && (
              <p className="text-red-600 text-sm mt-1">{errors.thresholdsJson.message}</p>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-wp-text mb-1">
              Severity
            </label>
            <select {...register('severity')} className="wp-input">
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="critical">Critical</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-wp-text mb-1">
              Tags (comma-separated)
            </label>
            <input
              {...register('tagsString')}
              className="wp-input"
              placeholder="infrastructure, cpu, monitoring"
              defaultValue={rule ? rule.tags.join(', ') : ''}
            />
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              {...register('enabled')}
              className="mr-2"
            />
            <label className="text-sm font-medium text-wp-text">
              Enable this rule
            </label>
          </div>
          
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={validateRule}
              disabled={isValidating}
              className="wp-button-secondary"
            >
              {isValidating ? 'Validating...' : 'Validate'}
            </button>
            <button type="submit" className="wp-button">
              <Save size={16} className="mr-2" />
              {rule ? 'Update' : 'Create'} Rule
            </button>
          </div>
          
          {validationResult && (
            <div className={`p-4 rounded-lg ${
              validationResult.overall_valid ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
            }`}>
              <p className={`text-sm font-medium ${
                validationResult.overall_valid ? 'text-green-800' : 'text-red-800'
              }`}>
                {validationResult.overall_valid ? 'Rule is valid!' : 'Validation failed'}
              </p>
              {!validationResult.overall_valid && (
                <p className="text-red-700 text-sm mt-1">
                  {validationResult.expression_message || validationResult.thresholds_message || validationResult.logic_message}
                </p>
              )}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default RuleForm;
