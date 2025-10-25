import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Eye, Mail, MessageSquare, Bell, Slack, Globe } from 'lucide-react';
import { fetchTemplate, renderTemplate, getSampleData } from '../services/api';
import toast from 'react-hot-toast';

const TemplatePreview = () => {
  const { templateId } = useParams();
  const [template, setTemplate] = useState(null);
  const [sampleData, setSampleData] = useState({});
  const [selectedFormat, setSelectedFormat] = useState('email');
  const [selectedLocale, setSelectedLocale] = useState('en');
  const [renderedContent, setRenderedContent] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTemplate();
    loadSampleData();
  }, [templateId]);

  useEffect(() => {
    if (template && sampleData[templateId]) {
      renderPreview();
    }
  }, [template, sampleData, selectedFormat, selectedLocale]);

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
      setRenderedContent(result);
    } catch (error) {
      toast.error('Failed to render preview');
    }
  };

  const getFormatIcon = (format) => {
    const icons = { email: Mail, sms: MessageSquare, push: Bell, slack: Slack };
    return icons[format] || Mail;
  };

  if (loading || !template) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Eye className="w-8 h-8 text-blue-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{template.name}</h1>
          <p className="text-gray-600">{template.description}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Controls */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white p-4 rounded-lg shadow-md">
            <h3 className="font-semibold text-gray-900 mb-3">Format</h3>
            <div className="space-y-2">
              {template.formats.map((format) => {
                const Icon = getFormatIcon(format.format_type);
                return (
                  <button
                    key={format.format_type}
                    onClick={() => setSelectedFormat(format.format_type)}
                    className={`w-full flex items-center space-x-2 p-2 rounded-md text-left transition-colors ${
                      selectedFormat === format.format_type
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="capitalize">{format.format_type}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow-md">
            <h3 className="font-semibold text-gray-900 mb-3">Language</h3>
            <div className="space-y-2">
              {template.locales.map((locale) => (
                <button
                  key={locale}
                  onClick={() => setSelectedLocale(locale)}
                  className={`w-full flex items-center space-x-2 p-2 rounded-md text-left transition-colors ${
                    selectedLocale === locale
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <Globe className="w-4 h-4" />
                  <span className="uppercase">{locale}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Preview */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="bg-gray-50 px-6 py-4 border-b">
              <h3 className="font-semibold text-gray-900">Preview</h3>
              {renderedContent?.subject && (
                <p className="text-sm text-gray-600 mt-1">
                  <strong>Subject:</strong> {renderedContent.subject}
                </p>
              )}
            </div>
            
            <div className="p-6">
              {renderedContent ? (
                <div>
                  {renderedContent.success ? (
                    <div className="space-y-4">
                      <div className="prose max-w-none">
                        {selectedFormat === 'email' ? (
                          <div 
                            dangerouslySetInnerHTML={{ __html: renderedContent.content }}
                            className="border rounded-lg p-4 bg-gray-50"
                          />
                        ) : (
                          <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded-lg border">
                            {renderedContent.content}
                          </pre>
                        )}
                      </div>
                      
                      {renderedContent.validation_warnings?.length > 0 && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                          <h4 className="text-sm font-medium text-yellow-800 mb-2">
                            Warnings:
                          </h4>
                          <ul className="text-sm text-yellow-700 list-disc list-inside">
                            {renderedContent.validation_warnings.map((warning, index) => (
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
                      <p className="text-sm text-red-700">{renderedContent.error}</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Eye className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p>Select a format and language to preview the template</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TemplatePreview;
