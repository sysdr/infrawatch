import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import TemplateEditor from './components/TemplateEditor';
import TemplatePreview from './components/TemplatePreview';
import TestingPanel from './components/TestingPanel';

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="App min-h-screen bg-gray-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/editor/:templateId?" element={<TemplateEditor />} />
            <Route path="/preview/:templateId" element={<TemplatePreview />} />
            <Route path="/testing" element={<TestingPanel />} />
          </Routes>
        </main>
        <Toaster position="top-right" />
      </div>
    </Router>
  );
}

export default App;
