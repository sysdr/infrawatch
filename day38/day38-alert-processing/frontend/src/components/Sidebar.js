import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Sidebar({ isOpen }) {
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/alerts', label: 'Alerts', icon: '🚨' },
    { path: '/stats', label: 'Statistics', icon: '📈' }
  ];

  return (
    <nav className={`sidebar ${!isOpen ? 'closed' : ''}`}>
      <ul className="nav-list">
        {navItems.map(item => (
          <li key={item.path} className="nav-item">
            <Link 
              to={item.path}
              className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export default Sidebar;
