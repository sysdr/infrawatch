import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Plus, Edit, Trash2, Power, PowerOff } from 'lucide-react';
import { rulesAPI } from '../services/api';
import RuleForm from '../components/rules/RuleForm';

const Rules = () => {
  const [showForm, setShowForm] = useState(false);
  const [editingRule, setEditingRule] = useState(null);
  const queryClient = useQueryClient();
  
  const { data: rules = [], isLoading } = useQuery('rules', () => 
    rulesAPI.getRules().then(res => res.data)
  );
  
  const deleteMutation = useMutation(rulesAPI.deleteRule, {
    onSuccess: () => {
      queryClient.invalidateQueries('rules');
    },
  });
  
  const toggleMutation = useMutation(
    ({ id, enabled }) => rulesAPI.updateRule(id, { enabled }),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('rules');
      },
    }
  );
  
  const handleEdit = (rule) => {
    setEditingRule(rule);
    setShowForm(true);
  };
  
  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this rule?')) {
      deleteMutation.mutate(id);
    }
  };
  
  const handleToggle = (rule) => {
    toggleMutation.mutate({ id: rule.id, enabled: !rule.enabled });
  };
  
  if (isLoading) {
    return <div className="text-center py-8">Loading rules...</div>;
  }
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">Alert Rules</h1>
          <p className="mt-2 text-slate-400">Manage your alert rule configurations</p>
        </div>
        <button
          onClick={() => {
            setEditingRule(null);
            setShowForm(true);
          }}
          className="wp-button"
        >
          <Plus size={20} className="mr-2" />
          Create Rule
        </button>
      </div>
      
      {showForm && (
        <RuleForm
          rule={editingRule}
          onClose={() => {
            setShowForm(false);
            setEditingRule(null);
          }}
          onSuccess={() => {
            setShowForm(false);
            setEditingRule(null);
            queryClient.invalidateQueries('rules');
          }}
        />
      )}
      
      <div className="wp-card">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-wp-gray-dark">
            <thead className="bg-wp-gray">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-wp-text-light uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-wp-text-light uppercase tracking-wider">
                  Severity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-wp-text-light uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-wp-text-light uppercase tracking-wider">
                  Expression
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-wp-text-light uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-wp-gray-dark">
              {rules.map((rule) => (
                <tr key={rule.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-black">{rule.name}</div>
                      <div className="text-sm text-gray-800">{rule.description}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`wp-badge ${
                      rule.severity === 'critical' ? 'wp-badge-error' :
                      rule.severity === 'warning' ? 'wp-badge-warning' : 'wp-badge-info'
                    }`}>
                      {rule.severity}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`wp-badge ${
                      rule.enabled ? 'wp-badge-success' : 'wp-badge-warning'
                    }`}>
                      {rule.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-800 font-mono">
                    {rule.expression.slice(0, 50)}...
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <button
                      onClick={() => handleToggle(rule)}
                      className="text-wp-blue hover:text-wp-blue-dark"
                    >
                      {rule.enabled ? <PowerOff size={16} /> : <Power size={16} />}
                    </button>
                    <button
                      onClick={() => handleEdit(rule)}
                      className="text-wp-blue hover:text-wp-blue-dark"
                    >
                      <Edit size={16} />
                    </button>
                    <button
                      onClick={() => handleDelete(rule.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Rules;
