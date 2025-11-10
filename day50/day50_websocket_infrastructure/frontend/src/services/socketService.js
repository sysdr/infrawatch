import { io } from 'socket.io-client';

class SocketService {
  constructor() {
    this.socket = null;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect(token) {
    if (this.socket?.connected) {
      console.log('Socket already connected');
      return this.socket;
    }

    const serverUrl = process.env.REACT_APP_WS_URL || 'http://localhost:5000';
    
    this.socket = io(serverUrl, {
      auth: { token },
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: this.maxReconnectAttempts,
      transports: ['websocket', 'polling']
    });

    this.setupEventHandlers();
    return this.socket;
  }

  setupEventHandlers() {
    this.socket.on('connect', () => {
      console.log('WebSocket connected:', this.socket.id);
      this.reconnectAttempts = 0;
      this.emit('connection_status', { connected: true, socketId: this.socket.id });
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      this.emit('connection_status', { connected: false, reason });
    });

    this.socket.on('connect_error', (error) => {
      console.error('Connection error:', error);
      this.reconnectAttempts++;
      this.emit('connection_error', { error: error.message, attempts: this.reconnectAttempts });
    });

    this.socket.on('reconnect', (attemptNumber) => {
      console.log('Reconnected after', attemptNumber, 'attempts');
      this.emit('reconnected', { attempts: attemptNumber });
    });

    this.socket.on('reconnect_attempt', (attemptNumber) => {
      console.log('Reconnection attempt:', attemptNumber);
      this.emit('reconnect_attempt', { attempts: attemptNumber });
    });

    this.socket.on('connected', (data) => {
      console.log('Server confirmed connection:', data);
      this.emit('server_connected', data);
    });

    this.socket.on('error', (error) => {
      console.error('Socket error:', error);
      this.emit('socket_error', error);
    });
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);

    if (this.socket) {
      this.socket.on(event, callback);
    }
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }

    if (this.socket) {
      this.socket.off(event, callback);
    }
  }

  emit(event, data) {
    const callbacks = this.listeners.get(event) || [];
    callbacks.forEach(callback => callback(data));
  }

  send(event, data, callback) {
    if (this.socket?.connected) {
      this.socket.emit(event, data, callback);
    } else {
      console.error('Socket not connected');
    }
  }

  joinRoom(room) {
    this.send('join_room', { room });
  }

  leaveRoom(room) {
    this.send('leave_room', { room });
  }

  sendMessage(room, message) {
    this.send('send_message', { room, message });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    this.listeners.clear();
  }

  isConnected() {
    return this.socket?.connected || false;
  }
}

export default new SocketService();
