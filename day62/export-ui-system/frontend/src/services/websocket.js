import { io } from 'socket.io-client';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.connected = false;
  }

  connect(url = 'http://localhost:8000') {
    if (this.socket && this.connected) {
      return this.socket;
    }

    this.socket = io(url, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.connected = true;
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      this.connected = false;
    });

    return this.socket;
  }

  subscribe(jobId, callback) {
    if (!this.socket) {
      this.connect();
    }

    this.socket.emit('subscribe', { job_id: jobId });

    this.socket.on('progress', (data) => {
      if (data.job_id === jobId) {
        callback(data);
      }
    });
  }

  unsubscribe(jobId) {
    if (this.socket) {
      this.socket.emit('unsubscribe', { job_id: jobId });
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.connected = false;
    }
  }
}

export default new WebSocketService();
