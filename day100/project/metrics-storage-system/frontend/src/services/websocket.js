class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.messageHandlers = [];
  }
  connect() {
    try {
      const host = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
      const wsUrl = `ws://${host}:8000/ws`;
      this.ws = new WebSocket(wsUrl);
      this.ws.onopen = () => { this.isConnected = true; this.reconnectAttempts = 0; };
      this.ws.onmessage = (e) => {
        try { this.messageHandlers.forEach(h => h(JSON.parse(e.data))); } catch (_) {}
      };
      this.ws.onclose = () => { this.isConnected = false; this.attemptReconnect(); };
      this.ws.onerror = () => { this.isConnected = false; };
    } catch (e) { this.attemptReconnect(); }
  }
  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => this.connect(), 1000 * this.reconnectAttempts);
    }
  }
  addMessageHandler(h) { this.messageHandlers.push(h); }
  removeMessageHandler(h) {
    const i = this.messageHandlers.indexOf(h);
    if (i > -1) this.messageHandlers.splice(i, 1);
  }
  disconnect() { if (this.ws) { this.ws.close(); this.ws = null; } this.isConnected = false; }
  get isConnected() { return this._connected || false; }
  set isConnected(v) { this._connected = v; }
}
export default new WebSocketService();
