import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Dashboard from './pages/Dashboard';
import SSHKeys from './pages/SSHKeys';
import Servers from './pages/Servers';
import AuthLogs from './pages/AuthLogs';
import Navbar from './components/Navbar';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/ssh-keys" element={<SSHKeys />} />
            <Route path="/servers" element={<Servers />} />
            <Route path="/logs" element={<AuthLogs />} />
          </Routes>
        </main>
        <Toaster position="top-right" />
      </div>
    </Router>
  );
}

export default App;
