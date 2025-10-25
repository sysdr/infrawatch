import React, { useState, useEffect } from 'react';
import { TestTube, Play, CheckCircle, XCircle, AlertTriangle, RefreshCw } from 'lucide-react';
import { getSampleData, testRenderAll, fetchTemplates } from '../services/api';
import toast from 'react-hot-toast';

const TestingPanel = () => {
  const [templates, setTemplates] = useState([]);
  const [sampleData, setSampleData] = useState({});
  const [testResults, setTestResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [templatesData, sampleDataResult] = await Promise.all([
        fetchTemplates(),
        getSampleData()
      ]);
      setTemplates(templatesData);
      setSampleData(sampleDataResult);
    } catch (error) {
      toast.error('Failed to load test data');
    } finally {
      setLoading(false);
    }
  };

  const runAllTests = async () => {
    setTesting(true);
    try {
      const results = await testRenderAll();
      setTestResults(results);
      toast.success('All tests completed successfully!');
    } catch (error) {
      toast.error('Tests failed to run');
    } finally {
      setTesting(false);
    }
  };

  const getStatusIcon = (success) => {
    return success ? (
      <CheckCircle className="w-5 h-5 text-green-500" />
    ) : (
      <XCircle className="w-5 h-5 text-red-500" />
    );
  };

  const getStatusColor = (success) => {
    return success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200';
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
        <TestTube className="w-8 h-8 text-blue-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Template Testing</h1>
          <p className="text-gray-600">Test all templates with sample data</p>
        </div>
      </div>

      {/* Test Controls */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Run Tests</h3>
            <p className="text-gray-600">
              Test all {templates.length} templates across all formats and locales
            </p>
          </div>
          
          <button
            onClick={runAllTests}
            disabled={testing}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg flex items-center space-x-2 transition-colors"
          >
            {testing ? (
              <RefreshCw className="w-5 h-5 animate-spin" />
            ) : (
              <Play className="w-5 h-5" />
            )}
            <span>{testing ? 'Running Tests...' : 'Run All Tests'}</span>
          </button>
        </div>
      </div>

      {/* Test Results */}
      {testResults && (
        <div className="space-y-4">
          <h3 className="text-xl font-semibold text-gray-900">Test Results</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-white p-4 rounded-lg shadow-md">
              <div className="flex items-center">
                <CheckCircle className="w-8 h-8 text-green-600" />
                <div className="ml-4">
                  <h4 className="text-lg font-semibold text-gray-900">
                    {testResults.test_results.filter(r => r.success).length}
                  </h4>
                  <p className="text-gray-600">Successful</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow-md">
              <div className="flex items-center">
                <XCircle className="w-8 h-8 text-red-600" />
                <div className="ml-4">
                  <h4 className="text-lg font-semibold text-gray-900">
                    {testResults.test_results.filter(r => !r.success).length}
                  </h4>
                  <p className="text-gray-600">Failed</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow-md">
              <div className="flex items-center">
                <TestTube className="w-8 h-8 text-blue-600" />
                <div className="ml-4">
                  <h4 className="text-lg font-semibold text-gray-900">
                    {testResults.test_results.length}
                  </h4>
                  <p className="text-gray-600">Total Tests</p>
                </div>
              </div>
            </div>
          </div>

          {/* Detailed Results */}
          <div className="space-y-4">
            {testResults.test_results.map((result, index) => (
              <div
                key={index}
                className={`border rounded-lg p-4 ${getStatusColor(result.success)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    {getStatusIcon(result.success)}
                    <div>
                      <h4 className="font-semibold text-gray-900">
                        {result.template_id} - {result.format} ({result.locale})
                      </h4>
                      <p className="text-sm text-gray-600">
                        Content Length: {result.content_length} characters
                      </p>
                      
                      {result.error && (
                        <p className="text-sm text-red-700 mt-1">
                          <strong>Error:</strong> {result.error}
                        </p>
                      )}
                      
                      {result.warnings && result.warnings.length > 0 && (
                        <div className="mt-2">
                          <p className="text-sm text-yellow-700 font-medium">Warnings:</p>
                          <ul className="text-sm text-yellow-700 list-disc list-inside ml-4">
                            {result.warnings.map((warning, wIndex) => (
                              <li key={wIndex}>{warning}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      result.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {result.success ? 'PASS' : 'FAIL'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sample Data Preview */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Sample Data</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(sampleData).map(([templateId, data]) => (
            <div key={templateId} className="border rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-2">{templateId}</h4>
              <pre className="text-sm text-gray-600 bg-gray-50 p-3 rounded overflow-x-auto">
                {JSON.stringify(data, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TestingPanel;
