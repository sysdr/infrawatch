import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
const API = 'http://localhost:8000';
const COLORS = ['#f9a825','#22c55e'];
export default function Analytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => { axios.get(`${API}/api/v2/analytics`).then(r=>{setData(r.data.data);setLoading(false);}).catch(()=>setLoading(false)); }, []);
  if (loading) return <div style={{padding:40,color:'#64748b'}}>Loading…</div>;
  if (!data)   return <div style={{padding:40,color:'#ef4444'}}>Failed to load analytics</div>;
  const callsData = [{name:'v1',calls:data.api_calls.v1,fill:'#f9a825'},{name:'v2',calls:data.api_calls.v2,fill:'#22c55e'}];
  const latencyData = [{name:'p50',ms:data.latency_ms.p50},{name:'p95',ms:data.latency_ms.p95},{name:'p99',ms:data.latency_ms.p99}];
  const adoptionPie = [{name:'v1',value:data.version_adoption[0].calls_pct},{name:'v2',value:data.version_adoption[1].calls_pct}];
  return (
    <div>
      <div className="page-header"><div className="page-title">Version Analytics</div><div className="page-sub">Real-time adoption metrics and migration health across all API versions</div></div>
      <div className="grid-4 section">
        {[[`Total Calls`,data.api_calls.total.toLocaleString(),'Last 24h'],[`Error Rate`,`${data.errors.rate}%`,`${data.errors.total} total`],['Uptime',`${data.uptime_pct}%`,'All versions'],['Active Clients',data.active_clients.v1+data.active_clients.v2,`v1:${data.active_clients.v1} · v2:${data.active_clients.v2}`]].map(([l,v,s],i)=>(
          <div key={i} className="stat-card"><div className="stat-label">{l}</div><div className="stat-value" style={i===1&&data.errors.rate>1?{color:'#ef4444'}:i===2?{color:'#16a34a'}:{}}>{v}</div><div className="stat-change">{s}</div></div>
        ))}
      </div>
      <div className="grid-2 section">
        <div className="card"><div className="card-header"><div className="card-title">API Calls by Version (24h)</div></div><div className="card-body"><ResponsiveContainer width="100%" height={200}><BarChart data={callsData}><XAxis dataKey="name" axisLine={false} tickLine={false} style={{fontSize:12}}/><YAxis axisLine={false} tickLine={false} style={{fontSize:11}}/><Tooltip formatter={v=>[v.toLocaleString(),'Calls']}/><Bar dataKey="calls" radius={[6,6,0,0]}>{callsData.map((e,i)=><Cell key={i} fill={e.fill}/>)}</Bar></BarChart></ResponsiveContainer></div></div>
        <div className="card"><div className="card-header"><div className="card-title">Version Adoption</div></div><div className="card-body"><ResponsiveContainer width="100%" height={200}><PieChart><Pie data={adoptionPie} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label={({name,value})=>`${name}: ${value}%`}>{adoptionPie.map((_,i)=><Cell key={i} fill={COLORS[i]}/>)}</Pie><Legend/><Tooltip formatter={v=>[`${v}%`]}/></PieChart></ResponsiveContainer></div></div>
      </div>
      <div className="card section"><div className="card-header"><div className="card-title">Latency Percentiles (ms)</div></div><div className="card-body"><ResponsiveContainer width="100%" height={180}><BarChart data={latencyData}><XAxis dataKey="name" axisLine={false} tickLine={false} style={{fontSize:12}}/><YAxis axisLine={false} tickLine={false} style={{fontSize:11}}/><Tooltip formatter={v=>[`${v}ms`,'Latency']}/><Bar dataKey="ms" fill="#86efac" radius={[6,6,0,0]}/></BarChart></ResponsiveContainer></div></div>
      <div className="card"><div className="card-header"><div className="card-title">Migration Progress</div></div><div className="card-body">{data.version_adoption.map((v,i)=><div key={i} className="adoption-bar-wrap"><div className="adoption-label"><span><strong>{v.version.toUpperCase()}</strong> · {v.trend}</span><span>{v.calls_pct}%</span></div><div className="adoption-bar-bg"><div className={`adoption-bar-fill ${v.version==='v2'?'fill-green':'fill-yellow'}`} style={{width:`${v.calls_pct}%`}}/></div></div>)}<div style={{marginTop:16,fontSize:12,color:'#64748b'}}>Target: ≥90% v2 adoption before v1 sunset on 2025-12-31. Currently <strong style={{color:'#16a34a'}}>{data.version_adoption[1].calls_pct}%</strong> on v2.</div></div></div>
    </div>
  );
}
