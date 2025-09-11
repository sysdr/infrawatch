import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import Executions from './pages/Executions';
import Workers from './pages/Workers';
import CreateTask from './pages/CreateTask';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main style={{ padding: '20px' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tasks" element={<Tasks />} />
            <Route path="/tasks/create" element={<CreateTask />} />
            <Route path="/executions" element={<Executions />} />
            <Route path="/workers" element={<Workers />} />
          </Routes>
        </main>
        <ToastContainer />
      </div>
    </Router>
  );
}

export default App;
