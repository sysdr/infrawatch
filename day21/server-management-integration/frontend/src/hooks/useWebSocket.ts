import { useEffect, useCallback, useRef } from 'react';
import { wsService, WebSocketMessage } from '../services/websocket';

export const useWebSocket = (
  onMessage?: (message: WebSocketMessage) => void,
  onConnect?: () => void,
  onDisconnect?: () => void
) => {
  const onMessageRef = useRef(onMessage);
  const onConnectRef = useRef(onConnect);
  const onDisconnectRef = useRef(onDisconnect);

  // Update refs when callbacks change
  useEffect(() => {
    onMessageRef.current = onMessage;
    onConnectRef.current = onConnect;
    onDisconnectRef.current = onDisconnect;
  });

  const handleMessage = useCallback((message: WebSocketMessage) => {
    onMessageRef.current?.(message);
  }, []);

  const handleConnect = useCallback(() => {
    onConnectRef.current?.();
  }, []);

  const handleDisconnect = useCallback(() => {
    onDisconnectRef.current?.();
  }, []);

  useEffect(() => {
    wsService.on('connected', handleConnect);
    wsService.on('server_update', handleMessage);
    wsService.on('server_created', handleMessage);
    wsService.on('server_deleted', handleMessage);

    // Connect to WebSocket
    wsService.connect().catch(console.error);

    return () => {
      wsService.off('connected', handleConnect);
      wsService.off('server_update', handleMessage);
      wsService.off('server_created', handleMessage);
      wsService.off('server_deleted', handleMessage);
    };
  }, [handleMessage, handleConnect, handleDisconnect]);

  const sendMessage = useCallback((message: any) => {
    wsService.send(message);
  }, []);

  return { sendMessage };
};
