import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, Plus } from 'lucide-react'

export default function MyTemplates() {
  return (
    <div style={{ minHeight: '100vh', background: '#f8f9fa' }}>
      <header style={{
        background: 'white',
        borderBottom: '1px solid #e0e0e0',
        padding: '1rem 0'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 2rem' }}>
          <Link to="/marketplace" style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            color: '#2563eb',
            textDecoration: 'none',
            fontWeight: '600'
          }}>
            <ArrowLeft size={20} />
            Back to Marketplace
          </Link>
        </div>
      </header>

      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
        <div style={{ textAlign: 'center', padding: '4rem', color: '#666' }}>
          <h2>My Templates</h2>
          <p>You haven't created any templates yet.</p>
          <Link to="/templates/new" style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.75rem 1.5rem',
            background: '#2563eb',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '6px',
            marginTop: '1rem',
            fontWeight: '500',
            transition: 'background 0.2s'
          }}>
            <Plus size={20} />
            Create Your First Template
          </Link>
        </div>
      </main>
    </div>
  )
}
