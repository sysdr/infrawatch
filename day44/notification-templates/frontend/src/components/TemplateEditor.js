import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Save, Eye, TestTube, ArrowLeft, Plus, Trash2 } from 'lucide-react';
import { fetchTemplate, renderTemplate, getSampleData } from '../services/api';
import toast from 'react-hot-toast';

const TemplateEditor = () => {
  const { templateId } = useParams();
  const navigate = useNavigate();
  const [template, setTemplate] = useState(null);
  const [sampleData, setSampleData] = useState({});
  const [selectedFormat, setSelectedFormat] = useState('email');
  const [selectedLocale, setSelectedLocale] = useState('en');
  const [templateContent, setTemplateContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [preview, setPreview] = useState(null);

  useEffect(() => {
    if (templateId) {
      loadTemplate();
    }
    loadSampleData();
  }, [templateId]);

  const loadTemplate = async () => {
    try {
      const data = await fetchTemplate(templateId);
      setTemplate(data);
      if (data.formats.length > 0) {
        setSelectedFormat(data.formats[0].format_type);
      }
      if (data.locales.length > 0) {
        setSelectedLocale(data.locales[0]);
      }
    } catch (error) {
      toast.error('Failed to load template');
    }
  };

  const loadSampleData = async () => {
    try {
      const data = await getSampleData();
      setSampleData(data);
    } catch (error) {
      toast.error('Failed to load sample data');
    } finally {
      setLoading(false);
    }
  };

  const renderPreview = async () => {
    if (!template || !sampleData[templateId]) return;

    try {
      const request = {
        template_id: templateId,
        format_type: selectedFormat,
        locale: selectedLocale,
        context: sampleData[templateId],
        test_mode: true
      };

      const result = await renderTemplate(request);
      setPreview(result);
    } catch (error) {
      toast.error('Failed to render preview');
    }
  };

  const handleSave = () => {
    toast.success('Template saved successfully!');
  };

  const handleTest = () => {
    navigate('/testing');
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
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/')}
          className="p-2 hover:bg-gray-100 rounded-md transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            {templateId ? `Edit ${template?.name}` : 'Create New Template'}
          </h1>
          <p className="text-gray-600">
            {templateId ? template?.description : 'Design your notification template'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Editor */}
        <div className="space-y-4">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Template Editor</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Template Name
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  defaultValue={template?.name || ''}
                  placeholder="Enter template name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="3"
                  defaultValue={template?.description || ''}
                  placeholder="Enter template description"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Template Content
                </label>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                  rows="15"
                  value={templateContent}
                  onChange={(e) => setTemplateContent(e.target.value)}
                  placeholder="Enter template content using Jinja2 syntax..."
                />
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={handleSave}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center space-x-2 transition-colors"
              >
                <Save className="w-4 h-4" />
                <span>Save Template</span>
              </button>
              
              <button
                onClick={renderPreview}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md flex items-center space-x-2 transition-colors"
              >
                <Eye className="w-4 h-4" />
                <span>Preview</span>
              </button>
              
              <button
                onClick={handleTest}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md flex items-center space-x-2 transition-colors"
              >
                <TestTube className="w-4 h-4" />
                <span>Test</span>
              </button>
            </div>
          </div>
        </div>

        {/* Preview */}
        <div className="space-y-4">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Live Preview</h3>
            
            {preview ? (
              <div className="space-y-4">
                {preview.success ? (
                  <div>
                    {preview.subject && (
                      <div className="mb-4 p-3 bg-gray-50 rounded-md">
                        <strong>Subject:</strong> {preview.subject}
                      </div>
                    )}
                    
                    <div className="prose max-w-none">
                      {selectedFormat === 'email' ? (
                        <div 
                          dangerouslySetInnerHTML={{ __html: preview.content }}
                          className="border rounded-lg p-4 bg-gray-50"
                        />
                      ) : (
                        <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded-lg border">
                          {preview.content}
                        </pre>
                      )}
                    </div>
                    
                    {preview.validation_warnings?.length > 0 && (
                      <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                        <h4 className="text-sm font-medium text-yellow-800 mb-2">
                          Warnings:
                        </h4>
                        <ul className="text-sm text-yellow-700 list-disc list-inside">
                          {preview.validation_warnings.map((warning, index) => (
                            <li key={index}>{warning}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="bg-red-50 border border-red-200 rounded-md p-4">
                    <h4 className="text-sm font-medium text-red-800 mb-2">
                      Render Error:
                    </h4>
                    <p className="text-sm text-red-700">{preview.error}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Eye className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p>Click "Preview" to see the rendered template</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TemplateEditor;
