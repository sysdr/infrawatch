import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Sidebar = () => {
  const location = useLocation();
  
  const isActive = (path) => location.pathname === path;
  
  return (
    <aside className="sidebar">
      <nav>
        <ul className="sidebar-nav">
          <li>
            <Link 
              to="/" 
              className={isActive('/') ? 'active' : ''}
            >
              Dashboard
            </Link>
          </li>
          <li>
            <Link 
              to="/search" 
              className={isActive('/search') ? 'active' : ''}
            >
              Search
            </Link>
          </li>
          <li>
            <Link 
              to="/statistics" 
              className={isActive('/statistics') ? 'active' : ''}
            >
              Statistics
            </Link>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
