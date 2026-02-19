import React, { useState } from 'react'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import Pipeline from './components/Pipeline'
import MLPanel from './components/ML'
import CorrelationPanel from './components/Correlation'
import ReportsPanel from './components/Reports'

const VIEWS = {
  dashboard:   { label: 'Overview',      icon: '◈', component: Dashboard },
  pipeline:    { label: 'Pipeline',      icon: '⟳', component: Pipeline },
  ml:          { label: 'ML Models',     icon: '⬡', component: MLPanel },
  correlation: { label: 'Correlations',  icon: '⊞', component: CorrelationPanel },
  reports:     { label: 'Reports',       icon: '◧', component: ReportsPanel },
}

export default function App() {
  const [active, setActive] = useState('dashboard')
  const View = VIEWS[active].component

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0f1117' }}>
      <Sidebar views={VIEWS} active={active} onSelect={setActive} />
      <main style={{ flex: 1, overflow: 'auto', padding: '28px 32px' }}>
        <View />
      </main>
    </div>
  )
}
