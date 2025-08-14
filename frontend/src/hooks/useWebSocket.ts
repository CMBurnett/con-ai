import { useEffect, useState, useCallback } from 'react';
import { AgentUpdate } from '@/types/agents';

interface UseWebSocketReturn {
  isConnected: boolean;
  agentUpdates: AgentUpdate[];
  sendCommand: (command: any) => void;
  clearUpdates: () => void;
}

export const useWebSocket = (): UseWebSocketReturn => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [agentUpdates, setAgentUpdates] = useState<AgentUpdate[]>([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8080/ws');
    
    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const update: AgentUpdate = JSON.parse(event.data);
        update.timestamp = new Date();
        setAgentUpdates(prev => [...prev.slice(-99), update]); // Keep last 100 updates
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, []);

  const sendCommand = useCallback((command: any) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(command));
    }
  }, [socket, isConnected]);

  const clearUpdates = useCallback(() => {
    setAgentUpdates([]);
  }, []);

  return {
    isConnected,
    agentUpdates,
    sendCommand,
    clearUpdates,
  };
};