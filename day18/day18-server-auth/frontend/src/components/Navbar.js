import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Key, Server, FileText } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/ssh-keys', icon: Key, label: 'SSH Keys' },
    { path: '/servers', icon: Server, label: 'Servers' },
    { path: '/logs', icon: FileText, label: 'Auth Logs' }
  ];

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <h1>Server Auth</h1>
      </div>
      <ul className="nav-menu">
        {navItems.map(({ path, icon: Icon, label }) => (
          <li key={path} className="nav-item">
            <Link 
              to={path} 
              className={`nav-link ${location.pathname === path ? 'active' : ''}`}
            >
              <Icon />
              {label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Navbar;
