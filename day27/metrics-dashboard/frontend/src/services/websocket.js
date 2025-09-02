import { io } from 'socket.io-client';

class MetricsWebSocket {
  constructor() {
    this.socket = null;
    this.subscribers = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect() {
    this.socket = new WebSocket('ws://localhost:8000/ws');
    
    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };

    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      this.attemptReconnect();
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  handleMessage(data) {
    if (data.type === 'metric_update') {
      const callbacks = this.subscribers.get(data.metric_name) || [];
      callbacks.forEach(callback => callback(data));
    }
  }

  subscribe(metricName, callback) {
    if (!this.subscribers.has(metricName)) {
      this.subscribers.set(metricName, []);
      this.sendMessage({
        type: 'subscribe',
        metric_name: metricName
      });
    }
    
    this.subscribers.get(metricName).push(callback);
  }

  unsubscribe(metricName, callback) {
    const callbacks = this.subscribers.get(metricName) || [];
    const index = callbacks.indexOf(callback);
    
    if (index > -1) {
      callbacks.splice(index, 1);
      
      if (callbacks.length === 0) {
        this.subscribers.delete(metricName);
        this.sendMessage({
          type: 'unsubscribe',
          metric_name: metricName
        });
      }
    }
  }

  sendMessage(message) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
        this.connect();
      }, 2000 * this.reconnectAttempts);
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.subscribers.clear();
  }
}

export const metricsWebSocket = new MetricsWebSocket();
