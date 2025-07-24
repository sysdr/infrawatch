import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ServerDashboard from './pages/ServerDashboard';
import ServerDetail from './pages/ServerDetail';
import Layout from './components/Layout';
import './styles/global.css';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<ServerDashboard />} />
          <Route path="/servers/:id" element={<ServerDetail />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
