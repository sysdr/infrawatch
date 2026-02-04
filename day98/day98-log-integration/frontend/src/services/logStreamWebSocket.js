/**
 * Module-level WebSocket for log stream.
 * Lives outside React lifecycle - avoids "closed before connection established"
 * when React Strict Mode double-mounts components.
 */

const getWsUrl = () => {
  const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  return apiUrl.replace(/^http/, 'ws') + '/api/logs/stream';
};

let ws = null;
let subscribers = new Set();
let reconnectTimeout = null;
let connectDelayTimeout = null;
let filters = {};

function connect() {
  if (ws?.readyState === WebSocket.OPEN) return;
  if (ws?.readyState === WebSocket.CONNECTING) return;

  ws = new WebSocket(getWsUrl());

  ws.onopen = () => {
    if (subscribers.size === 0) {
      ws.close();
      ws = null;
      return;
    }
    notify({ type: 'status', connected: true });
    ws.send(JSON.stringify({ type: 'subscribe', filters }));
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'ping') {
      ws.send(JSON.stringify({ type: 'pong' }));
      return;
    }
    if (data.type === 'subscribed') return;
    notify({ type: 'log', data });
  };

  ws.onerror = () => {
    notify({ type: 'status', connected: false, error: true });
  };

  ws.onclose = () => {
    ws = null;
    notify({ type: 'status', connected: false });
    reconnectTimeout = setTimeout(connect, 5000);
  };
}

function notify(msg) {
  subscribers.forEach((cb) => cb(msg));
}

export function subscribe(callback) {
  subscribers.add(callback);
  if (subscribers.size === 1) {
    if (connectDelayTimeout) clearTimeout(connectDelayTimeout);
    connectDelayTimeout = setTimeout(() => {
      connectDelayTimeout = null;
      if (subscribers.size > 0) connect();
    }, 150);
  } else if (ws?.readyState === WebSocket.OPEN) {
    callback({ type: 'status', connected: true });
  }
}

export function unsubscribe(callback) {
  subscribers.delete(callback);
  if (connectDelayTimeout) {
    clearTimeout(connectDelayTimeout);
    connectDelayTimeout = null;
  }
  if (subscribers.size === 0 && ws) {
    clearTimeout(reconnectTimeout);
    reconnectTimeout = null;
    if (ws.readyState === WebSocket.OPEN) {
      ws.close();
    }
    if (ws.readyState !== WebSocket.CONNECTING) {
      ws = null;
    }
  }
}

export function setFilters(newFilters) {
  filters = { ...newFilters };
  if (ws?.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'subscribe', filters }));
  }
}
