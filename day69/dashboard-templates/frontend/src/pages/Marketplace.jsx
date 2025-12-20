import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Search, Star, Download, Filter, TrendingUp, Plus } from 'lucide-react'
import { templateApi, statsApi } from '../services/api'

export default function Marketplace() {
  const [templates, setTemplates] = useState([])
  const [stats, setStats] = useState(null)
  const [categories, setCategories] = useState([])
  const [filters, setFilters] = useState({
    query: '',
    category: '',
    sort_by: 'created_at',
    min_rating: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [filters])

  const loadData = async () => {
    try {
      setLoading(true)
      const [templatesRes, statsRes, categoriesRes] = await Promise.all([
        templateApi.search(filters),
        statsApi.get(),
        statsApi.getCategories()
      ])
      setTemplates(templatesRes.data.templates)
      setStats(statsRes.data)
      setCategories(categoriesRes.data)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    loadData()
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f8f9fa' }}>
      {/* Header */}
      <header style={{
        background: 'linear-gradient(135deg, #1e40af 0%, #2563eb 100%)',
        color: 'white',
        padding: '2rem 0',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
            <h1 style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0 }}>Dashboard Templates</h1>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <Link to="/my-templates" style={{
                padding: '0.5rem 1rem',
                background: 'rgba(255,255,255,0.2)',
                borderRadius: '6px',
                textDecoration: 'none',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                My Templates
              </Link>
              <Link to="/templates/new" style={{
                padding: '0.5rem 1rem',
                background: 'white',
                color: '#2563eb',
                borderRadius: '6px',
                textDecoration: 'none',
                fontWeight: '600',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                transition: 'background 0.2s'
              }}>
                <Plus size={20} />
                Create Template
              </Link>
            </div>
          </div>

          {/* Stats */}
          {stats && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
              <div style={{ background: 'rgba(255,255,255,0.15)', padding: '1rem', borderRadius: '8px' }}>
                <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{stats.total_templates}</div>
                <div style={{ opacity: 0.9 }}>Templates</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.15)', padding: '1rem', borderRadius: '8px' }}>
                <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{stats.total_dashboards}</div>
                <div style={{ opacity: 0.9 }}>Dashboards Created</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.15)', padding: '1rem', borderRadius: '8px' }}>
                <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{categories.length}</div>
                <div style={{ opacity: 0.9 }}>Categories</div>
              </div>
            </div>
          )}

          {/* Search */}
          <form onSubmit={handleSearch} style={{ position: 'relative' }}>
            <Search style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: '#666' }} />
            <input
              type="text"
              placeholder="Search templates..."
              value={filters.query}
              onChange={(e) => setFilters({ ...filters, query: e.target.value })}
              style={{
                width: '100%',
                padding: '1rem 1rem 1rem 3rem',
                borderRadius: '8px',
                border: 'none',
                fontSize: '1rem'
              }}
            />
          </form>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
        {/* Filters */}
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
          <select
            value={filters.category}
            onChange={(e) => setFilters({ ...filters, category: e.target.value })}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              border: '1px solid #ddd',
              background: 'white'
            }}
          >
            <option value="">All Categories</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>

          <select
            value={filters.sort_by}
            onChange={(e) => setFilters({ ...filters, sort_by: e.target.value })}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              border: '1px solid #ddd',
              background: 'white'
            }}
          >
            <option value="created_at">Latest</option>
            <option value="usage_count">Most Used</option>
            <option value="rating">Highest Rated</option>
          </select>

          <select
            value={filters.min_rating}
            onChange={(e) => setFilters({ ...filters, min_rating: parseInt(e.target.value) })}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              border: '1px solid #ddd',
              background: 'white'
            }}
          >
            <option value="0">All Ratings</option>
            <option value="3">3+ Stars</option>
            <option value="4">4+ Stars</option>
          </select>
        </div>

        {/* Templates Grid */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '4rem' }}>Loading...</div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
            {templates.map(template => (
              <Link
                key={template.id}
                to={`/templates/${template.id}`}
                style={{
                  background: 'white',
                  borderRadius: '12px',
                  padding: '1.5rem',
                  textDecoration: 'none',
                  color: 'inherit',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  cursor: 'pointer'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'translateY(-4px)'
                  e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.15)'
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)'
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                  <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: '600' }}>{template.name}</h3>
                  <span style={{
                    background: '#e3f2fd',
                    color: '#1976d2',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '4px',
                    fontSize: '0.75rem',
                    fontWeight: '600'
                  }}>
                    v{template.version}
                  </span>
                </div>

                <p style={{
                  color: '#666',
                  fontSize: '0.875rem',
                  marginBottom: '1rem',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical'
                }}>
                  {template.description || 'No description'}
                </p>

                <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
                  {template.tags.slice(0, 3).map(tag => (
                    <span key={tag} style={{
                      background: '#f5f5f5',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem'
                    }}>
                      {tag}
                    </span>
                  ))}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '1rem', borderTop: '1px solid #f0f0f0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: '#ffa726' }}>
                    <Star size={16} fill="#ffa726" />
                    <span style={{ fontWeight: '600' }}>{template.rating}</span>
                    <span style={{ color: '#999', fontSize: '0.875rem' }}>({template.rating_count})</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: '#666' }}>
                    <Download size={16} />
                    <span style={{ fontSize: '0.875rem' }}>{template.usage_count}</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}

        {templates.length === 0 && !loading && (
          <div style={{ textAlign: 'center', padding: '4rem', color: '#666' }}>
            <p>No templates found. Try adjusting your filters.</p>
          </div>
        )}
      </main>
    </div>
  )
}
