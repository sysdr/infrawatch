import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Save, Plus, X } from 'lucide-react'
import { templateApi } from '../services/api'

export default function TemplateEditor() {
  const navigate = useNavigate()
  const [template, setTemplate] = useState({
    name: '',
    description: '',
    category: 'monitoring',
    tags: [],
    visibility: 'private',
    role_access: [],
    config: {
      widgets: []
    },
    variables: []
  })
  const [newTag, setNewTag] = useState('')
  const [newVariable, setNewVariable] = useState({ name: '', description: '', variable_type: 'string', required: true })

  const handleSave = async () => {
    try {
      const result = await templateApi.create(template)
      alert('Template created successfully!')
      navigate(`/templates/${result.data.id}`)
    } catch (error) {
      alert('Failed to create template')
    }
  }

  const addWidget = () => {
    setTemplate({
      ...template,
      config: {
        ...template.config,
        widgets: [
          ...template.config.widgets,
          {
            id: `widget_${Date.now()}`,
            type: 'chart',
            title: 'New Widget',
            query: 'SELECT {{metric_name}} FROM metrics'
          }
        ]
      }
    })
  }

  const addTag = () => {
    if (newTag && !template.tags.includes(newTag)) {
      setTemplate({ ...template, tags: [...template.tags, newTag] })
      setNewTag('')
    }
  }

  const addVariable = () => {
    if (newVariable.name) {
      setTemplate({
        ...template,
        variables: [...template.variables, { ...newVariable }]
      })
      setNewVariable({ name: '', description: '', variable_type: 'string', required: true })
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
          <h1 style={{ margin: 0, fontSize: '1.5rem' }}>Create Template</h1>
          <button
            onClick={handleSave}
            style={{
              padding: '0.75rem 1.5rem',
              background: '#2563eb',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontWeight: '600',
              transition: 'background 0.2s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = '#1d4ed8'}
            onMouseLeave={(e) => e.currentTarget.style.background = '#2563eb'}
          >
            <Save size={20} />
            Save Template
          </button>
        </div>
      </header>

      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
          {/* Left Column */}
          <div>
            <div style={{ background: 'white', borderRadius: '12px', padding: '2rem', marginBottom: '2rem' }}>
              <h2 style={{ marginBottom: '1.5rem' }}>Template Details</h2>
              
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>Name</label>
                <input
                  type="text"
                  value={template.name}
                  onChange={(e) => setTemplate({ ...template, name: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #ddd',
                    borderRadius: '6px'
                  }}
                  placeholder="API Monitoring Dashboard"
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>Description</label>
                <textarea
                  value={template.description}
                  onChange={(e) => setTemplate({ ...template, description: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #ddd',
                    borderRadius: '6px',
                    minHeight: '100px'
                  }}
                  placeholder="Monitor API performance metrics..."
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>Category</label>
                <select
                  value={template.category}
                  onChange={(e) => setTemplate({ ...template, category: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #ddd',
                    borderRadius: '6px'
                  }}
                >
                  <option value="monitoring">Monitoring</option>
                  <option value="analytics">Analytics</option>
                  <option value="operations">Operations</option>
                  <option value="business">Business</option>
                </select>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>Visibility</label>
                <select
                  value={template.visibility}
                  onChange={(e) => setTemplate({ ...template, visibility: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #ddd',
                    borderRadius: '6px'
                  }}
                >
                  <option value="private">Private</option>
                  <option value="team">Team</option>
                  <option value="public">Public</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>Tags</label>
                <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <input
                    type="text"
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && addTag()}
                    style={{
                      flex: 1,
                      padding: '0.5rem',
                      border: '1px solid #ddd',
                      borderRadius: '6px'
                    }}
                    placeholder="Add tag..."
                  />
                  <button
                    onClick={addTag}
                    style={{
                      padding: '0.5rem 1rem',
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
                    <Plus size={16} />
                  </button>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  {template.tags.map(tag => (
                    <span key={tag} style={{
                      background: '#f5f5f5',
                      padding: '0.5rem',
                      borderRadius: '6px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      {tag}
                      <X
                        size={14}
                        onClick={() => setTemplate({ ...template, tags: template.tags.filter(t => t !== tag) })}
                        style={{ cursor: 'pointer' }}
                      />
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Variables */}
            <div style={{ background: 'white', borderRadius: '12px', padding: '2rem' }}>
              <h2 style={{ marginBottom: '1.5rem' }}>Template Variables</h2>
              
              <div style={{ marginBottom: '1rem', padding: '1rem', background: '#f8f9fa', borderRadius: '6px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <input
                    type="text"
                    value={newVariable.name}
                    onChange={(e) => setNewVariable({ ...newVariable, name: e.target.value })}
                    placeholder="Variable name"
                    style={{ padding: '0.5rem', border: '1px solid #ddd', borderRadius: '6px' }}
                  />
                  <select
                    value={newVariable.variable_type}
                    onChange={(e) => setNewVariable({ ...newVariable, variable_type: e.target.value })}
                    style={{ padding: '0.5rem', border: '1px solid #ddd', borderRadius: '6px' }}
                  >
                    <option value="string">String</option>
                    <option value="number">Number</option>
                    <option value="boolean">Boolean</option>
                  </select>
                </div>
                <input
                  type="text"
                  value={newVariable.description}
                  onChange={(e) => setNewVariable({ ...newVariable, description: e.target.value })}
                  placeholder="Description"
                  style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '6px', marginBottom: '0.5rem' }}
                />
                <button
                  onClick={addVariable}
                  style={{
                    padding: '0.5rem 1rem',
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
                  Add Variable
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {template.variables.map((v, i) => (
                  <div key={i} style={{
                    padding: '0.75rem',
                    background: '#f8f9fa',
                    borderRadius: '6px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <div>
                      <div style={{ fontWeight: '600' }}>{`{{${v.name}}}`}</div>
                      <div style={{ fontSize: '0.875rem', color: '#666' }}>{v.description}</div>
                    </div>
                    <X
                      size={16}
                      onClick={() => setTemplate({
                        ...template,
                        variables: template.variables.filter((_, idx) => idx !== i)
                      })}
                      style={{ cursor: 'pointer' }}
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div>
            <div style={{ background: 'white', borderRadius: '12px', padding: '2rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2 style={{ margin: 0 }}>Widgets</h2>
                <button
                  onClick={addWidget}
                  style={{
                    padding: '0.5rem 1rem',
                    background: '#2563eb',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    transition: 'background 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = '#1d4ed8'}
                  onMouseLeave={(e) => e.currentTarget.style.background = '#2563eb'}
                >
                  <Plus size={16} />
                  Add Widget
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {template.config.widgets.map((widget, index) => (
                  <div key={widget.id} style={{
                    padding: '1rem',
                    border: '1px solid #e0e0e0',
                    borderRadius: '8px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <input
                        type="text"
                        value={widget.title}
                        onChange={(e) => {
                          const newWidgets = [...template.config.widgets]
                          newWidgets[index].title = e.target.value
                          setTemplate({
                            ...template,
                            config: { ...template.config, widgets: newWidgets }
                          })
                        }}
                        style={{
                          flex: 1,
                          padding: '0.5rem',
                          border: '1px solid #ddd',
                          borderRadius: '6px',
                          fontWeight: '600'
                        }}
                      />
                      <X
                        size={20}
                        onClick={() => setTemplate({
                          ...template,
                          config: {
                            ...template.config,
                            widgets: template.config.widgets.filter(w => w.id !== widget.id)
                          }
                        })}
                        style={{ cursor: 'pointer', marginLeft: '0.5rem' }}
                      />
                    </div>
                    <textarea
                      value={widget.query}
                      onChange={(e) => {
                        const newWidgets = [...template.config.widgets]
                        newWidgets[index].query = e.target.value
                        setTemplate({
                          ...template,
                          config: { ...template.config, widgets: newWidgets }
                        })
                      }}
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: '1px solid #ddd',
                        borderRadius: '6px',
                        fontFamily: 'monospace',
                        fontSize: '0.875rem',
                        minHeight: '60px'
                      }}
                      placeholder="SELECT metric FROM data"
                    />
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
