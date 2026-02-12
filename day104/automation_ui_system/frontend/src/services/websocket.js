import { io } from 'socket.io-client';

const WS_URL = process.env.REACT_APP_WS_URL || 'http://localhost:8000';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = {};
  }
  connect() {
    if (!this.socket) {
      this.socket = io(WS_URL, { path: '/socket.io', transports: ['websocket', 'polling'] });
      this.socket.on('connect', () => console.log('WebSocket connected'));
      this.socket.on('disconnect', () => console.log('WebSocket disconnected'));
      this.socket.on('workflow_update', (data) => {
        if (this.listeners['workflow_update']) this.listeners['workflow_update'].forEach(cb => cb(data));
      });
    }
    return this.socket;
  }
  disconnect() {
    if (this.socket) { this.socket.disconnect(); this.socket = null; }
  }
  on(event, callback) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(callback);
  }
  off(event, callback) {
    if (this.listeners[event]) this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
  }
}

export default new WebSocketService();
