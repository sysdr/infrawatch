import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Mail, MessageSquare, Bell, Slack, Edit, Eye, CheckCircle, AlertTriangle } from 'lucide-react';
import { fetchTemplates, validateTemplate } from '../services/api';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [validationStatus, setValidationStatus] = useState({});

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const data = await fetchTemplates();
      setTemplates(data);
      
      // Load validation status for each template
      const validation = {};
      for (const template of data) {
        try {
          const result = await validateTemplate(template.id);
          validation[template.id] = result;
        } catch (error) {
          validation[template.id] = { valid: false, errors: ['Validation failed'] };
        }
      }
      setValidationStatus(validation);
    } catch (error) {
      toast.error('Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  const getFormatIcon = (format) => {
    const icons = {
      email: Mail,
      sms: MessageSquare,
      push: Bell,
      slack: Slack,
    };
    return icons[format] || Mail;
  };

  const formatTypeColors = {
    email: 'bg-blue-100 text-blue-800',
    sms: 'bg-green-100 text-green-800',
    push: 'bg-purple-100 text-purple-800',
    slack: 'bg-orange-100 text-orange-800',
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Notification Templates
          </h1>
          <p className="text-gray-600 mt-2">
            Manage and test your notification templates across all channels
          </p>
        </div>
        
        <Link
          to="/editor"
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>New Template</span>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <Mail className="w-8 h-8 text-blue-600" />
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-900">
                {templates.length}
              </h3>
              <p className="text-gray-600">Total Templates</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <CheckCircle className="w-8 h-8 text-green-600" />
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-900">
                {Object.values(validationStatus).filter(v => v.valid).length}
              </h3>
              <p className="text-gray-600">Valid Templates</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <Bell className="w-8 h-8 text-purple-600" />
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-900">
                {templates.reduce((acc, t) => acc + t.formats.length, 0)}
              </h3>
              <p className="text-gray-600">Total Formats</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <MessageSquare className="w-8 h-8 text-orange-600" />
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-900">
                {templates.reduce((acc, t) => acc + t.locales.length, 0)}
              </h3>
              <p className="text-gray-600">Total Locales</p>
            </div>
          </div>
        </div>
      </div>

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map((template) => {
          const validation = validationStatus[template.id] || {};
          
          return (
            <div key={template.id} className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {template.name}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {template.description}
                    </p>
                  </div>
                  
                  <div className="flex items-center">
                    {validation.valid ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <AlertTriangle className="w-5 h-5 text-red-500" />
                    )}
                  </div>
                </div>
                
                {/* Formats */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {template.formats.map((format) => {
                    const Icon = getFormatIcon(format.format_type);
                    return (
                      <span
                        key={format.format_type}
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          formatTypeColors[format.format_type] || 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        <Icon className="w-3 h-3 mr-1" />
                        {format.format_type}
                      </span>
                    );
                  })}
                </div>
                
                {/* Locales */}
                <div className="mb-4">
                  <p className="text-sm text-gray-600 mb-2">
                    Languages: {template.locales.join(', ').toUpperCase()}
                  </p>
                </div>
                
                {/* Validation Issues */}
                {!validation.valid && validation.errors && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                    <p className="text-sm text-red-800 font-medium mb-1">
                      Validation Issues:
                    </p>
                    <ul className="text-xs text-red-700 list-disc list-inside">
                      {validation.errors.slice(0, 2).map((error, index) => (
                        <li key={index}>{error}</li>
                      ))}
                      {validation.errors.length > 2 && (
                        <li>+ {validation.errors.length - 2} more...</li>
                      )}
                    </ul>
                  </div>
                )}
                
                {/* Actions */}
                <div className="flex space-x-2">
                  <Link
                    to={`/editor/${template.id}`}
                    className="flex-1 bg-blue-50 hover:bg-blue-100 text-blue-700 px-3 py-2 rounded-md text-sm font-medium flex items-center justify-center space-x-1 transition-colors"
                  >
                    <Edit className="w-4 h-4" />
                    <span>Edit</span>
                  </Link>
                  
                  <Link
                    to={`/preview/${template.id}`}
                    className="flex-1 bg-gray-50 hover:bg-gray-100 text-gray-700 px-3 py-2 rounded-md text-sm font-medium flex items-center justify-center space-x-1 transition-colors"
                  >
                    <Eye className="w-4 h-4" />
                    <span>Preview</span>
                  </Link>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      {templates.length === 0 && (
        <div className="text-center py-12">
          <Mail className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No templates yet
          </h3>
          <p className="text-gray-600 mb-4">
            Get started by creating your first notification template
          </p>
          <Link
            to="/editor"
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg inline-flex items-center space-x-2 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Create Template</span>
          </Link>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
