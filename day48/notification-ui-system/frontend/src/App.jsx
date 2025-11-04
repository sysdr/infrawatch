import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import NotificationDashboard from './components/NotificationDashboard'
import './App.css'

function App() {
  return (
    <Router
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <div className="App">
        <Toaster position="top-right" />
        <Routes>
          <Route path="/" element={<NotificationDashboard />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
