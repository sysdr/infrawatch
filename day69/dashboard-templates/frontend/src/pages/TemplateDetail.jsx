import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Star, Download, Calendar, User, Tag, Code } from 'lucide-react'
import { templateApi } from '../services/api'

export default function TemplateDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [template, setTemplate] = useState(null)
  const [versions, setVersions] = useState([])
  const [showInstall, setShowInstall] = useState(false)
  const [dashboardName, setDashboardName] = useState('')
  const [variableValues, setVariableValues] = useState({})
  const [rating, setRating] = useState(5)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTemplate()
  }, [id])

  const loadTemplate = async () => {
    try {
      const [templateRes, versionsRes] = await Promise.all([
        templateApi.get(id),
        templateApi.getVersions(id)
      ])
      setTemplate(templateRes.data)
      setVersions(versionsRes.data)
      
      // Initialize variable values with defaults
      const defaults = {}
      if (templateRes.data.variables && Array.isArray(templateRes.data.variables)) {
        templateRes.data.variables.forEach(v => {
          defaults[v.name] = v.default_value || ''
        })
      }
      setVariableValues(defaults)
    } catch (error) {
      console.error('Failed to load template:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleInstall = async () => {
    // Check if template is published
    if (!template || template.status !== 'published') {
      alert('Only published templates can be instantiated')
      return
    }

    // Validate dashboard name
    if (!dashboardName || dashboardName.trim() === '') {
      alert('Please enter a dashboard name')
      return
    }

    // Validate required variables
    if (template && template.variables && Array.isArray(template.variables)) {
      const missingRequired = template.variables.filter(
        v => v.required && (!variableValues[v.name] || String(variableValues[v.name]).trim() === '')
      )
      if (missingRequired.length > 0) {
        alert(`Please fill in all required variables: ${missingRequired.map(v => v.name).join(', ')}`)
        return
      }
    }

    try {
      await templateApi.instantiate(id, {
        name: dashboardName.trim(),
        variable_values: variableValues
      })
      alert('Dashboard created successfully!')
      navigate('/dashboards')
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create dashboard'
      console.error('Failed to create dashboard:', error)
      alert(`Failed to create dashboard: ${errorMessage}`)
    }
  }

  const handlePublish = async () => {
    try {
      await templateApi.publish(id)
      alert('Template published successfully!')
      loadTemplate()
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to publish template'
      console.error('Failed to publish template:', error)
      alert(`Failed to publish template: ${errorMessage}`)
    }
  }

  const handleRate = async () => {
    try {
      await templateApi.rate(id, { rating, review: '' })
      await loadTemplate() // Reload template to get updated rating
      alert('Rating submitted!')
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to submit rating'
      console.error('Failed to submit rating:', error)
      alert(`Failed to submit rating: ${errorMessage}`)
    }
  }

  if (loading) return <div style={{ padding: '2rem' }}>Loading...</div>

  return (
    <div style={{ minHeight: '100vh', background: '#f8f9fa' }}>
      {/* Header */}
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
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
          {/* Left Column */}
          <div>
            <div style={{ background: 'white', borderRadius: '12px', padding: '2rem', marginBottom: '2rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                <div>
                  <h1 style={{ margin: '0 0 0.5rem 0', fontSize: '2rem' }}>{template.name}</h1>
                  <div style={{ display: 'flex', gap: '1rem', color: '#666', fontSize: '0.875rem' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <Calendar size={16} />
                      {new Date(template.created_at).toLocaleDateString()}
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <User size={16} />
                      Author #{template.author_id}
                    </span>
                  </div>
                </div>
                <span style={{
                  background: '#eff6ff',
                  color: '#1e40af',
                  padding: '0.5rem 1rem',
                  borderRadius: '6px',
                  fontSize: '1rem',
                  fontWeight: '600'
                }}>
                  v{template.version}
                </span>
              </div>

              <p style={{ color: '#666', lineHeight: '1.6', marginBottom: '1.5rem' }}>
                {template.description}
              </p>

              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
                {template.tags.map(tag => (
                  <span key={tag} style={{
                    background: '#f5f5f5',
                    padding: '0.5rem 1rem',
                    borderRadius: '6px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.25rem'
                  }}>
                    <Tag size={14} />
                    {tag}
                  </span>
                ))}
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', padding: '1rem', background: '#f8f9fa', borderRadius: '8px' }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: '#666', marginBottom: '0.25rem' }}>Rating</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Star size={20} fill="#ffa726" color="#ffa726" />
                    <span style={{ fontSize: '1.25rem', fontWeight: '600' }}>{template.rating}</span>
                    <span style={{ color: '#999' }}>({template.rating_count})</span>
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: '#666', marginBottom: '0.25rem' }}>Downloads</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Download size={20} color="#666" />
                    <span style={{ fontSize: '1.25rem', fontWeight: '600' }}>{template.usage_count}</span>
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: '#666', marginBottom: '0.25rem' }}>Category</div>
                  <div style={{ fontSize: '1rem', fontWeight: '600' }}>{template.category || 'General'}</div>
                </div>
              </div>
            </div>

            {/* Configuration Preview */}
            <div style={{ background: 'white', borderRadius: '12px', padding: '2rem' }}>
              <h2 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Code size={24} />
                Configuration
              </h2>
              <pre style={{
                background: '#f5f5f5',
                padding: '1rem',
                borderRadius: '8px',
                overflow: 'auto',
                fontSize: '0.875rem'
              }}>
                {JSON.stringify(template.config, null, 2)}
              </pre>
            </div>
          </div>

          {/* Right Column */}
          <div>
            {/* Install Card */}
            <div style={{ background: 'white', borderRadius: '12px', padding: '1.5rem', marginBottom: '1rem' }}>
              <h3 style={{ marginBottom: '1rem' }}>Use This Template</h3>
              
              {template.status !== 'published' ? (
                <div>
                  <div style={{
                    padding: '1rem',
                    background: '#fff3cd',
                    border: '1px solid #ffc107',
                    borderRadius: '8px',
                    color: '#856404',
                    marginBottom: '1rem'
                  }}>
                    This template is not published yet. Only published templates can be instantiated.
                  </div>
                  {template.status === 'draft' && (
                    <button
                      onClick={handlePublish}
                      style={{
                        width: '100%',
                        padding: '1rem',
                        background: '#28a745',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        fontSize: '1rem',
                        fontWeight: '600',
                        cursor: 'pointer'
                      }}
                    >
                      Publish Template
                    </button>
                  )}
                </div>
              ) : !showInstall ? (
                <button
                  onClick={() => setShowInstall(true)}
                  style={{
                    width: '100%',
                    padding: '1rem',
                    background: '#2563eb',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '1rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'background 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = '#1d4ed8'}
                  onMouseLeave={(e) => e.currentTarget.style.background = '#2563eb'}
                >
                  Create Dashboard
                </button>
              ) : (
                <div>
                  <input
                    type="text"
                    placeholder="Dashboard Name"
                    value={dashboardName}
                    onChange={(e) => setDashboardName(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      marginBottom: '1rem',
                      border: '1px solid #ddd',
                      borderRadius: '6px'
                    }}
                  />
                  
                  {template.variables && template.variables.length > 0 && template.variables.map(variable => (
                    <div key={variable.name} style={{ marginBottom: '1rem' }}>
                      <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '600' }}>
                        {variable.name}
                        {variable.required && <span style={{ color: 'red' }}>*</span>}
                      </label>
                      {variable.description && (
                        <p style={{ fontSize: '0.75rem', color: '#666', marginBottom: '0.5rem' }}>
                          {variable.description}
                        </p>
                      )}
                      <input
                        type="text"
                        value={variableValues[variable.name] || ''}
                        onChange={(e) => setVariableValues({
                          ...variableValues,
                          [variable.name]: e.target.value
                        })}
                        placeholder={variable.default_value}
                        style={{
                          width: '100%',
                          padding: '0.75rem',
                          border: '1px solid #ddd',
                          borderRadius: '6px'
                        }}
                      />
                    </div>
                  ))}
                  
                  <button
                    onClick={handleInstall}
                    style={{
                      width: '100%',
                      padding: '1rem',
                      background: '#2563eb',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '1rem',
                      fontWeight: '600',
                      cursor: 'pointer',
                      marginBottom: '0.5rem',
                      transition: 'background 0.2s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = '#1d4ed8'}
                    onMouseLeave={(e) => e.currentTarget.style.background = '#2563eb'}
                  >
                    Create Dashboard
                  </button>
                  <button
                    onClick={() => setShowInstall(false)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      background: 'transparent',
                      border: '1px solid #ddd',
                      borderRadius: '6px',
                      cursor: 'pointer'
                    }}
                  >
                    Cancel
                  </button>
                </div>
              )}
            </div>

            {/* Rate Template */}
            <div style={{ background: 'white', borderRadius: '12px', padding: '1.5rem', marginBottom: '1rem' }}>
              <h3 style={{ marginBottom: '1rem' }}>Rate This Template</h3>
              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
                {[1, 2, 3, 4, 5].map(star => (
                  <Star
                    key={star}
                    size={32}
                    fill={star <= rating ? '#ffa726' : 'none'}
                    color="#ffa726"
                    onClick={() => setRating(star)}
                    style={{ cursor: 'pointer' }}
                  />
                ))}
              </div>
              <button
                onClick={handleRate}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: '#2563eb',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  transition: 'background 0.2s'
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = '#1d4ed8'}
                onMouseLeave={(e) => e.currentTarget.style.background = '#2563eb'}
              >
                Submit Rating
              </button>
            </div>

            {/* Version History */}
            <div style={{ background: 'white', borderRadius: '12px', padding: '1.5rem' }}>
              <h3 style={{ marginBottom: '1rem' }}>Version History</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {versions.slice(0, 5).map(v => (
                  <div key={v.id} style={{
                    padding: '0.75rem',
                    background: v.id === template.id ? '#e3f2fd' : '#f8f9fa',
                    borderRadius: '6px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                      <span style={{ fontWeight: '600' }}>v{v.version}</span>
                      <span style={{ fontSize: '0.75rem', color: '#666' }}>
                        {new Date(v.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#666' }}>{v.status}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
