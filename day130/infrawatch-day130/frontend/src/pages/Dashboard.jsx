import React, { useState, useEffect, useCallback } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, CartesianGrid } from 'recharts';
import { usersApi, notificationsApi, subscriptionsApi } from '../services/api.js';
import { usePushNotifications } from '../hooks/usePushNotifications.js';

const COLORS = ['#00d4aa','#3b82f6','#f59e0b','#ef4444','#a78bfa'];
const TT = { contentStyle:{background:'#132040',border:'1px solid #1e3a5f',borderRadius:8,fontSize:12} };

function Sidebar({ active, setActive }) {
  const items = [
    { id:'overview',     icon:'📊', label:'Overview'     },
    { id:'subscribe',    icon:'🔔', label:'Subscribe'    },
    { id:'preferences',  icon:'⚙️', label:'Preferences'  },
    { id:'send',         icon:'📤', label:'Send Test'    },
    { id:'analytics',    icon:'📈', label:'Analytics'    },
  ];
  return (
    <div className="sidebar">
      <div className="sidebar-logo">⚡ InfraWatch</div>
      <nav>
        {items.map(i => (
          <div key={i.id} className={`nav-item ${active===i.id?'active':''}`} onClick={()=>setActive(i.id)}>
            <span style={{fontSize:16}}>{i.icon}</span>{i.label}
          </div>
        ))}
      </nav>
    </div>
  );
}

function OverviewPage({ analytics }) {
  if (!analytics) return <div className="page"><p style={{color:'var(--text-secondary)'}}>Loading…</p></div>;
  const { totals:t, rates:r, subscriptions:s, by_category, recent } = analytics;
  return (
    <div className="page">
      <div className="page-title">Push Notification Overview</div>
      <div className="page-subtitle">Day 130 · Real-time delivery metrics and subscription health</div>
      <div className="grid-4">
        {[
          {label:'Total Sent',          val:t.sent,           cls:'',           sub:'all-time'},
          {label:'Delivery Rate',       val:r.delivery_rate+'%', cls:r.delivery_rate>=90?'stat-success':r.delivery_rate>=70?'stat-warn':'stat-danger', sub:t.delivered+' delivered'},
          {label:'Click-Through Rate',  val:r.ctr+'%',        cls:'stat-accent',sub:t.clicked+' clicked'},
          {label:'Active Subscriptions',val:s.active,         cls:'stat-success',sub:s.inactive+' inactive'},
        ].map(x=>(
          <div className="stat-card" key={x.label}>
            <div className="stat-label">{x.label}</div>
            <div className={`stat-value ${x.cls}`}>{x.val}</div>
            <div className="stat-sub">{x.sub}</div>
          </div>
        ))}
      </div>
      <div className="grid-2">
        <div className="card">
          <div className="card-title">Delivery Funnel</div>
          {[{label:'Sent',val:t.sent,color:'#3b82f6'},{label:'Delivered',val:t.delivered,color:'#00d4aa'},
            {label:'Clicked',val:t.clicked,color:'#22c55e'},{label:'Dismissed',val:t.dismissed,color:'#f59e0b'},
            {label:'Failed',val:t.failed,color:'#ef4444'}].map(row=>(
            <div className="bar-row" key={row.label}>
              <span className="bar-label">{row.label}</span>
              <div className="bar-track"><div className="bar-fill" style={{width:`${t.sent>0?Math.round(row.val/t.sent*100):0}%`,background:row.color}}/></div>
              <span className="bar-val">{row.val}</span>
            </div>
          ))}
        </div>
        <div className="card">
          <div className="card-title">By Category</div>
          {by_category.length===0
            ? <p style={{color:'var(--text-muted)',fontSize:13}}>No notifications yet — use Send Test tab.</p>
            : <ResponsiveContainer width="100%" height={180}>
                <PieChart><Pie data={by_category} dataKey="count" nameKey="category" cx="50%" cy="50%" outerRadius={70}
                    label={({category,percent})=>`${category} ${(percent*100).toFixed(0)}%`} labelLine={false}>
                  {by_category.map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]}/>)}
                </Pie><Tooltip {...TT}/></PieChart>
              </ResponsiveContainer>
          }
        </div>
      </div>
      <div className="card">
        <div className="card-title">Recent Notifications</div>
        {recent.length===0
          ? <p style={{color:'var(--text-muted)',fontSize:13}}>No notifications yet.</p>
          : <div className="table-wrap"><table>
              <thead><tr><th>Title</th><th>Category</th><th>Status</th><th>Sent At</th></tr></thead>
              <tbody>{recent.map(n=>(
                <tr key={n.id}>
                  <td style={{color:'var(--text-primary)'}}>{n.title}</td>
                  <td><span className="badge badge-blue">{n.category}</span></td>
                  <td><span className={`badge ${n.status==='clicked'?'badge-green':n.status==='delivered'?'badge-teal':n.status==='failed'?'badge-red':'badge-yellow'}`}>{n.status}</span></td>
                  <td>{n.sent_at?new Date(n.sent_at).toLocaleString():'—'}</td>
                </tr>
              ))}</tbody>
            </table></div>
        }
      </div>
    </div>
  );
}

function SubscribePage({ users, refresh }) {
  const [sel, setSel] = useState('');
  const [subs, setSubs] = useState([]);
  const [msg, setMsg] = useState(null);
  const { status, error, subscribe, unsubscribe, checkPermission } = usePushNotifications();
  const perm = checkPermission();

  useEffect(()=>{ if(sel) subscriptionsApi.getUserSubs(sel).then(r=>setSubs(r.data)).catch(()=>setSubs([])); },[sel,status]);

  const handleSubscribe = async () => {
    if (!sel) return setMsg({type:'warn',text:'Select a user first'});
    const res = await subscribe(sel);
    if (res) { setMsg({type:'success',text:'Subscribed! Push enabled.'}); refresh(); }
    else if (error) setMsg({type:'error',text:error});
  };

  return (
    <div className="page">
      <div className="page-title">Subscription Management</div>
      <div className="page-subtitle">Enable Web Push for your browser session</div>
      {perm==='denied'&&<div className="alert alert-error" style={{marginBottom:16}}>🚫 Blocked — reset in Browser Settings → Site Settings → Notifications.</div>}
      <div className="subscribe-banner">
        <div className="subscribe-info">
          <h3>🔔 Enable Push Notifications</h3>
          <p>Instant alerts for CPU spikes, failures, and security events — even with the tab closed.</p>
        </div>
        <div style={{display:'flex',gap:10,alignItems:'center'}}>
          <select className="user-selector" value={sel} onChange={e=>setSel(e.target.value)}>
            <option value="">Select user…</option>
            {users.map(u=><option key={u.id} value={u.id}>{u.username} ({u.role})</option>)}
          </select>
          <button className="btn btn-primary" onClick={handleSubscribe} disabled={status==='requesting'||!sel}>
            {status==='requesting'?'⏳ Requesting…':status==='subscribed'?'✅ Re-Subscribe':'🔔 Subscribe'}
          </button>
        </div>
      </div>
      {msg&&<div className={`alert alert-${msg.type}`}>{msg.text}</div>}
      <div className="card">
        <div className="card-title">Active Subscriptions {sel?`— ${users.find(u=>u.id===sel)?.username}`:''}</div>
        {!sel ? <p style={{color:'var(--text-muted)',fontSize:13}}>Select a user to see subscriptions.</p>
          : subs.length===0 ? <p style={{color:'var(--text-muted)',fontSize:13}}>No active subscriptions. Click Subscribe above.</p>
          : <div className="table-wrap"><table>
              <thead><tr><th>Endpoint</th><th>Status</th><th>Created</th><th>Action</th></tr></thead>
              <tbody>{subs.map(s=>(
                <tr key={s.id}>
                  <td style={{fontFamily:'monospace',fontSize:11}}>{s.endpoint}</td>
                  <td><span className={`badge ${s.is_active?'badge-green':'badge-red'}`}>{s.is_active?'active':'inactive'}</span></td>
                  <td>{new Date(s.created_at).toLocaleString()}</td>
                  <td><button className="btn btn-danger btn-sm" onClick={()=>unsubscribe(s.id).then(()=>subscriptionsApi.getUserSubs(sel).then(r=>setSubs(r.data)))}>Unsubscribe</button></td>
                </tr>
              ))}</tbody>
            </table></div>
        }
      </div>
      <div className="card" style={{marginTop:16}}>
        <div className="card-title">Browser Capability Check</div>
        <div style={{display:'flex',gap:16,flexWrap:'wrap'}}>
          {[{label:'Notifications API',ok:'Notification'in window},{label:'Service Worker',ok:'serviceWorker'in navigator},
            {label:'Push Manager',ok:'PushManager'in window},{label:'Permission',ok:perm==='granted',warn:perm==='default'}].map(item=>(
            <div key={item.label} style={{background:'var(--bg-primary)',border:'1px solid var(--border)',borderRadius:8,padding:'10px 16px'}}>
              <span className={`dot ${item.ok?'dot-green':item.warn?'dot-yellow':'dot-red'}`}/>
              <span style={{fontSize:12,color:'var(--text-secondary)'}}>{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function PreferencesPage({ users, refresh }) {
  const [sel, setSel] = useState('');
  const [prefs, setPrefs] = useState(null);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState(null);

  useEffect(()=>{ if(sel) notificationsApi.getPreferences(sel).then(r=>setPrefs(r.data)).catch(()=>setPrefs(null)); },[sel]);

  const toggle = async (field) => {
    if(!prefs) return;
    setPrefs({...prefs,[field]:!prefs[field]}); setSaving(true);
    await notificationsApi.updatePreferences(sel,{[field]:!prefs[field]}); setSaving(false);
    setMsg({type:'success',text:'Saved.'}); setTimeout(()=>setMsg(null),2000);
  };

  const handleSnooze = async (min) => {
    await notificationsApi.snooze({user_id:sel,duration_minutes:min});
    setPrefs((await notificationsApi.getPreferences(sel)).data);
    setMsg({type:'info',text:`Snoozed for ${min} min.`}); setTimeout(()=>setMsg(null),3000);
  };

  const clearSnooze = async () => {
    await notificationsApi.clearSnooze(sel);
    setPrefs((await notificationsApi.getPreferences(sel)).data);
    setMsg({type:'success',text:'Snooze cleared.'}); setTimeout(()=>setMsg(null),2000);
  };

  const items = prefs ? [
    {f:'alerts_enabled',          n:'⚡ Alert Notifications', d:'CPU spikes, memory, disk'},
    {f:'team_updates_enabled',    n:'👥 Team Updates',        d:'Members, roles, deployments'},
    {f:'daily_digest_enabled',    n:'📋 Daily Digest',        d:'Morning health summary (08:00)'},
    {f:'security_events_enabled', n:'🔒 Security Events',     d:'Failed logins, cert expiry'},
    {f:'quiet_hours_enabled',     n:`🌙 Quiet Hours (${prefs.quiet_hours_start}:00–${prefs.quiet_hours_end}:00)`, d:'Suppress non-critical at night'},
  ] : [];

  return (
    <div className="page">
      <div className="page-title">Notification Preferences</div>
      <div className="page-subtitle">Per-user, per-category controls with quiet hours and snooze</div>
      <div style={{marginBottom:20}}>
        <select className="user-selector" value={sel} onChange={e=>setSel(e.target.value)}>
          <option value="">Select user…</option>
          {users.map(u=><option key={u.id} value={u.id}>{u.username} ({u.role})</option>)}
        </select>
      </div>
      {msg&&<div className={`alert alert-${msg.type}`}>{msg.text}</div>}
      {!sel ? <div className="alert alert-info">Select a user to manage preferences.</div>
        : !prefs ? <div className="alert alert-warn">No preferences — subscribe this user first.</div>
        : <div className="grid-2">
            <div className="card">
              <div className="card-title">Category Controls {saving?'(saving…)':''}</div>
              {items.map(item=>(
                <div className="pref-row" key={item.f}>
                  <div className="pref-info"><span className="pref-name">{item.n}</span><span className="pref-desc">{item.d}</span></div>
                  <label className="toggle"><input type="checkbox" checked={!!prefs[item.f]} onChange={()=>toggle(item.f)}/><span className="toggle-slider"/></label>
                </div>
              ))}
            </div>
            <div className="card">
              <div className="card-title">Snooze Controls</div>
              {prefs.snoozed_until && new Date(prefs.snoozed_until)>new Date()
                ? <div><div className="alert alert-warn" style={{marginBottom:12}}>🔕 Snoozed until {new Date(prefs.snoozed_until).toLocaleString()}</div>
                    <button className="btn btn-secondary" onClick={clearSnooze}>Clear Snooze</button></div>
                : <div><p style={{color:'var(--text-muted)',fontSize:12,marginBottom:12}}>Temporarily suppress all non-critical</p>
                    <div style={{display:'flex',gap:8,flexWrap:'wrap'}}>
                      <button className="btn btn-secondary btn-sm" onClick={()=>handleSnooze(60)}>😴 1 Hour</button>
                      <button className="btn btn-secondary btn-sm" onClick={()=>handleSnooze(240)}>😴 4 Hours</button>
                      <button className="btn btn-secondary btn-sm" onClick={()=>handleSnooze(480)}>😴 8 Hours</button>
                    </div></div>
              }
              <div style={{marginTop:20}}>
                <div className="card-title">Role Defaults</div>
                {[{r:'devops',ok:true,n:'All categories on'},{r:'engineer',ok:true,n:'All categories on'},{r:'manager',ok:false,n:'Digest + team only'}].map(x=>(
                  <div key={x.r} style={{display:'flex',justifyContent:'space-between',padding:'6px 0',borderBottom:'1px solid var(--border)',fontSize:12}}>
                    <span style={{color:'var(--text-secondary)'}}>{x.r}</span>
                    <span style={{color:x.ok?'var(--success)':'var(--warn)'}}>{x.n}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
      }
    </div>
  );
}

function SendTestPage({ users, refresh }) {
  const [form, setForm] = useState({user_id:'',category:'alerts',title:'⚡ CPU Spike Detected',body:'prod-web-01 CPU at 94% — threshold exceeded',url:'/dashboard/alerts'});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if(!form.user_id) return setResult({type:'warn',text:'Select a user first'});
    setLoading(true); setResult(null);
    try {
      const {data} = await notificationsApi.send(form);
      setResult({type:'success',text:`Sent ✓ ID: ${data.notification_id.slice(0,12)}... Results: ${JSON.stringify(data.results)}`});
      refresh();
    } catch(e){ setResult({type:'error',text:e.response?.data?.detail||e.message}); }
    setLoading(false);
  };

  return (
    <div className="page">
      <div className="page-title">Send Test Notification</div>
      <div className="page-subtitle">Manually trigger a push for demo and debugging</div>
      <div className="card" style={{maxWidth:560}}>
        <div className="card-title">Notification Payload</div>
        <div style={{display:'flex',flexDirection:'column',gap:12}}>
          <div>
            <label style={{fontSize:11,color:'var(--text-muted)',display:'block',marginBottom:4}}>RECIPIENT</label>
            <select className="user-selector input" value={form.user_id} onChange={e=>setForm({...form,user_id:e.target.value})}>
              <option value="">Select user…</option>
              {users.map(u=><option key={u.id} value={u.id}>{u.username} ({u.role})</option>)}
            </select>
          </div>
          <div>
            <label style={{fontSize:11,color:'var(--text-muted)',display:'block',marginBottom:4}}>CATEGORY</label>
            <select className="user-selector input" value={form.category} onChange={e=>setForm({...form,category:e.target.value})}>
              <option value="alerts">⚡ Alerts</option>
              <option value="team_updates">👥 Team Updates</option>
              <option value="daily_digest">📋 Daily Digest</option>
              <option value="security_events">🔒 Security Events</option>
            </select>
          </div>
          {['title','body','url'].map(f=>(
            <div key={f}>
              <label style={{fontSize:11,color:'var(--text-muted)',display:'block',marginBottom:4}}>{f.toUpperCase()}</label>
              <input className="input" value={form[f]} onChange={e=>setForm({...form,[f]:e.target.value})}/>
            </div>
          ))}
          <button className="btn btn-primary" onClick={send} disabled={loading}>{loading?'⏳ Sending…':'📤 Send Notification'}</button>
        </div>
        {result&&<div className={`alert alert-${result.type}`} style={{marginTop:14,wordBreak:'break-all',fontSize:12}}>{result.text}</div>}
      </div>
      <div className="card" style={{marginTop:20,maxWidth:560}}>
        <div className="card-title">⚡ Quick Templates</div>
        {[
          {title:'🔴 Critical: Service Down',  body:'api-gateway-prod not responding — 5xx rate 100%',   category:'alerts'},
          {title:'🔐 Security: Login Anomaly', body:'15 failed logins from 185.220.x.x in last 5 min',  category:'security_events'},
          {title:'📋 Daily Digest',            body:'System health: 98% uptime · 3 alerts resolved',     category:'daily_digest'},
        ].map((t,i)=>(
          <div key={i} style={{padding:'10px 0',borderBottom:'1px solid var(--border)',cursor:'pointer'}} onClick={()=>setForm({...form,...t})}>
            <div style={{fontSize:13,fontWeight:600,color:'var(--text-primary)'}}>{t.title}</div>
            <div style={{fontSize:11,color:'var(--text-muted)',marginTop:2}}>{t.body}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AnalyticsPage({ analytics }) {
  if (!analytics) return <div className="page"><p style={{color:'var(--text-secondary)'}}>Loading…</p></div>;
  const { totals:t, rates:r, subscriptions:s, by_category } = analytics;
  const funnel = [{name:'Sent',value:t.sent},{name:'Delivered',value:t.delivered},{name:'Clicked',value:t.clicked},{name:'Dismissed',value:t.dismissed}];
  return (
    <div className="page">
      <div className="page-title">Notification Analytics</div>
      <div className="page-subtitle">Delivery rates, engagement metrics, and subscription health</div>
      <div className="grid-4">
        {[
          {label:'Delivery Rate',      val:r.delivery_rate+'%', cls:r.delivery_rate>=90?'stat-success':'stat-warn', sub:'target ≥ 95%'},
          {label:'Click-Through Rate', val:r.ctr+'%',           cls:'stat-accent',  sub:'benchmark 10–20%'},
          {label:'Dismiss Rate',       val:r.dismiss_rate+'%',  cls:r.dismiss_rate<30?'stat-success':'stat-warn', sub:'high → reduce noise'},
          {label:'Active Subs',        val:s.active,            cls:'stat-success', sub:s.inactive+' inactive'},
        ].map(x=>(
          <div className="stat-card" key={x.label}>
            <div className="stat-label">{x.label}</div>
            <div className={`stat-value ${x.cls}`}>{x.val}</div>
            <div className="stat-sub">{x.sub}</div>
          </div>
        ))}
      </div>
      <div className="grid-2">
        <div className="card">
          <div className="card-title">Delivery Funnel</div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={funnel} margin={{top:4,right:20,bottom:0,left:0}}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f"/>
              <XAxis dataKey="name" tick={{fill:'#8899bb',fontSize:11}}/>
              <YAxis tick={{fill:'#8899bb',fontSize:11}} allowDecimals={false}/>
              <Tooltip {...TT}/><Bar dataKey="value" fill="#00d4aa" radius={[4,4,0,0]}/>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <div className="card-title">By Category</div>
          {by_category.length===0
            ? <p style={{color:'var(--text-muted)',fontSize:13}}>Send notifications first.</p>
            : <ResponsiveContainer width="100%" height={200}>
                <BarChart data={by_category} layout="vertical" margin={{left:20,right:20}}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f"/>
                  <XAxis type="number" tick={{fill:'#8899bb',fontSize:11}}/>
                  <YAxis type="category" dataKey="category" tick={{fill:'#8899bb',fontSize:11}} width={100}/>
                  <Tooltip {...TT}/><Bar dataKey="count" radius={[0,4,4,0]}>
                    {by_category.map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]}/>)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
          }
        </div>
      </div>
      <div className="card">
        <div className="card-title">Interpretation Guide</div>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
          {[
            {m:'Delivery Rate < 95%',  d:'Stale subscriptions — run GC',         c:'var(--danger)'},
            {m:'CTR < 5%',            d:'Content not actionable — improve copy', c:'var(--warn)'},
            {m:'Dismiss Rate > 40%',  d:'Notification fatigue — reduce frequency',c:'var(--warn)'},
            {m:'Sub Churn > 5%/week', d:'Poor relevance — personalize',          c:'var(--danger)'},
          ].map(x=>(
            <div key={x.m} style={{padding:'10px 14px',background:'var(--bg-primary)',borderRadius:8,borderLeft:`3px solid ${x.c}`}}>
              <div style={{fontSize:12,fontWeight:700,color:'var(--text-primary)',marginBottom:4}}>{x.m}</div>
              <div style={{fontSize:11,color:'var(--text-muted)'}}>{x.d}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [page, setPage] = useState('overview');
  const [users, setUsers] = useState([]);
  const [analytics, setAnalytics] = useState(null);

  const loadAnalytics = useCallback(()=>{
    notificationsApi.getAnalytics().then(r=>setAnalytics(r.data)).catch(console.error);
  },[]);

  useEffect(()=>{
    usersApi.list().then(r=>setUsers(r.data)).catch(console.error);
    loadAnalytics();
    const iv = setInterval(loadAnalytics, 10000);
    return ()=>clearInterval(iv);
  },[loadAnalytics]);

  useEffect(()=>{
    usersApi.list().then(r=>{
      if(r.data.length===0) Promise.all([
        usersApi.create({username:'alice_devops',email:'alice@infrawatch.dev',role:'devops',timezone:'UTC'}),
        usersApi.create({username:'bob_sre',     email:'bob@infrawatch.dev',  role:'engineer',timezone:'UTC'}),
        usersApi.create({username:'carol_pm',    email:'carol@infrawatch.dev',role:'manager', timezone:'UTC'}),
      ]).then(()=>usersApi.list().then(r2=>setUsers(r2.data)));
    });
  },[]);

  return (
    <div className="layout">
      <Sidebar active={page} setActive={setPage}/>
      <div className="main-content">
        <div className="topbar">
          <div className="topbar-brand"><span>⚡</span> InfraWatch · Push Notifications</div>
          <div style={{display:'flex',gap:12,alignItems:'center'}}>
            <span className="badge badge-green">● Live</span>
            <span style={{color:'var(--text-muted)',fontSize:12}}>Day 130</span>
          </div>
        </div>
        {page==='overview'    && <OverviewPage analytics={analytics} users={users}/>}
        {page==='subscribe'   && <SubscribePage users={users} refresh={loadAnalytics}/>}
        {page==='preferences' && <PreferencesPage users={users} refresh={loadAnalytics}/>}
        {page==='send'        && <SendTestPage users={users} refresh={loadAnalytics}/>}
        {page==='analytics'   && <AnalyticsPage analytics={analytics}/>}
      </div>
    </div>
  );
}
