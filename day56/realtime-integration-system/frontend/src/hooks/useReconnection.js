import { useState, useEffect } from 'react';

export const useReconnection = (isConnected) => {
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const [isReconnecting, setIsReconnecting] = useState(false);

  useEffect(() => {
    if (!isConnected) {
      setIsReconnecting(true);
      setReconnectAttempts(prev => prev + 1);
    } else {
      setIsReconnecting(false);
      setReconnectAttempts(0);
    }
  }, [isConnected]);

  return {
    reconnectAttempts,
    isReconnecting
  };
};
