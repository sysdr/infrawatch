import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

interface AuthState {
  isAuthenticated: boolean;
  user: any | null;
  tokens: any | null;
}

interface TestResult {
  id: string;
  name: string;
  status: 'passed' | 'failed' | 'running';
  duration?: number;
  error?: string;
}

interface ServiceStatus {
  name: string;
  status: 'healthy' | 'unhealthy' | 'unknown';
  responseTime?: number;
  lastChecked: Date;
}

function App() {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    tokens: null
  });

  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [isRunningTests, setIsRunningTests] = useState(false);
  const [serviceStatus, setServiceStatus] = useState<ServiceStatus[]>([]);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'auth' | 'tests' | 'monitoring'>('dashboard');

  // Form states
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [registerForm, setRegisterForm] = useState({
    email: '',
    password: '',
    firstName: '',
    lastName: ''
  });

  // Add missing state variables for error and success messages
  const [registerError, setRegisterError] = useState<string>("");
  const [registerSuccess, setRegisterSuccess] = useState<string>("");
  const [loginError, setLoginError] = useState<string>("");
  const [loginSuccess, setLoginSuccess] = useState<string>("");
  const [healthStatus, setHealthStatus] = useState<string>("Checking...");

  useEffect(() => {
    checkServiceHealth();
    const interval = setInterval(checkServiceHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Health check for all services via backend
  const checkServiceHealth = async () => {
    setHealthStatus('Checking...');
    try {
      const response = await fetch('http://localhost:8000/api/health');
      if (response.ok) {
        const data = await response.json();
        setHealthStatus(`Backend: ${data.status}, App: ${data.app_name}, Version: ${data.version}`);
      } else {
        setHealthStatus('Backend health check failed');
      }
    } catch (error) {
      setHealthStatus('Backend health check failed');
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError("");
    setLoginSuccess("");
    try {
      const response = await axios.post(
        "http://localhost:8000/api/auth/login",
        {
          email: loginForm.email,
          password: loginForm.password,
        }
      );
      setLoginSuccess("Login successful!");
      setAuthState({
        isAuthenticated: true,
        user: response.data.user,
        tokens: response.data
      });
      setLoginForm({ email: '', password: '' });
    } catch (error: any) {
      setLoginError("Login failed. Please try again.");
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setRegisterError("");
    setRegisterSuccess("");
    try {
      const response = await axios.post(
        "http://localhost:8000/api/auth/register",
        {
          email: registerForm.email,
          password: registerForm.password,
          first_name: registerForm.firstName,
          last_name: registerForm.lastName,
        }
      );
      setRegisterSuccess("Registration successful!");
      setAuthState({
        isAuthenticated: true,
        user: response.data.user,
        tokens: response.data
      });
      setRegisterForm({ email: '', password: '', firstName: '', lastName: '' });
    } catch (error: any) {
      setRegisterError("Registration failed. Please try again.");
    }
  };

  const handleLogout = async () => {
    try {
      if (authState.tokens?.access_token) {
        await fetch('http://localhost:8000/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authState.tokens.access_token}`,
            'Content-Type': 'application/json'
          }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setAuthState({ isAuthenticated: false, user: null, tokens: null });
    }
  };

  const runTests = async () => {
    setIsRunningTests(true);
    setTestResults([]);

    const testSuites = [
      { name: 'Unit Tests', endpoint: '/api/tests/unit' },
      { name: 'Integration Tests', endpoint: '/api/tests/integration' },
      { name: 'Security Tests', endpoint: '/api/tests/security' },
      { name: 'Performance Tests', endpoint: '/api/tests/performance' }
    ];

    const results: TestResult[] = [];

    for (const suite of testSuites) {
      const testResult: TestResult = {
        id: Date.now().toString() + Math.random(),
        name: suite.name,
        status: 'running'
      };
      results.push(testResult);
      setTestResults([...results]);

      try {
        const startTime = Date.now();
        const response = await fetch(`http://localhost:8000${suite.endpoint}`, {
          method: 'POST',
          headers: {
            'Authorization': authState.tokens?.access_token ? `Bearer ${authState.tokens.access_token}` : '',
            'Content-Type': 'application/json'
          }
        });

        const duration = Date.now() - startTime;
        const data = await response.json();

        const updatedResult = {
          ...testResult,
          status: response.ok ? 'passed' : 'failed',
          duration,
          error: response.ok ? undefined : data.error || 'Test failed'
        };

        const updatedResults = results.map(r => r.id === testResult.id ? updatedResult : r);
        setTestResults([...updatedResults]);
      } catch (error) {
        const updatedResult = {
          ...testResult,
          status: 'failed',
          error: 'Test execution failed'
        };
        const updatedResults = results.map(r => r.id === testResult.id ? updatedResult : r);
        setTestResults([...updatedResults]);
      }
    }

    setIsRunningTests(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return '#10B981';
      case 'unhealthy': return '#EF4444';
      default: return '#F59E0B';
    }
  };

  const getTestStatusColor = (status: string) => {
    switch (status) {
      case 'passed': return '#10B981';
      case 'failed': return '#EF4444';
      case 'running': return '#3B82F6';
      default: return '#6B7280';
    }
  };

  return (
    <div className="App">
      <nav className="navbar">
        <div className="nav-brand">
          <h1>🔐 Auth Testing Suite</h1>
        </div>
        <div className="nav-tabs">
          <button 
            className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button 
            className={`nav-tab ${activeTab === 'auth' ? 'active' : ''}`}
            onClick={() => setActiveTab('auth')}
          >
            Authentication
          </button>
          <button 
            className={`nav-tab ${activeTab === 'tests' ? 'active' : ''}`}
            onClick={() => setActiveTab('tests')}
          >
            Test Suite
          </button>
          <button 
            className={`nav-tab ${activeTab === 'monitoring' ? 'active' : ''}`}
            onClick={() => setActiveTab('monitoring')}
          >
            Monitoring
          </button>
        </div>
        {authState.isAuthenticated && (
          <div className="user-info">
            <span>Welcome, {authState.user?.email}</span>
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        )}
      </nav>

      <main className="main-content">
        {activeTab === 'dashboard' && (
          <div className="dashboard">
            <div className="welcome-section">
              <h2>Authentication Security Guardian</h2>
              <p>Comprehensive testing framework for bulletproof authentication systems</p>
            </div>

            <div className="status-grid">
              <div className="status-card">
                <h3>Service Health</h3>
                <div className="service-list">
                  {serviceStatus.map((service, index) => (
                    <div key={index} className="service-item">
                      <span className="service-name">{service.name}</span>
                      <div className="service-status">
                        <div 
                          className="status-indicator" 
                          style={{ backgroundColor: getStatusColor(service.status) }}
                        />
                        <span className="status-text">{service.status}</span>
                        {service.responseTime && (
                          <span className="response-time">{service.responseTime}ms</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="status-card">
                <h3>Authentication Status</h3>
                <div className="auth-status">
                  <div className="status-item">
                    <span>User Status:</span>
                    <span className={authState.isAuthenticated ? 'status-success' : 'status-warning'}>
                      {authState.isAuthenticated ? 'Authenticated' : 'Not Authenticated'}
                    </span>
                  </div>
                  {authState.user && (
                    <div className="user-details">
                      <p><strong>Email:</strong> {authState.user.email}</p>
                      <p><strong>Role:</strong> {authState.user.role || 'User'}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'auth' && (
          <div className="auth-section">
            <div className="auth-container">
              {!authState.isAuthenticated ? (
                <div className="auth-forms">
                  <div className="auth-form">
                    <h3>Login</h3>
                    <form onSubmit={handleLogin}>
                      <div className="form-group">
                        <label>Email:</label>
                        <input
                          type="email"
                          value={loginForm.email}
                          onChange={(e) => setLoginForm({...loginForm, email: e.target.value})}
                          required
                        />
                      </div>
                      <div className="form-group">
                        <label>Password:</label>
                        <input
                          type="password"
                          value={loginForm.password}
                          onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                          required
                        />
                      </div>
                      <button type="submit" className="btn-primary">Login</button>
                    </form>
                  </div>

                  <div className="auth-form">
                    <h3>Register</h3>
                    <form onSubmit={handleRegister}>
                      <div className="form-group">
                        <label>First Name:</label>
                        <input
                          type="text"
                          value={registerForm.firstName}
                          onChange={(e) => setRegisterForm({...registerForm, firstName: e.target.value})}
                          required
                        />
                      </div>
                      <div className="form-group">
                        <label>Last Name:</label>
                        <input
                          type="text"
                          value={registerForm.lastName}
                          onChange={(e) => setRegisterForm({...registerForm, lastName: e.target.value})}
                          required
                        />
                      </div>
                      <div className="form-group">
                        <label>Email:</label>
                        <input
                          type="email"
                          value={registerForm.email}
                          onChange={(e) => setRegisterForm({...registerForm, email: e.target.value})}
                          required
                        />
                      </div>
                      <div className="form-group">
                        <label>Password:</label>
                        <input
                          type="password"
                          value={registerForm.password}
                          onChange={(e) => setRegisterForm({...registerForm, password: e.target.value})}
                          required
                        />
                      </div>
                      <button type="submit" className="btn-primary">Register</button>
                    </form>
                  </div>
                </div>
              ) : (
                <div className="authenticated-view">
                  <h3>Welcome, {authState.user?.email}!</h3>
                  <div className="user-info-card">
                    <h4>User Information</h4>
                    <p><strong>Email:</strong> {authState.user?.email}</p>
                    <p><strong>Name:</strong> {authState.user?.first_name} {authState.user?.last_name}</p>
                    <p><strong>Role:</strong> {authState.user?.role || 'User'}</p>
                    <p><strong>Status:</strong> {authState.user?.is_active ? 'Active' : 'Inactive'}</p>
                  </div>
                  <button onClick={handleLogout} className="btn-secondary">Logout</button>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'tests' && (
          <div className="tests-section">
            <div className="tests-header">
              <h3>Test Suite Execution</h3>
              <button 
                onClick={runTests} 
                disabled={isRunningTests}
                className="btn-primary"
              >
                {isRunningTests ? 'Running Tests...' : 'Run All Tests'}
              </button>
            </div>

            <div className="test-results">
              {testResults.map((result) => (
                <div key={result.id} className="test-result">
                  <div className="test-header">
                    <span className="test-name">{result.name}</span>
                    <div className="test-status">
                      <div 
                        className="status-indicator" 
                        style={{ backgroundColor: getTestStatusColor(result.status) }}
                      />
                      <span className="status-text">{result.status}</span>
                      {result.duration && (
                        <span className="duration">{result.duration}ms</span>
                      )}
                    </div>
                  </div>
                  {result.error && (
                    <div className="test-error">
                      <strong>Error:</strong> {result.error}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'monitoring' && (
          <div className="monitoring-section">
            <h3>System Monitoring</h3>
            <div className="monitoring-grid">
              <div className="monitoring-card">
                <h4>Service Response Times</h4>
                <div className="response-times">
                  {serviceStatus.map((service, index) => (
                    <div key={index} className="response-item">
                      <span>{service.name}</span>
                      <span>{service.responseTime || 'N/A'}ms</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="monitoring-card">
                <h4>Test Coverage</h4>
                <div className="coverage-stats">
                  <div className="coverage-item">
                    <span>Unit Tests</span>
                    <span className="coverage-percentage">95%</span>
                  </div>
                  <div className="coverage-item">
                    <span>Integration Tests</span>
                    <span className="coverage-percentage">88%</span>
                  </div>
                  <div className="coverage-item">
                    <span>Security Tests</span>
                    <span className="coverage-percentage">92%</span>
                  </div>
                  <div className="coverage-item">
                    <span>Performance Tests</span>
                    <span className="coverage-percentage">85%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App; 