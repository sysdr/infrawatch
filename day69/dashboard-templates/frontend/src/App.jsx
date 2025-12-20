import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Marketplace from './pages/Marketplace'
import TemplateEditor from './pages/TemplateEditor'
import TemplateDetail from './pages/TemplateDetail'
import MyTemplates from './pages/MyTemplates'
import Dashboard from './pages/Dashboard'

function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        <Route path="/" element={<Navigate to="/marketplace" replace />} />
        <Route path="/marketplace" element={<Marketplace />} />
        <Route path="/templates/new" element={<TemplateEditor />} />
        <Route path="/templates/:id" element={<TemplateDetail />} />
        <Route path="/templates/:id/edit" element={<TemplateEditor />} />
        <Route path="/my-templates" element={<MyTemplates />} />
        <Route path="/dashboards" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
