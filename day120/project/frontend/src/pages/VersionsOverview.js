import React, { useState, useEffect } from 'react';
import axios from 'axios';
const API = 'http://localhost:8000';
export default function VersionsOverview() {
  const [versions, setVersions] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    axios.get(`${API}/api/versions`).then(r => {
      const v = r.data.versions || [];
      setVersions(v);
      const byStatus = {};
      v.forEach(x => { byStatus[x.status] = (byStatus[x.status]||0)+1; });
      setStats({ total: v.length, byStatus });
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);
  const sc = s => s==='stable'?'stable':s==='deprecated'?'deprecated':s==='beta'?'beta':'retired';
  const vc = v => `version-card ${v}`;
  if (loading) return <div style={{padding:40,color:'#64748b'}}>Loading…</div>;
  return (
    <div>
      <div className="page-header"><div className="page-title">API Version Control</div><div className="page-sub">Manage and monitor all active API versions</div></div>
      <div className="grid-4 section">
        {[['Total Versions',versions.length,'All time'],['Active / Stable',(stats?.byStatus?.stable||0)+(stats?.byStatus?.beta||0),'Currently serving'],['Deprecated',stats?.byStatus?.deprecated||0,'Sunset scheduled'],['Recommended','v2','Current stable']].map(([l,v,s],i)=>(
          <div key={i} className="stat-card"><div className="stat-label">{l}</div><div className="stat-value" style={i===2?{color:'#b45309'}:i===3?{color:'#16a34a',fontSize:20}:{}}>{v}</div><div className="stat-change">{s}</div></div>
        ))}
      </div>
      <div className="section-title">All API Versions</div>
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:20,marginBottom:28}}>
        {versions.map(v => (
          <div key={v.version} className={vc(v.version)}>
            <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:8}}>
              <div className="version-number">API {v.version.toUpperCase()}</div>
              <span className={`badge badge-${sc(v.status)}`}>{v.status}</span>
            </div>
            <div className="version-desc">{v.description}</div>
            <div className="version-meta">
              <div className="meta-item">Released <strong>{v.release_date}</strong></div>
              {v.sunset_date && <div className="meta-item" style={{color:'#b45309'}}>Sunset <strong>{v.sunset_date}</strong></div>}
            </div>
            {v.new_features?.length>0 && <div className="features-list" style={{marginTop:12}}><div style={{fontSize:11,fontWeight:600,color:'#64748b',marginBottom:6,textTransform:'uppercase'}}>New</div>{v.new_features.slice(0,4).map((f,i)=><div key={i} className="feature-item">{f}</div>)}</div>}
            {v.breaking_changes?.length>0 && <div className="breaking-list" style={{marginTop:8}}><div style={{fontSize:11,fontWeight:600,color:'#92400e',marginBottom:6,textTransform:'uppercase'}}>Breaking</div>{v.breaking_changes.slice(0,3).map((b,i)=><div key={i} className="breaking-item">{b}</div>)}</div>}
          </div>
        ))}
      </div>
      <div className="card">
        <div className="card-header"><div className="card-title">Version Lifecycle Timeline</div></div>
        <div className="card-body">
          <div className="timeline">
            {[['','2024-01-15','v1 Released','Initial stable release'],['','2025-01-01','v2 GA','Cursor pagination, webhooks, analytics, structured errors'],['warn','2025-03-01','v1 Deprecated','Sunset headers added to all v1 responses'],['','2025-06-01','v3 Beta','Field selection, SSE subscriptions, batch operations'],['danger','2025-12-31','v1 Sunset','v1 endpoints removed — migrate to v2']].map(([cls,date,title,desc],i)=>(
              <div key={i} className="timeline-item">
                <div className={`timeline-dot ${cls}`}></div>
                <div className="timeline-date">{date}</div>
                <div className="timeline-content"><strong>{title}</strong> — {desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
