import React, { useState } from 'react';
import { useQuery, useMutation } from 'react-query';
import { Play, CheckCircle, XCircle } from 'lucide-react';
import { testingAPI, rulesAPI } from '../services/api';

const Testing = () => {
  const [selectedRule, setSelectedRule] = useState('');
  const [testData, setTestData] = useState('');
  const [expectedResults, setExpectedResults] = useState('');
  const [testResults, setTestResults] = useState(null);
  
  const { data: rules = [] } = useQuery('rules', () => 
    rulesAPI.getRules().then(res => res.data)
  );
  
  const { data: exampleData } = useQuery('exampleData', () =>
    testingAPI.getExampleData().then(res => res.data)
  );
  
  const testMutation = useMutation(testingAPI.testRule, {
    onSuccess: (data) => {
      setTestResults(data.data);
    },
  });
  
  const handleTest = () => {
    try {
      const rule = rules.find(r => r.id === parseInt(selectedRule));
      if (!rule) {
        alert('Please select a rule');
        return;
      }
      
      const parsedTestData = JSON.parse(testData);
      const parsedExpectedResults = JSON.parse(expectedResults);
      
      if (!Array.isArray(parsedTestData) || !Array.isArray(parsedExpectedResults)) {
        alert('Test data and expected results must be arrays');
        return;
      }
      
      testMutation.mutate({
        rule_id: rule.id,
        test_data: parsedTestData,
        expected_results: parsedExpectedResults
      });
    } catch (error) {
      alert('Invalid JSON in test data or expected results');
    }
  };
  
  const loadExample = (exampleKey) => {
    if (!exampleData || !exampleData[exampleKey]) return;
    
    const example = exampleData[exampleKey];
    setTestData(JSON.stringify(example.test_data, null, 2));
    setExpectedResults(JSON.stringify(example.expected_results, null, 2));
  };
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-wp-text">Rule Testing</h1>
        <p className="mt-2 text-wp-text-light">Test your alert rules against sample data</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <div className="wp-card p-6">
            <h3 className="text-lg font-semibold text-wp-text mb-4">Test Configuration</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-wp-text mb-1">
                  Select Rule
                </label>
                <select
                  value={selectedRule}
                  onChange={(e) => setSelectedRule(e.target.value)}
                  className="wp-input"
                >
                  <option value="">Choose a rule to test</option>
                  {rules.map((rule) => (
                    <option key={rule.id} value={rule.id}>
                      {rule.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-wp-text mb-1">
                  Test Data (JSON Array)
                </label>
                <textarea
                  value={testData}
                  onChange={(e) => setTestData(e.target.value)}
                  className="wp-input font-mono"
                  rows={8}
                  placeholder='[{"cpu_usage_percent": 45.2}, {"cpu_usage_percent": 89.7}]'
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-wp-text mb-1">
                  Expected Results (JSON Array)
                </label>
                <textarea
                  value={expectedResults}
                  onChange={(e) => setExpectedResults(e.target.value)}
                  className="wp-input font-mono"
                  rows={3}
                  placeholder='[false, true]'
                />
              </div>
              
              <button
                onClick={handleTest}
                disabled={testMutation.isLoading}
                className="w-full wp-button"
              >
                <Play size={16} className="mr-2" />
                {testMutation.isLoading ? 'Testing...' : 'Run Test'}
              </button>
            </div>
          </div>
          
          <div className="wp-card p-6">
            <h3 className="text-lg font-semibold text-wp-text mb-4">Example Test Data</h3>
            <div className="space-y-2">
              {exampleData && Object.keys(exampleData).map((key) => (
                <button
                  key={key}
                  onClick={() => loadExample(key)}
                  className="w-full text-left wp-button-secondary"
                >
                  {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </button>
              ))}
            </div>
          </div>
        </div>
        
        <div className="wp-card p-6">
          <h3 className="text-lg font-semibold text-wp-text mb-4">Test Results</h3>
          
          {testResults ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-wp-gray rounded-lg">
                <div>
                  <p className="font-medium">Overall Result</p>
                  <p className="text-sm text-wp-text-light">
                    {testResults.passed_tests}/{testResults.total_tests} tests passed
                  </p>
                </div>
                <div className="flex items-center">
                  {testResults.overall_passed ? (
                    <CheckCircle className="text-green-600" size={24} />
                  ) : (
                    <XCircle className="text-red-600" size={24} />
                  )}
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-wp-text mb-2">Test Cases</h4>
                <div className="space-y-2">
                  {testResults.results.map((result, index) => (
                    <div
                      key={index}
                      className={`p-3 rounded-lg border ${
                        result.passed 
                          ? 'bg-green-50 border-green-200' 
                          : 'bg-red-50 border-red-200'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium">Test Case {result.test_case}</span>
                        {result.passed ? (
                          <CheckCircle className="text-green-600" size={16} />
                        ) : (
                          <XCircle className="text-red-600" size={16} />
                        )}
                      </div>
                      <div className="text-sm text-wp-text-light mt-1">
                        Expected: {result.expected.toString()}, 
                        Actual: {result.actual?.toString() || 'Error'}
                      </div>
                      {result.error && (
                        <div className="text-sm text-red-600 mt-1">
                          Error: {result.error}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="text-sm text-wp-text-light">
                Execution time: {testResults.execution_time_ms?.toFixed(2)}ms
              </div>
            </div>
          ) : (
            <p className="text-wp-text-light text-center py-8">
              Run a test to see results here
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Testing;
