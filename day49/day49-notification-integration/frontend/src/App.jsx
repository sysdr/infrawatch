import React, { useState } from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Alerts from './pages/Alerts'
import Notifications from './pages/Notifications'
import Preferences from './pages/Preferences'
import Escalations from './pages/Escalations'
import { Bell, AlertTriangle, Settings, TrendingUp } from 'lucide-react'

function App() {
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true
      }}
    >
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex space-x-8">
                <Link to="/" className="flex items-center px-3 py-2 text-gray-900 hover:text-blue-600">
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Dashboard
                </Link>
                <Link to="/alerts" className="flex items-center px-3 py-2 text-gray-700 hover:text-blue-600">
                  <AlertTriangle className="h-5 w-5 mr-2" />
                  Alerts
                </Link>
                <Link to="/notifications" className="flex items-center px-3 py-2 text-gray-700 hover:text-blue-600">
                  <Bell className="h-5 w-5 mr-2" />
                  Notifications
                </Link>
                <Link to="/preferences" className="flex items-center px-3 py-2 text-gray-700 hover:text-blue-600">
                  <Settings className="h-5 w-5 mr-2" />
                  Preferences
                </Link>
                <Link to="/escalations" className="flex items-center px-3 py-2 text-gray-700 hover:text-blue-600">
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Escalations
                </Link>
              </div>
            </div>
          </div>
        </nav>
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/notifications" element={<Notifications />} />
            <Route path="/preferences" element={<Preferences />} />
            <Route path="/escalations" element={<Escalations />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
