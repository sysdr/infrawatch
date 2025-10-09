import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="header-logo">
          🚨 Alert Management
        </Link>
        <nav className="header-nav">
          <Link to="/">Dashboard</Link>
          <Link to="/search">Search</Link>
          <Link to="/statistics">Statistics</Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;
