import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import VersionsOverview from './pages/VersionsOverview';
import MigrationGuide from './pages/MigrationGuide';
import ApiExplorer from './pages/ApiExplorer';
import Analytics from './pages/Analytics';
import './App.css';

function Sidebar() {
  const nav = [
    {to:'/',label:'Version Overview',icon:'⚡'},
    {to:'/migration',label:'Migration Guide',icon:'🔀'},
    {to:'/explorer',label:'API Explorer',icon:'🧪'},
    {to:'/analytics',label:'Analytics',icon:'📊'},
  ];
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">V</div>
        <div><div className="brand-name">VersionCtrl</div><div className="brand-sub">API Management</div></div>
      </div>
      <nav className="sidebar-nav">
        {nav.map(n => (
          <NavLink key={n.to} to={n.to} end={n.to==='/'} className={({isActive})=>`nav-item ${isActive?'active':''}`}>
            <span className="nav-icon">{n.icon}</span><span>{n.label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div className="version-badge stable">v2 Active</div>
        <div className="version-badge deprecated">v1 Deprecated</div>
      </div>
    </aside>
  );
}

export default function App() {
  return (
    <Router>
      <div className="app-shell">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<VersionsOverview />} />
            <Route path="/migration" element={<MigrationGuide />} />
            <Route path="/explorer" element={<ApiExplorer />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
