import React, { useState } from 'react';
import axios from 'axios';
const API = 'http://localhost:8000';
const ENDPOINTS = [
  {label:'GET /api/v1/users',url:'/api/v1/users',version:'v1'},
  {label:'GET /api/v2/users',url:'/api/v2/users',version:'v2'},
  {label:'GET /api/v1/users/1',url:'/api/v1/users/1',version:'v1'},
  {label:'GET /api/v2/users/1',url:'/api/v2/users/1',version:'v2'},
  {label:'GET /api/v1/teams/1',url:'/api/v1/teams/1',version:'v1'},
  {label:'GET /api/v2/teams/1',url:'/api/v2/teams/1',version:'v2'},
  {label:'GET /api/v2/analytics',url:'/api/v2/analytics',version:'v2'},
  {label:'GET /api/versions',url:'/api/versions',version:'meta'},
  {label:'GET /api/migration/v1/v2',url:'/api/migration/v1/v2',version:'meta'},
  {label:'GET /api/v2/compat/v1/users (Shim)',url:'/api/v2/compat/v1/users',version:'shim'},
];
const vc = v => v==='v1'?'#b45309':v==='v2'?'#16a34a':v==='shim'?'#5b21b6':'#475569';
const vbg = v => v==='v1'?'#fef9c3':v==='v2'?'#dcfce7':'#ede9fe';
const IH = ['x-api-version','sunset','deprecation','x-deprecation-notice','link','x-response-time'];
export default function ApiExplorer() {
  const [sel, setSel] = useState(ENDPOINTS[0]);
  const [res, setRes] = useState(null);
  const [hdrs, setHdrs] = useState({});
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [time, setTime] = useState(null);
  const fire = async () => {
    setLoading(true); const t0 = Date.now();
    try { const r = await axios.get(`${API}${sel.url}`); setStatus(r.status); setRes(r.data); setHdrs(r.headers); setTime(Date.now()-t0); }
    catch(e) { setStatus(e.response?.status||'ERR'); setRes(e.response?.data||{error:e.message}); setHdrs(e.response?.headers||{}); setTime(Date.now()-t0); }
    setLoading(false);
  };
  return (
    <div>
      <div className="page-header"><div className="page-title">API Explorer</div><div className="page-sub">Compare v1 vs v2 responses live — observe schema differences and deprecation headers</div></div>
      <div className="grid-2" style={{gap:24}}>
        <div>
          <div className="section-title">Select Endpoint</div>
          <div style={{display:'flex',flexDirection:'column',gap:6,marginBottom:20}}>
            {ENDPOINTS.map((ep,i)=>(
              <button key={i} className="btn btn-outline" style={{textAlign:'left',justifyContent:'flex-start',background:sel.url===ep.url?'#f0fdf4':'white',borderColor:sel.url===ep.url?'#16a34a':'#e2e8f0',color:vc(ep.version),fontFamily:'JetBrains Mono,monospace',fontSize:12}} onClick={()=>{setSel(ep);setRes(null);setStatus(null);}}>
                <span style={{fontSize:10,background:vbg(ep.version),borderRadius:4,padding:'2px 6px',marginRight:8,fontWeight:700,color:vc(ep.version)}}>{ep.version}</span>{ep.label}
              </button>
            ))}
          </div>
          <button className="btn btn-primary" style={{width:'100%'}} onClick={fire} disabled={loading}>{loading?'Sending…':'▶ Send Request'}</button>
        </div>
        <div>
          <div className="section-title">Response</div>
          <div className="response-panel">
            {!res && !loading && <div style={{color:'#475569',fontSize:13}}>Select an endpoint and click Send Request</div>}
            {loading && <div style={{color:'#86efac',fontSize:13}}>Sending…</div>}
            {res && <>
              <div className="response-meta">
                <span className={`response-status ${status===200?'status-200':'status-err'}`}>{status} {status===200?'OK':'Error'}</span>
                {time && <span className="header-tag">{time}ms</span>}
                {hdrs['x-api-version'] && <span className="header-tag">X-API-Version: {hdrs['x-api-version']}</span>}
                {hdrs['sunset'] && <span className="header-tag" style={{color:'#fde68a'}}>Sunset: {hdrs['sunset']}</span>}
              </div>
              {IH.some(h=>hdrs[h]) && <div style={{marginBottom:12}}><div style={{fontSize:11,color:'#64748b',marginBottom:6,textTransform:'uppercase'}}>Response Headers</div>{IH.filter(h=>hdrs[h]).map(h=><div key={h} style={{fontSize:11,fontFamily:'JetBrains Mono',color:'#a5f3fc',marginBottom:2}}><span style={{color:'#86efac'}}>{h}:</span> {hdrs[h]}</div>)}</div>}
              <div style={{fontSize:11,color:'#64748b',marginBottom:6,textTransform:'uppercase'}}>Body</div>
              <pre className="response-json">{JSON.stringify(res,null,2)}</pre>
            </>}
          </div>
          {sel.version==='v1' && <div style={{marginTop:12,background:'#fef9c3',borderRadius:8,padding:12,fontSize:12,color:'#92400e'}}><strong>v1 response:</strong> flat <code>name</code>, offset pagination. Check the Sunset header.</div>}
          {sel.version==='v2' && <div style={{marginTop:12,background:'#f0fdf4',borderRadius:8,padding:12,fontSize:12,color:'#166534'}}><strong>v2 response:</strong> <code>first_name</code>/<code>last_name</code>, cursor pagination, structured errors.</div>}
          {sel.version==='shim' && <div style={{marginTop:12,background:'#ede9fe',borderRadius:8,padding:12,fontSize:12,color:'#4c1d95'}}><strong>Shim active:</strong> v2 data re-shaped to v1 schema. Zero changes needed on the client.</div>}
        </div>
      </div>
    </div>
  );
}
