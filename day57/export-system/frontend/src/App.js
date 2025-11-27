import React, { useState, useEffect } from 'react';
import './App.css';
import ExportForm from './components/ExportForm';
import ExportList from './components/ExportList';
import { getExports, createExport, getExportStatus, downloadExport } from './services/api';

function App() {
  const [exports, setExports] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadExports();
    
    // Poll for updates every 3 seconds
    const interval = setInterval(loadExports, 3000);
    return () => clearInterval(interval);
  }, []);

  const loadExports = async () => {
    try {
      const data = await getExports();
      setExports(data);
    } catch (error) {
      console.error('Error loading exports:', error);
    }
  };

  const handleCreateExport = async (exportRequest) => {
    setLoading(true);
    try {
      await createExport(exportRequest);
      await loadExports();
    } catch (error) {
      console.error('Error creating export:', error);
      alert('Failed to create export');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (jobId) => {
    try {
      await downloadExport(jobId);
    } catch (error) {
      console.error('Error downloading export:', error);
      alert('Failed to download export');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>📊 Export System Dashboard</h1>
        <p>Multi-Format Data Export Management</p>
      </header>

      <main className="App-main">
        <div className="container">
          <ExportForm onSubmit={handleCreateExport} loading={loading} />
          <ExportList exports={exports} onDownload={handleDownload} />
        </div>
      </main>

      <footer className="App-footer">
        <p>Day 57: Export System Foundation - Built with React & FastAPI</p>
      </footer>
    </div>
  );
}

export default App;
