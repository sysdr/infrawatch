import { useState, useEffect, useCallback, useRef } from 'react';

const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws/security/events';

// Singleton WebSocket manager to prevent multiple connections
class WebSocketManager {
  constructor() {
    this.ws = null;
    this.listeners = new Set();
    this.reconnectAttempt = 0;
    this.isConnecting = false;
    this.heartbeatInterval = null;
    this.reconnectTimeout = null;
    this.isManuallyClosed = false;
    this.lastConnectTime = 0;
    this.lastCloseTime = 0;
    this.connectionStartTime = 0;
    this.failureCount = 0;
    this.lastFailureTime = 0;
    this.circuitBreakerOpen = false;
    this.circuitBreakerOpenTime = 0;
    
    // Circuit breaker settings
    this.maxFailures = 3; // Open circuit after 3 rapid failures
    this.circuitBreakerTimeout = 30000; // Keep circuit open for 30 seconds
    this.minReconnectDelay = 10000; // Minimum 10 seconds between attempts
    this.maxReconnectAttempts = 3; // Stop after 3 attempts
    this.minConnectionLifetime = 5000; // Connection must stay open 5 seconds to be stable
  }

  connect() {
    // Circuit breaker check - don't attempt if circuit is open
    const now = Date.now();
    if (this.circuitBreakerOpen) {
      const timeSinceOpen = now - this.circuitBreakerOpenTime;
      if (timeSinceOpen < this.circuitBreakerTimeout) {
        // Circuit still open, don't attempt connection
        return;
      } else {
        // Circuit breaker timeout expired, reset
        this.circuitBreakerOpen = false;
        this.failureCount = 0;
      }
    }

    // Prevent multiple simultaneous connection attempts
    if (this.isConnecting) {
      return;
    }

    // Don't reconnect if already connected and healthy
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return;
    }

    // If connecting, wait for it to complete
    if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
      return;
    }

    // Don't connect if manually closed
    if (this.isManuallyClosed) {
      return;
    }

    // Enforce minimum delay between reconnection attempts
    const timeSinceLastConnect = now - this.lastConnectTime;
    if (timeSinceLastConnect < this.minReconnectDelay) {
      const waitTime = this.minReconnectDelay - timeSinceLastConnect;
      this.reconnectTimeout = setTimeout(() => {
        this.connect();
      }, waitTime);
      return;
    }

    // Stop reconnecting if we've exceeded max attempts
    if (this.reconnectAttempt >= this.maxReconnectAttempts) {
      // Open circuit breaker
      this.circuitBreakerOpen = true;
      this.circuitBreakerOpenTime = now;
      return;
    }

    this.isConnecting = true;
    this.lastConnectTime = now;

    try {
      // Clear any existing reconnect timeout
      if (this.reconnectTimeout) {
        clearTimeout(this.reconnectTimeout);
        this.reconnectTimeout = null;
      }

      // Clean up existing connection if it's in a bad state
      if (this.ws) {
        const state = this.ws.readyState;
        if (state !== WebSocket.OPEN && state !== WebSocket.CONNECTING) {
          try {
            this.ws.onerror = null;
            this.ws.onclose = null;
            this.ws.onopen = null;
            this.ws.onmessage = null;
            if (this.heartbeatInterval) {
              clearInterval(this.heartbeatInterval);
              this.heartbeatInterval = null;
            }
            if (state !== WebSocket.CLOSED) {
              this.ws.close();
            }
          } catch (e) {
            // Ignore cleanup errors
          }
          this.ws = null;
        } else {
          this.isConnecting = false;
          return;
        }
      }

      const ws = new WebSocket(WS_URL);
      this.ws = ws;

      ws.onopen = () => {
        const connectTime = Date.now();
        this.isConnecting = false;
        this.reconnectAttempt = 0;
        this.failureCount = 0;
        this.isManuallyClosed = false;
        this.lastConnectTime = connectTime;
        this.connectionStartTime = connectTime;
        this.circuitBreakerOpen = false;

        if (ws.readyState !== WebSocket.OPEN) {
          return;
        }

        // Notify all listeners
        this.listeners.forEach(listener => {
          if (listener.onConnect) listener.onConnect();
        });

        // Start heartbeat
        this.heartbeatInterval = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN && ws === this.ws) {
            try {
              ws.send(JSON.stringify({ type: 'ping' }));
            } catch (error) {
              clearInterval(this.heartbeatInterval);
              this.heartbeatInterval = null;
            }
          } else {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          // Handle control messages silently
          if (data.type === 'pong' || data.type === 'keepalive' || data.type === 'connected' || data.type === 'subscribed') {
            return;
          }

          // Only add actual security events
          if (data.event_id || data.event_type) {
            this.listeners.forEach(listener => {
              if (listener.onEvent) listener.onEvent(data);
            });
          }
        } catch (error) {
          // Silently handle parse errors
        }
      };

      ws.onerror = () => {
        this.isConnecting = false;
      };

      ws.onclose = (event) => {
        const closeCode = event.code;
        const closeTime = Date.now();
        this.isConnecting = false;
        this.lastCloseTime = closeTime;

        // Check if connection was unstable
        const connectionLifetime = this.connectionStartTime > 0 
          ? closeTime - this.connectionStartTime 
          : 0;
        const wasUnstable = connectionLifetime > 0 && connectionLifetime < this.minConnectionLifetime;

        // Track failures for circuit breaker
        if (wasUnstable || closeCode !== 1000) {
          this.failureCount++;
          this.lastFailureTime = closeTime;
          
          // Open circuit breaker if too many rapid failures
          if (this.failureCount >= this.maxFailures) {
            this.circuitBreakerOpen = true;
            this.circuitBreakerOpenTime = closeTime;
          }
        } else {
          // Successful connection, reset failure count
          this.failureCount = 0;
        }

        // Clear WebSocket reference
        if (this.ws === ws) {
          this.ws = null;
        }

        if (this.heartbeatInterval) {
          clearInterval(this.heartbeatInterval);
          this.heartbeatInterval = null;
        }

        // Notify listeners
        this.listeners.forEach(listener => {
          if (listener.onDisconnect) listener.onDisconnect();
        });

        // Only reconnect if not manually closed, not normal closure, and circuit breaker is closed
        if (!this.isManuallyClosed && closeCode !== 1000 && closeCode !== 1001 && !this.circuitBreakerOpen) {
          if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = null;
          }

          if (this.reconnectAttempt >= this.maxReconnectAttempts) {
            this.circuitBreakerOpen = true;
            this.circuitBreakerOpenTime = closeTime;
            return;
          }

          // Longer backoff for unstable connections
          let backoffTime;
          if (wasUnstable) {
            backoffTime = Math.max(20000, Math.min(60000, 20000 * (this.reconnectAttempt + 1)));
          } else {
            backoffTime = Math.max(
              this.minReconnectDelay, 
              Math.min(1000 * Math.pow(2, this.reconnectAttempt), 60000)
            );
          }

          this.reconnectAttempt = this.reconnectAttempt + 1;

          this.reconnectTimeout = setTimeout(() => {
            if (!this.isManuallyClosed && 
                !this.circuitBreakerOpen &&
                (!this.ws || this.ws.readyState === WebSocket.CLOSED || this.ws.readyState === WebSocket.CLOSING) &&
                this.reconnectAttempt <= this.maxReconnectAttempts) {
              this.connect();
            }
          }, backoffTime);
        } else {
          if (this.isManuallyClosed || closeCode === 1000 || closeCode === 1001) {
            this.reconnectAttempt = 0;
            this.failureCount = 0;
            this.connectionStartTime = 0;
            this.circuitBreakerOpen = false;
          }
        }
      };
    } catch (error) {
      this.isConnecting = false;
      this.failureCount++;
      if (this.failureCount >= this.maxFailures) {
        this.circuitBreakerOpen = true;
        this.circuitBreakerOpenTime = Date.now();
      }
    }
  }

  disconnect() {
    this.isManuallyClosed = true;

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }

    if (this.ws) {
      try {
        this.ws.onerror = null;
        this.ws.onclose = null;
        this.ws.onopen = null;
        this.ws.onmessage = null;
        
        if (this.ws.readyState !== WebSocket.CLOSED && this.ws.readyState !== WebSocket.CLOSING) {
          this.ws.close(1000, 'Manual disconnect');
        }
      } catch (e) {
        // Ignore errors
      }
      this.ws = null;
    }
    
    this.reconnectAttempt = 0;
    this.failureCount = 0;
    this.circuitBreakerOpen = false;
  }

  subscribe(listener) {
    this.listeners.add(listener);
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      this.connect();
    }
  }

  unsubscribe(listener) {
    this.listeners.delete(listener);
    if (this.listeners.size === 0 && !this.isConnecting) {
      setTimeout(() => {
        if (this.listeners.size === 0) {
          this.disconnect();
        }
      }, 100);
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

// Global singleton instance
const wsManager = new WebSocketManager();

export const useWebSocket = (filters = {}) => {
  const [events, setEvents] = useState([]);
  const [isConnected, setIsConnected] = useState(() => wsManager.isConnected());
  const listenerRef = useRef(null);
  const isSubscribedRef = useRef(false);

  useEffect(() => {
    if (isSubscribedRef.current) {
      return;
    }

    listenerRef.current = {
      onConnect: () => {
        setIsConnected(true);
        if (Object.keys(filters).length > 0) {
          setTimeout(() => {
            if (wsManager.isConnected()) {
              wsManager.send({
                type: 'subscribe',
                filters: filters
              });
            }
          }, 500);
        }
      },
      onDisconnect: () => {
        setIsConnected(false);
      },
      onError: () => {
        setIsConnected(false);
      },
      onEvent: (event) => {
        setEvents((prevEvents) => {
          const newEvents = [event, ...prevEvents];
          return newEvents.slice(0, 10000);
        });
      }
    };

    wsManager.subscribe(listenerRef.current);
    isSubscribedRef.current = true;
    
    if (wsManager.isConnected()) {
      setIsConnected(true);
    }

    return () => {
      if (listenerRef.current) {
        wsManager.unsubscribe(listenerRef.current);
        listenerRef.current = null;
        isSubscribedRef.current = false;
      }
    };
  }, []);

  useEffect(() => {
    if (wsManager.isConnected() && Object.keys(filters).length > 0) {
      wsManager.send({
        type: 'subscribe',
        filters: filters
      });
    }
  }, [filters]);

  const clearEvents = useCallback(() => {
    setEvents([]);
  }, []);

  return { events, isConnected, clearEvents };
};
