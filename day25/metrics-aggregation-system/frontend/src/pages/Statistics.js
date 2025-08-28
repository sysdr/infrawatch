import React, { useState } from 'react';
import { Calculator, TrendingUp, AlertTriangle } from 'lucide-react';
import axios from 'axios';

const Statistics = ({ isConnected }) => {
  const [inputValues, setInputValues] = useState('');
  const [operation, setOperation] = useState('all');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const calculateStatistics = async () => {
    if (!inputValues.trim()) return;
    
    setLoading(true);
    try {
      const response = await axios.get('/statistics/calculate', {
        params: {
          values: inputValues,
          operation: operation
        }
      });
      setResults(response.data);
    } catch (error) {
      console.error('Error calculating statistics:', error);
    }
    setLoading(false);
  };

  const StatCard = ({ title, value, subtitle }) => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <h4 className="text-sm font-medium text-gray-600 uppercase tracking-wider">{title}</h4>
      <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
      {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Statistical Analysis</h1>
        <p className="text-gray-600 mt-1">Compute advanced statistics for your data</p>
      </div>

      {/* Input Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Calculate Statistics</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Enter Values (comma-separated)
            </label>
            <textarea
              value={inputValues}
              onChange={(e) => setInputValues(e.target.value)}
              placeholder="10, 20, 30, 40, 50..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Operation
            </label>
            <select
              value={operation}
              onChange={(e) => setOperation(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Statistics</option>
              <option value="basic">Basic (Count, Sum, Average, Min, Max)</option>
              <option value="percentiles">Percentiles (P50, P95, P99)</option>
              <option value="advanced">Advanced (Std Dev, Variance, Rate of Change)</option>
              <option value="anomalies">Anomaly Detection</option>
            </select>
          </div>
          
          <button
            onClick={calculateStatistics}
            disabled={!inputValues.trim() || loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 flex items-center"
          >
            <Calculator className="h-4 w-4 mr-2" />
            {loading ? 'Calculating...' : 'Calculate'}
          </button>
        </div>
      </div>

      {/* Results Section */}
      {results && (
        <div className="space-y-6">
          {/* Basic Statistics */}
          {results.results.basic && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Basic Statistics</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                <StatCard title="Count" value={results.results.basic.count} />
                <StatCard title="Sum" value={results.results.basic.sum.toFixed(2)} />
                <StatCard title="Average" value={results.results.basic.average.toFixed(2)} />
                <StatCard title="Minimum" value={results.results.basic.min.toFixed(2)} />
                <StatCard title="Maximum" value={results.results.basic.max.toFixed(2)} />
              </div>
            </div>
          )}

          {/* Percentiles */}
          {results.results.percentiles && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Percentiles</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <StatCard title="P50 (Median)" value={results.results.percentiles.p50.toFixed(2)} />
                <StatCard title="P95" value={results.results.percentiles.p95.toFixed(2)} />
                <StatCard title="P99" value={results.results.percentiles.p99.toFixed(2)} />
              </div>
            </div>
          )}

          {/* Advanced Statistics */}
          {results.results.advanced && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Advanced Statistics</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <StatCard 
                  title="Standard Deviation" 
                  value={results.results.advanced.std_dev.toFixed(2)}
                  subtitle="Measure of data spread"
                />
                <StatCard 
                  title="Variance" 
                  value={results.results.advanced.variance.toFixed(2)}
                  subtitle="Square of std deviation"
                />
                <StatCard 
                  title="Rate of Change" 
                  value={`${results.results.advanced.rate_of_change.toFixed(2)}%`}
                  subtitle="First to last value change"
                />
              </div>
            </div>
          )}

          {/* Anomalies */}
          {results.results.anomalies && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <AlertTriangle className="h-5 w-5 mr-2 text-yellow-600" />
                Anomaly Detection
              </h3>
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                {results.results.anomalies.count > 0 ? (
                  <div>
                    <p className="text-sm text-gray-600 mb-3">
                      Found {results.results.anomalies.count} anomalies at positions: {' '}
                      {results.results.anomalies.indices.join(', ')}
                    </p>
                    <div className="space-y-2">
                      {results.results.anomalies.values.map((value, index) => (
                        <div key={index} className="flex items-center justify-between bg-yellow-50 px-3 py-2 rounded">
                          <span className="text-sm text-gray-700">
                            Position {results.results.anomalies.indices[index]}
                          </span>
                          <span className="text-sm font-medium text-yellow-800">{value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-green-600">No anomalies detected in the data.</p>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Statistics;
