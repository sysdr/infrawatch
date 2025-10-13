import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
  const location = useLocation();

  return (
    <nav style={{
      background: '#1e293b',
      padding: '15px 20px',
      color: 'white'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        gap: '30px'
      }}>
        <h2>Alert Management</h2>
        <div style={{ display: 'flex', gap: '20px' }}>
          <Link 
            to="/" 
            style={{
              color: location.pathname === '/' ? '#60a5fa' : '#cbd5e1',
              textDecoration: 'none'
            }}
          >
            Dashboard
          </Link>
          <Link 
            to="/rules" 
            style={{
              color: location.pathname === '/rules' ? '#60a5fa' : '#cbd5e1',
              textDecoration: 'none'
            }}
          >
            Rules
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
