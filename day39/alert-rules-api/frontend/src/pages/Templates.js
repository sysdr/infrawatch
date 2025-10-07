import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Plus, Copy } from 'lucide-react';
import { templatesAPI } from '../services/api';

const Templates = () => {
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [ruleName, setRuleName] = useState('');
  const queryClient = useQueryClient();
  
  const { data: templates = [] } = useQuery('templates', () => 
    templatesAPI.getTemplates().then(res => res.data)
  );
  
  const createRuleMutation = useMutation(
    ({ templateId, name }) => templatesAPI.createRuleFromTemplate(templateId, name),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('rules');
        setSelectedTemplate(null);
        setRuleName('');
        alert('Rule created successfully!');
      },
    }
  );
  
  const initializeDefaultsMutation = useMutation(templatesAPI.initializeDefaults, {
    onSuccess: () => {
      queryClient.invalidateQueries('templates');
    },
  });
  
  const handleCreateRule = () => {
    if (!selectedTemplate || !ruleName.trim()) {
      alert('Please select a template and enter a rule name');
      return;
    }
    
    createRuleMutation.mutate({
      templateId: selectedTemplate.id,
      name: ruleName.trim()
    });
  };
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">Rule Templates</h1>
          <p className="mt-2 text-slate-400">Create rules from pre-built templates</p>
        </div>
        <button
          onClick={() => initializeDefaultsMutation.mutate()}
          className="wp-button-secondary"
        >
          <Plus size={20} className="mr-2" />
          Initialize Defaults
        </button>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {templates.map((template) => (
              <div
                key={template.id}
                className={`wp-card p-4 cursor-pointer transition-all ${
                  selectedTemplate?.id === template.id 
                    ? 'ring-2 ring-wp-blue border-wp-blue' 
                    : 'hover:shadow-md'
                }`}
                onClick={() => setSelectedTemplate(template)}
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-black">{template.name}</h3>
                  <span className="wp-badge wp-badge-info">{template.category}</span>
                </div>
                <p className="text-sm text-gray-800 mb-3">{template.description}</p>
                
                <div className="text-xs font-mono bg-wp-gray p-2 rounded">
                  {template.template_config.expression}
                </div>
                
                <div className="mt-3 flex flex-wrap gap-1">
                  {template.template_config.tags?.map((tag) => (
                    <span key={tag} className="wp-badge wp-badge-info text-xs">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="wp-card p-6">
          <h3 className="text-lg font-semibold text-black mb-4">Create Rule from Template</h3>
          
          {selectedTemplate ? (
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-black mb-2">{selectedTemplate.name}</h4>
                <p className="text-sm text-gray-800">{selectedTemplate.description}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-black mb-1">
                  Rule Name
                </label>
                <input
                  type="text"
                  value={ruleName}
                  onChange={(e) => setRuleName(e.target.value)}
                  className="wp-input"
                  placeholder="Enter rule name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-black mb-1">
                  Template Configuration
                </label>
                <pre className="text-xs bg-wp-gray p-3 rounded overflow-x-auto">
                  {JSON.stringify(selectedTemplate.template_config, null, 2)}
                </pre>
              </div>
              
              <button
                onClick={handleCreateRule}
                disabled={createRuleMutation.isLoading}
                className="w-full wp-button"
              >
                <Copy size={16} className="mr-2" />
                {createRuleMutation.isLoading ? 'Creating...' : 'Create Rule'}
              </button>
            </div>
          ) : (
            <p className="text-gray-800 text-center py-8">
              Select a template to create a rule
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Templates;
