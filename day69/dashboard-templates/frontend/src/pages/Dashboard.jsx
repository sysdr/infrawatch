import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, TrendingUp } from 'lucide-react'
import { dashboardApi } from '../services/api'

export default function Dashboard() {
  const [dashboards, setDashboards] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboards()
  }, [])

  const loadDashboards = async () => {
    try {
      const response = await dashboardApi.list()
      setDashboards(response.data)
    } catch (error) {
      console.error('Failed to load dashboards:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f8f9fa' }}>
      <header style={{
        background: 'white',
        borderBottom: '1px solid #e0e0e0',
        padding: '1rem 0'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
          <h1 style={{ margin: 0, fontSize: '1.5rem' }}>My Dashboards</h1>
        </div>
      </header>

      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '4rem' }}>Loading...</div>
        ) : dashboards.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '4rem', color: '#666' }}>
            <TrendingUp size={48} style={{ marginBottom: '1rem' }} />
            <h2>No Dashboards Yet</h2>
            <p>Create a dashboard from a template to get started.</p>
            <Link to="/marketplace" style={{
              display: 'inline-block',
              padding: '0.75rem 1.5rem',
              background: '#2563eb',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '6px',
              marginTop: '1rem',
              fontWeight: '500',
              transition: 'background 0.2s'
            }}>
              Browse Templates
            </Link>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
            {dashboards.map(dashboard => (
              <div key={dashboard.id} style={{
                background: 'white',
                borderRadius: '12px',
                padding: '1.5rem',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                border: '1px solid #e5e7eb',
                transition: 'box-shadow 0.2s, transform 0.2s',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.12)'
                e.currentTarget.style.transform = 'translateY(-2px)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)'
                e.currentTarget.style.transform = 'translateY(0)'
              }}>
                <h3 style={{ marginBottom: '0.5rem' }}>{dashboard.name}</h3>
                <p style={{ color: '#666', fontSize: '0.875rem', marginBottom: '1rem' }}>
                  Created: {new Date(dashboard.created_at).toLocaleDateString()}
                </p>
                {dashboard.template_id && (
                  <div style={{
                    padding: '0.5rem 0.75rem',
                    background: '#eff6ff',
                    borderRadius: '6px',
                    fontSize: '0.875rem',
                    color: '#1e40af',
                    fontWeight: '500'
                  }}>
                    From template v{dashboard.template_version}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
