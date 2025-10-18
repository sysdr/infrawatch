import React, { useState } from 'react';
import axios from 'axios';
import { TestTube, Mail, MessageSquare, Smartphone, Webhook, Bell, Play, CheckCircle, XCircle } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

const ChannelTester = () => {
  const [testResults, setTestResults] = useState({});
  const [testing, setTesting] = useState({});

  const channels = [
    { 
      id: 'email', 
      name: 'Email', 
      icon: Mail, 
      placeholder: 'test@example.com',
      description: 'Send test email notification'
    },
    { 
      id: 'sms', 
      name: 'SMS', 
      icon: Smartphone, 
      placeholder: '+1234567890',
      description: 'Send test SMS message'
    },
    { 
      id: 'slack', 
      name: 'Slack', 
      icon: MessageSquare, 
      placeholder: '#general',
      description: 'Send test Slack message'
    },
    { 
      id: 'webhook', 
      name: 'Webhook', 
      icon: Webhook, 
      placeholder: 'https://api.example.com/webhook',
      description: 'Send test webhook notification'
    },
    { 
      id: 'push', 
      name: 'Push', 
      icon: Bell, 
      placeholder: 'device_token_demo',
      description: 'Send test push notification'
    }
  ];

  const testChannel = async (channel) => {
    setTesting(prev => ({ ...prev, [channel.id]: true }));
    
    try {
      const response = await axios.post(`${API_BASE}/channels/test`, {
        channel: channel.id,
        recipient: channel.placeholder,
        test_message: `Test notification from ${channel.name} channel at ${new Date().toLocaleTimeString()}`
      });
      
      setTestResults(prev => ({
        ...prev,
        [channel.id]: {
          success: true,
          timestamp: new Date().toISOString(),
          result: response.data.result
        }
      }));
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        [channel.id]: {
          success: false,
          timestamp: new Date().toISOString(),
          error: error.response?.data?.detail?.errors || [error.message]
        }
      }));
    } finally {
      setTesting(prev => ({ ...prev, [channel.id]: false }));
    }
  };

  const runAllTests = async () => {
    for (const channel of channels) {
      await testChannel(channel);
      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  };

  const getTestStatus = (channelId) => {
    const result = testResults[channelId];
    if (!result) return null;
    return result.success ? 'success' : 'error';
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Channel Testing</h2>
          <p className="mt-1 text-sm text-gray-500">
            Test all notification channels to ensure they're working correctly
          </p>
        </div>
        <button
          onClick={runAllTests}
          disabled={Object.values(testing).some(Boolean)}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <TestTube className="h-4 w-4 mr-2" />
          Test All Channels
        </button>
      </div>

      {/* Test Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {channels.map((channel) => {
          const Icon = channel.icon;
          const isLoading = testing[channel.id];
          const testStatus = getTestStatus(channel.id);
          const result = testResults[channel.id];
          
          return (
            <div key={channel.id} className="bg-white shadow rounded-lg overflow-hidden">
              <div className="p-6">
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <Icon className="h-8 w-8 text-gray-600" />
                    </div>
                    <div className="ml-4">
                      <h3 className="text-lg font-medium text-gray-900">
                        {channel.name}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {channel.description}
                      </p>
                    </div>
                  </div>
                  
                  {/* Status Indicator */}
                  {testStatus && (
                    <div className="flex-shrink-0">
                      {testStatus === 'success' ? (
                        <CheckCircle className="h-6 w-6 text-green-500" />
                      ) : (
                        <XCircle className="h-6 w-6 text-red-500" />
                      )}
                    </div>
                  )}
                </div>

                {/* Test Configuration */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Test Recipient
                  </label>
                  <input
                    type="text"
                    value={channel.placeholder}
                    readOnly
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-gray-50 text-gray-600"
                  />
                </div>

                {/* Test Button */}
                <button
                  onClick={() => testChannel(channel)}
                  disabled={isLoading}
                  className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  ) : (
                    <Play className="h-4 w-4 mr-2" />
                  )}
                  {isLoading ? 'Testing...' : 'Run Test'}
                </button>

                {/* Test Results */}
                {result && (
                  <div className={`mt-4 p-3 rounded-md ${
                    result.success 
                      ? 'bg-green-50 border border-green-200' 
                      : 'bg-red-50 border border-red-200'
                  }`}>
                    <div className="flex items-start">
                      <div className={`flex-shrink-0 ${
                        result.success ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {result.success ? (
                          <CheckCircle className="h-5 w-5" />
                        ) : (
                          <XCircle className="h-5 w-5" />
                        )}
                      </div>
                      <div className="ml-3 flex-1">
                        <h4 className={`text-sm font-medium ${
                          result.success ? 'text-green-800' : 'text-red-800'
                        }`}>
                          {result.success ? 'Test Passed' : 'Test Failed'}
                        </h4>
                        <div className={`mt-1 text-xs ${
                          result.success ? 'text-green-600' : 'text-red-600'
                        }`}>
                          <p>Tested at {formatTimestamp(result.timestamp)}</p>
                          
                          {result.success && result.result && (
                            <div className="mt-2">
                              <p>Message ID: {result.result.message_id}</p>
                              <p>Provider: {result.result.provider}</p>
                              {result.result.cost !== undefined && (
                                <p>Cost: ${result.result.cost}</p>
                              )}
                            </div>
                          )}
                          
                          {!result.success && result.error && (
                            <div className="mt-2">
                              <p className="font-medium">Errors:</p>
                              <ul className="list-disc list-inside">
                                {Array.isArray(result.error) 
                                  ? result.error.map((err, idx) => (
                                      <li key={idx}>{err}</li>
                                    ))
                                  : <li>{result.error}</li>
                                }
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Test Summary */}
      {Object.keys(testResults).length > 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Test Summary</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900">
                  {Object.keys(testResults).length}
                </div>
                <div className="text-sm text-gray-500">Total Tests Run</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">
                  {Object.values(testResults).filter(r => r.success).length}
                </div>
                <div className="text-sm text-gray-500">Passed</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-red-600">
                  {Object.values(testResults).filter(r => !r.success).length}
                </div>
                <div className="text-sm text-gray-500">Failed</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChannelTester;
