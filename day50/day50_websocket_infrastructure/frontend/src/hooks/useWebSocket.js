import { useState, useEffect, useCallback } from 'react';
import socketService from '../services/socketService';

export const useWebSocket = (token) => {
  const [isConnected, setIsConnected] = useState(false);
  const [socketId, setSocketId] = useState(null);
  const [error, setError] = useState(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  useEffect(() => {
    if (!token) return;

    socketService.connect(token);

    const handleConnectionStatus = (data) => {
      setIsConnected(data.connected);
      if (data.connected) {
        setSocketId(data.socketId);
        setError(null);
        setReconnectAttempts(0);
      }
    };

    const handleServerConnected = (data) => {
      setSocketId(data.socket_id);
      setIsConnected(true);
    };

    const handleConnectionError = (data) => {
      setError(data.error);
      setReconnectAttempts(data.attempts);
    };

    const handleReconnectAttempt = (data) => {
      setReconnectAttempts(data.attempts);
    };

    socketService.on('connection_status', handleConnectionStatus);
    socketService.on('server_connected', handleServerConnected);
    socketService.on('connection_error', handleConnectionError);
    socketService.on('reconnect_attempt', handleReconnectAttempt);

    return () => {
      socketService.off('connection_status', handleConnectionStatus);
      socketService.off('server_connected', handleServerConnected);
      socketService.off('connection_error', handleConnectionError);
      socketService.off('reconnect_attempt', handleReconnectAttempt);
    };
  }, [token]);

  const joinRoom = useCallback((room) => {
    socketService.joinRoom(room);
  }, []);

  const leaveRoom = useCallback((room) => {
    socketService.leaveRoom(room);
  }, []);

  const sendMessage = useCallback((room, message) => {
    socketService.sendMessage(room, message);
  }, []);

  return {
    isConnected,
    socketId,
    error,
    reconnectAttempts,
    joinRoom,
    leaveRoom,
    sendMessage,
    on: socketService.on.bind(socketService),
    off: socketService.off.bind(socketService)
  };
};
