import { onLCP, onFID, onCLS, onTTFB, onINP } from 'web-vitals';

const SESSION_ID = Math.random().toString(36).slice(2);
const API_BASE   = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const BATCH_MS   = 2000;

let pending = [];
let timer   = null;

function flush() {
  if (!pending.length) return;
  const toSend = [...pending];
  pending = [];
  const payload = {
    metrics: toSend.map(m => ({
      name: m.name,
      value: m.value,
      route: window.location.pathname,
      sessionId: SESSION_ID,
      connectionType: navigator?.connection?.effectiveType ?? 'unknown',
    })),
  };
  // Use sendBeacon so it survives page unload
  const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
  if (navigator.sendBeacon) {
    navigator.sendBeacon(`${API_BASE}/api/metrics/vitals`, blob);
  } else {
    fetch(`${API_BASE}/api/metrics/vitals`, { method: 'POST', body: blob, headers: { 'Content-Type': 'application/json' } }).catch(() => {});
  }
}

function queue(metric) {
  pending.push(metric);
  clearTimeout(timer);
  timer = setTimeout(flush, BATCH_MS);
}

export function initVitalsReporting() {
  onLCP(queue);
  onFID(queue);
  onCLS(queue);
  onTTFB(queue);
  onINP(queue);
  window.addEventListener('pagehide', flush);
  // Also report bundle chunk loads via PerformanceObserver
  if ('PerformanceObserver' in window) {
    const obs = new PerformanceObserver(list => {
      const chunks = list.getEntries()
        .filter(e => e.initiatorType === 'script' && e.name.includes('chunk'))
        .map(e => ({
          name: e.name.split('/').pop().split('?')[0],
          sizeBytes: e.transferSize || 0,
          loadTimeMs: Math.round(e.duration),
          cached: e.transferSize === 0 && e.decodedBodySize > 0,
          route: window.location.pathname,
          sessionId: SESSION_ID,
        }));
      if (!chunks.length) return;
      fetch(`${API_BASE}/api/metrics/bundles`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chunks }),
      }).catch(() => {});
    });
    try { obs.observe({ type: 'resource', buffered: true }); } catch (_) {}
  }
}

export { SESSION_ID };
