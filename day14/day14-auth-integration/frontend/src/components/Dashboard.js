import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { tokenManager } from '../services/tokenManager';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [tokenInfo, setTokenInfo] = useState(null);

  useEffect(() => {
    const token = tokenManager.getAccessToken();
    if (token) {
      setTokenInfo({
        hasToken: true,
        isExpired: tokenManager.isTokenExpired(token),
        shouldRefresh: tokenManager.shouldRefreshToken(token),
        expiration: tokenManager.getTokenExpiration(token)
      });
    }
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
      toast.success('Logged out successfully');
    } catch (error) {
      toast.error('Logout failed');
    }
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </div>

      <div className="dashboard-content">
        <div className="user-info-card">
          <h2>User Information</h2>
          <div className="user-details">
            <p><strong>Email:</strong> {user?.email}</p>
            <p><strong>Username:</strong> {user?.username}</p>
            <p><strong>Full Name:</strong> {user?.full_name || 'Not provided'}</p>
            <p><strong>Status:</strong> {user?.is_active ? 'Active' : 'Inactive'}</p>
          </div>
        </div>

        <div className="token-info-card">
          <h2>Authentication Status</h2>
          <div className="token-details">
            <p><strong>Has Token:</strong> {tokenInfo?.hasToken ? 'Yes' : 'No'}</p>
            <p><strong>Token Expired:</strong> {tokenInfo?.isExpired ? 'Yes' : 'No'}</p>
            <p><strong>Should Refresh:</strong> {tokenInfo?.shouldRefresh ? 'Yes' : 'No'}</p>
            {tokenInfo?.expiration && (
              <p><strong>Expires At:</strong> {new Date(tokenInfo.expiration).toLocaleString()}</p>
            )}
          </div>
        </div>

        <div className="integration-demo-card">
          <h2>Authentication Integration Demo</h2>
          <p>✅ Frontend connected to backend</p>
          <p>✅ Token-based authentication working</p>
          <p>✅ Automatic token refresh enabled</p>
          <p>✅ Session persistence across browser restarts</p>
          <p>✅ Protected routes functioning</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
