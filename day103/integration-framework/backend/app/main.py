import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.database import init_db, get_db
from app.models import Integration, WebhookEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Integration Framework API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class IntegrationCreate(BaseModel):
    name: str
    type: str = "webhook"
    config: Optional[Dict[str, Any]] = {}

class WebhookPayload(BaseModel):
    source: Optional[str] = None
    payload: Optional[Dict[str, Any]] = {}

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Integration Framework Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    * { box-sizing: border-box; }
    body {
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      margin: 0;
      padding: 0;
      background: linear-gradient(160deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
      min-height: 100vh;
      color: #e0e0e0;
    }
    .container { max-width: 1200px; margin: 0 auto; padding: 24px; }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
      margin-bottom: 28px;
      padding-bottom: 20px;
      border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    h1 {
      margin: 0;
      font-size: 1.75rem;
      font-weight: 700;
      background: linear-gradient(90deg, #00d9ff, #00ff88);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    .subtitle { color: rgba(255,255,255,0.6); font-size: 0.9rem; margin-top: 4px; }
    .header-right { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
    .live-badge {
      background: rgba(0, 255, 136, 0.2);
      color: #00ff88;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: 600;
    }
    .last-updated { color: rgba(255,255,255,0.5); font-size: 0.8rem; }
    .btn {
      background: linear-gradient(135deg, #00d9ff, #0099cc);
      color: #fff;
      border: none;
      padding: 10px 20px;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 600;
      font-size: 0.9rem;
    }
    .btn:hover { opacity: 0.9; transform: translateY(-1px); }
    .cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin-bottom: 28px;
    }
    .card {
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.08);
      padding: 24px;
      border-radius: 16px;
      position: relative;
      overflow: hidden;
    }
    .card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 4px;
      height: 100%;
    }
    .card.integrations::before { background: linear-gradient(180deg, #00d9ff, #0099cc); }
    .card.webhooks::before { background: linear-gradient(180deg, #ff6b6b, #ee5a5a); }
    .card.events::before { background: linear-gradient(180deg, #00ff88, #00cc6a); }
    .card h3 {
      margin: 0 0 8px 0;
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: rgba(255,255,255,0.6);
    }
    .card .value { font-size: 2.25rem; font-weight: 800; color: #fff; }
    .chart-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin-bottom: 24px;
    }
    @media (max-width: 768px) { .chart-row { grid-template-columns: 1fr; } }
    .chart-card {
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 16px;
      padding: 24px;
    }
    .chart-card h4 {
      margin: 0 0 16px 0;
      font-size: 1rem;
      color: rgba(255,255,255,0.9);
    }
    .chart-container { position: relative; height: 280px; }
    .activity-card {
      grid-column: 1 / -1;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 16px;
      padding: 24px;
    }
    .activity-card h4 { margin: 0 0 16px 0; font-size: 1rem; color: rgba(255,255,255,0.9); }
    .activity-card .chart-container { height: 200px; }
    #err {
      background: rgba(255, 100, 100, 0.15);
      color: #ff6b6b;
      padding: 14px 20px;
      border-radius: 12px;
      margin-bottom: 20px;
      display: none;
      border: 1px solid rgba(255,107,107,0.3);
    }
    .links { margin-top: 20px; }
    .links a { color: #00d9ff; margin-right: 16px; text-decoration: none; font-size: 0.9rem; }
    .links a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>Integration Framework Dashboard</h1>
        <p class="subtitle">Day 103 &middot; Webhooks &amp; integrations &middot; Live metrics</p>
      </div>
      <div class="header-right">
        <span class="live-badge">&bull; Live</span>
        <span class="last-updated" id="lastUpdated">—</span>
        <button class="btn" onclick="load()">Refresh</button>
      </div>
    </header>
    <div class="cards">
      <div class="card integrations"><h3>Integrations</h3><div class="value" id="integrations">0</div></div>
      <div class="card webhooks"><h3>Webhooks received</h3><div class="value" id="webhooks">0</div></div>
      <div class="card events"><h3>Events processed</h3><div class="value" id="events">0</div></div>
    </div>
    <div id="err"></div>
    <div class="chart-row">
      <div class="chart-card">
        <h4>Metrics overview</h4>
        <div class="chart-container"><canvas id="barChart"></canvas></div>
      </div>
      <div class="chart-card">
        <h4>Distribution</h4>
        <div class="chart-container"><canvas id="doughnutChart"></canvas></div>
      </div>
    </div>
    <div class="chart-row">
      <div class="activity-card">
        <h4>Activity over time (last updates)</h4>
        <div class="chart-container"><canvas id="lineChart"></canvas></div>
      </div>
    </div>
    <div class="links">
      <a href="/api/dashboard" target="_blank">API</a>
      <a href="/docs" target="_blank">Swagger Docs</a>
    </div>
  </div>
  <script>
    var barChart, doughnutChart, lineChart;
    var historyData = [];
    var maxHistory = 20;
    var colors = { integrations: 'rgba(0, 217, 255, 0.8)', webhooks: 'rgba(255, 107, 107, 0.8)', events: 'rgba(0, 255, 136, 0.8)' };
    var borderColors = { integrations: '#00d9ff', webhooks: '#ff6b6b', events: '#00ff88' };
    function initCharts() {
      var opts = { responsive: true, maintainAspectRatio: false };
      barChart = new Chart(document.getElementById('barChart'), {
        type: 'bar',
        data: {
          labels: ['Integrations', 'Webhooks', 'Events'],
          datasets: [{ label: 'Count', data: [0, 0, 0], backgroundColor: [colors.integrations, colors.webhooks, colors.events], borderColor: [borderColors.integrations, borderColors.webhooks, borderColors.events], borderWidth: 1 }]
        },
        options: { ...opts, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.06)' }, ticks: { color: '#aaa' } }, x: { grid: { display: false }, ticks: { color: '#aaa' } } } }
      });
      doughnutChart = new Chart(document.getElementById('doughnutChart'), {
        type: 'doughnut',
        data: {
          labels: ['Integrations', 'Webhooks', 'Events'],
          datasets: [{ data: [0, 0, 0], backgroundColor: [colors.integrations, colors.webhooks, colors.events], borderColor: ['#0f0c29', '#0f0c29', '#0f0c29'], borderWidth: 2 }]
        },
        options: { ...opts, plugins: { legend: { labels: { color: '#e0e0e0' } } } }
      });
      lineChart = new Chart(document.getElementById('lineChart'), {
        type: 'line',
        data: {
          labels: [],
          datasets: [
            { label: 'Webhooks', data: [], borderColor: '#ff6b6b', backgroundColor: 'rgba(255,107,107,0.2)', fill: true, tension: 0.3 },
            { label: 'Events', data: [], borderColor: '#00ff88', backgroundColor: 'rgba(0,255,136,0.2)', fill: true, tension: 0.3 }
          ]
        },
        options: { ...opts, plugins: { legend: { labels: { color: '#e0e0e0' } } }, scales: { y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.06)' }, ticks: { color: '#aaa' } }, x: { grid: { color: 'rgba(255,255,255,0.06)' }, ticks: { color: '#aaa' } } } }
      });
    }
    function updateCharts(d) {
      var i = d.integrations != null ? d.integrations : 0;
      var w = d.webhooks_received != null ? d.webhooks_received : 0;
      var e = d.events_processed != null ? d.events_processed : 0;
      if (barChart) {
        barChart.data.datasets[0].data = [i, w, e];
        barChart.update('none');
      }
      if (doughnutChart) {
        var total = i + w + e || 1;
        doughnutChart.data.datasets[0].data = [i, w, e];
        doughnutChart.update('none');
      }
      historyData.push({ w: w, e: e, t: new Date().toLocaleTimeString() });
      if (historyData.length > maxHistory) historyData.shift();
      if (lineChart && historyData.length) {
        lineChart.data.labels = historyData.map(function(x) { return x.t; });
        lineChart.data.datasets[0].data = historyData.map(function(x) { return x.w; });
        lineChart.data.datasets[1].data = historyData.map(function(x) { return x.e; });
        lineChart.update('none');
      }
    }
    function load() {
      var base = window.location.origin;
      var errEl = document.getElementById('err');
      errEl.style.display = 'none';
      fetch(base + '/api/dashboard').then(function(r) { if (!r.ok) throw new Error(r.status); return r.json(); }).then(function(d) {
        document.getElementById('integrations').textContent = d.integrations != null ? d.integrations : 0;
        document.getElementById('webhooks').textContent = d.webhooks_received != null ? d.webhooks_received : 0;
        document.getElementById('events').textContent = d.events_processed != null ? d.events_processed : 0;
        document.getElementById('lastUpdated').textContent = 'Updated ' + new Date().toLocaleTimeString();
        updateCharts(d);
      }).catch(function() {
        document.getElementById('integrations').textContent = '0';
        document.getElementById('webhooks').textContent = '0';
        document.getElementById('events').textContent = '0';
        errEl.textContent = 'Could not load metrics. Ensure backend is running on ' + base;
        errEl.style.display = 'block';
      });
    }
    if (typeof Chart !== 'undefined') {
      initCharts();
      load();
      setInterval(load, 5000);
    } else {
      document.getElementById('err').textContent = 'Chart.js failed to load.';
      document.getElementById('err').style.display = 'block';
      load();
      setInterval(load, 5000);
    }
  </script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
@app.get("/dashboard/", response_class=HTMLResponse)
async def dashboard_page():
    """Dashboard at root and /dashboard - open http://localhost:8000 or http://localhost:8000/dashboard"""
    return DASHBOARD_HTML

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/root")
async def root():
    return {"message": "Day 103: Integration Framework API", "version": "1.0.0"}

@app.get("/api/dashboard")
async def get_dashboard(db: Session = Depends(get_db)):
    integrations = db.query(Integration).count()
    webhooks_received = db.query(WebhookEvent).count()
    events_processed = db.query(WebhookEvent).filter(WebhookEvent.processed == 1).count()
    return {
        "integrations": integrations,
        "webhooks_received": webhooks_received,
        "events_processed": events_processed,
    }

@app.post("/api/integrations", response_model=dict)
async def create_integration(body: IntegrationCreate, db: Session = Depends(get_db)):
    i = Integration(name=body.name, type=body.type, config=body.config or {})
    db.add(i)
    db.commit()
    db.refresh(i)
    return {"id": i.id, "name": i.name, "type": i.type}

@app.get("/api/integrations")
async def list_integrations(db: Session = Depends(get_db)):
    rows = db.query(Integration).all()
    return [{"id": r.id, "name": r.name, "type": r.type, "enabled": r.enabled} for r in rows]

@app.post("/api/webhook/{integration_id}")
async def receive_webhook(integration_id: str, body: WebhookPayload, db: Session = Depends(get_db)):
    integ = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integ:
        raise HTTPException(404, "Integration not found")
    ev = WebhookEvent(integration_id=integration_id, source=body.source or "unknown", payload=body.payload or {}, processed=1)
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return {"status": "received", "event_id": ev.id}

@app.post("/api/webhook")
async def receive_webhook_any(body: WebhookPayload, db: Session = Depends(get_db)):
    integs = db.query(Integration).filter(Integration.enabled == 1).limit(1).all()
    if not integs:
        raise HTTPException(400, "No integration configured. Create one first.")
    integ = integs[0]
    ev = WebhookEvent(integration_id=integ.id, source=body.source or "anonymous", payload=body.payload or {}, processed=1)
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return {"status": "received", "event_id": ev.id}
