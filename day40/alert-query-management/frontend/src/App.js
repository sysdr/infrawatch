import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import Header from './components/common/Header';
import Sidebar from './components/common/Sidebar';
import AlertDashboard from './pages/AlertDashboard';
import AlertSearch from './pages/AlertSearch';
import AlertStatistics from './pages/AlertStatistics';
import './styles/App.css';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <div className="app">
          <Header />
          <div className="app-body">
            <Sidebar />
            <main className="app-content">
              <Routes>
                <Route path="/" element={<AlertDashboard />} />
                <Route path="/search" element={<AlertSearch />} />
                <Route path="/statistics" element={<AlertStatistics />} />
              </Routes>
            </main>
          </div>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
