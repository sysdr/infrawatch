import React, { useState, useEffect } from 'react';
import axios from 'axios';
const API = 'http://localhost:8000';
export default function MigrationGuide() {
  const [guide, setGuide] = useState(null);
  const [from, setFrom] = useState('v1');
  const [to, setTo] = useState('v2');
  const [loading, setLoading] = useState(false);
  const load = (f, t) => { setLoading(true); axios.get(`${API}/api/migration/${f}/${t}`).then(r=>{setGuide(r.data);setLoading(false);}).catch(()=>{setGuide(null);setLoading(false);}); };
  useEffect(() => { load('v1','v2'); }, []);
  return (
    <div>
      <div className="page-header"><div className="page-title">Migration Guide</div><div className="page-sub">Step-by-step instructions to migrate between API versions</div></div>
      <div className="explorer-controls">
        <select value={from} onChange={e=>setFrom(e.target.value)}><option value="v1">v1 (Deprecated)</option><option value="v2">v2 (Stable)</option></select>
        <span style={{color:'#94a3b8',fontSize:18}}>→</span>
        <select value={to} onChange={e=>setTo(e.target.value)}><option value="v2">v2 (Stable)</option><option value="v3">v3 (Beta)</option></select>
        <button className="btn btn-primary" onClick={()=>load(from,to)}>Load Guide</button>
      </div>
      {loading && <div style={{color:'#64748b',padding:20}}>Loading…</div>}
      {!loading && !guide && <div className="card"><div className="card-body" style={{color:'#94a3b8',textAlign:'center',padding:40}}>No migration guide found for {from} → {to}</div></div>}
      {!loading && guide && <>
        <div className="card section">
          <div className="card-header"><div className="card-title">{guide.from_version.toUpperCase()} → {guide.to_version.toUpperCase()} Migration</div><span className="badge badge-stable">Est. {guide.estimated_effort}</span></div>
          <div className="card-body">
            <div className="section-title" style={{fontSize:14}}>Breaking Changes</div>
            {guide.breaking_changes.map((b,i)=><div key={i} className="breaking-item">{b}</div>)}
          </div>
        </div>
        <div className="section-title">Migration Steps</div>
        {guide.steps.map((s,i)=>(
          <div key={i} className="step-card">
            <div className="step-num">{s.order}</div>
            <div style={{flex:1}}><div className="step-title">{s.title}</div><div className="step-desc">{s.description}</div>{s.code && <div className="code-block mono" style={{marginTop:10}}>{s.code}</div>}</div>
          </div>
        ))}
        {Object.keys(guide.field_mappings).length>0 && (
          <div className="card" style={{marginTop:24}}>
            <div className="card-header"><div className="card-title">Field Mapping Reference</div><span style={{fontSize:12,color:'#94a3b8'}}>{Object.keys(guide.field_mappings).length} fields changed</span></div>
            <div style={{overflowX:'auto'}}>
              <table className="mapping-table"><thead><tr><th>{guide.from_version} Field</th><th className="arrow-cell"></th><th>{guide.to_version} Field</th></tr></thead>
              <tbody>{Object.entries(guide.field_mappings).map(([k,v],i)=><tr key={i}><td className="from-field">{k}</td><td className="arrow-cell">→</td><td className="to-field">{v}</td></tr>)}</tbody></table>
            </div>
          </div>
        )}
      </>}
    </div>
  );
}
