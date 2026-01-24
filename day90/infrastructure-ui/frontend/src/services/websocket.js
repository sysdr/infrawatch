import { io } from 'socket.io-client';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = new Map();
  }

  connect(clientId) {
    // Prevent multiple connections
    if (this.socket) {
      if (this.socket.readyState === WebSocket.CONNECTING || this.socket.readyState === WebSocket.OPEN) {
        return;
      }
      // Clean up any existing closed socket
      if (this.socket.readyState === WebSocket.CLOSED) {
        this.socket = null;
      }
    }
    
    // Using native WebSocket for simplicity
    try {
      this.socket = new WebSocket(`ws://localhost:8000/ws/${clientId}`);
      
      this.socket.onopen = () => {
        console.log('WebSocket connected');
      };
      
      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifyListeners(data);
        } catch (e) {
          // Silently handle parse errors
        }
      };
      
      this.socket.onerror = (error) => {
        // Suppress error logs in development - connection may not be critical
        // Only log if socket was actually trying to connect
        if (this.socket && this.socket.readyState === WebSocket.CONNECTING) {
          // Silently handle - WebSocket may not be available
        }
      };
      
      this.socket.onclose = (event) => {
        // Only reconnect if it wasn't a manual close (code 1000) and wasn't clean
        // Don't reconnect if it was closed before connection (code 1006 or immediate close)
        if (event.code !== 1000 && event.code !== 1006 && !event.wasClean && this.socket) {
          // Only reconnect if socket was actually connected
          const wasConnected = event.code !== 1006;
          if (wasConnected) {
            console.log('WebSocket closed unexpectedly, reconnecting in 3 seconds...');
            setTimeout(() => {
              if (!this.socket || this.socket.readyState === WebSocket.CLOSED) {
                this.connect(clientId);
              }
            }, 3000);
          }
        }
        // Clear socket reference
        if (this.socket && this.socket.readyState === WebSocket.CLOSED) {
          this.socket = null;
        }
      };
    } catch (error) {
      // Silently handle connection errors
      this.socket = null;
    }
  }

  disconnect() {
    if (this.socket) {
      // Only close if socket is actually open or connecting
      // Don't close if already closed or closing
      if (this.socket.readyState === WebSocket.OPEN) {
        this.socket.close(1000, 'Manual disconnect');
      } else if (this.socket.readyState === WebSocket.CONNECTING) {
        // If still connecting, wait a bit then close
        setTimeout(() => {
          if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.close(1000, 'Manual disconnect');
          } else if (this.socket) {
            this.socket.close();
          }
        }, 100);
      }
      this.socket = null;
    }
  }

  subscribe(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  notifyListeners(data) {
    const event = data.type || 'message';
    const callbacks = this.listeners.get(event) || [];
    callbacks.forEach(callback => callback(data));
  }

  send(message) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    }
  }
}

export default new WebSocketService();
