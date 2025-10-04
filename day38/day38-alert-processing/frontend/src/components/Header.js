import React from 'react';

function Header({ onMenuClick }) {
  return (
    <header className="header">
      <div className="header-left">
        <button className="menu-button" onClick={onMenuClick}>
          ☰
        </button>
        <h1 className="app-title">Alert Processing Pipeline</h1>
      </div>
      <div className="header-right">
        <div className="user-info">
          <span>Admin User</span>
        </div>
      </div>
    </header>
  );
}

export default Header;
