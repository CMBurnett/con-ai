import { useEffect, useState, useCallback, useRef } from 'react';
import { AgentUpdate } from '@/types/agents';
import { useAgentStore } from '@/stores/agentStore';
import { useUIStore } from '@/stores/uiStore';

interface UseWebSocketReturn {
  isConnected: boolean;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  sendCommand: (command: any) => void;
  sendAgentStart: (agentId: string, agentType: string, taskType: string, parameters?: any) => void;
  sendAgentStop: (agentId: string) => void;
  sendPing: () => void;
}

export const useWebSocket = (): UseWebSocketReturn => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  
  const addAgentUpdate = useAgentStore(state => state.addAgentUpdate);
  const addNotification = useUIStore(state => state.addNotification);
  const setOnlineStatus = useUIStore(state => state.setOnlineStatus);

  const connect = useCallback(() => {
    if (socket?.readyState === WebSocket.OPEN) return;
    
    setConnectionStatus('connecting');
    const ws = new WebSocket('ws://localhost:8080/ws');
    
    ws.onopen = () => {
      setIsConnected(true);
      setConnectionStatus('connected');
      setOnlineStatus(true);
      reconnectAttempts.current = 0;
      console.log('WebSocket connected to Orchestra backend');
      
      addNotification({
        type: 'success',
        title: 'Connected',
        message: 'Real-time connection established',
        duration: 3000,
      });
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        
        // Handle different message types from Orchestra backend
        switch (message.type) {
          case 'connection_established':
            console.log('Connection established with client ID:', message.client_id);
            break;
            
          case 'agent_update':
            // Convert Orchestra agent update format to our AgentUpdate type
            const agentUpdate: AgentUpdate = {
              agentId: message.data.agentId,
              status: message.data.status as any,
              progress: message.data.progress || 0,
              message: message.data.message || '',
              data: message.data.data,
              timestamp: new Date(message.timestamp),
            };
            addAgentUpdate(agentUpdate);
            break;
            
          case 'command_received':
            addNotification({
              type: 'info',
              title: 'Command Received',
              message: message.message,
              duration: 2000,
            });
            break;
            
          case 'error':
            addNotification({
              type: 'error',
              title: 'WebSocket Error',
              message: message.message,
              duration: 5000,
            });
            break;
            
          case 'pong':
            // Heartbeat response - connection is healthy
            break;
            
          default:
            console.log('Unknown message type:', message.type, message);
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
        addNotification({
          type: 'error',
          title: 'Message Parse Error',
          message: 'Failed to parse incoming message',
          duration: 3000,
        });
      }
    };

    ws.onclose = (event) => {
      setIsConnected(false);
      setConnectionStatus('disconnected');
      setOnlineStatus(false);
      console.log('WebSocket disconnected:', event.code, event.reason);
      
      // Attempt to reconnect if not a manual close
      if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
        reconnectAttempts.current++;
        
        addNotification({
          type: 'warning',
          title: 'Connection Lost',
          message: `Reconnecting in ${delay/1000}s (attempt ${reconnectAttempts.current}/${maxReconnectAttempts})`,
          duration: delay,
        });
        
        reconnectTimeoutRef.current = setTimeout(connect, delay);
      } else if (reconnectAttempts.current >= maxReconnectAttempts) {
        setConnectionStatus('error');
        addNotification({
          type: 'error',
          title: 'Connection Failed',
          message: 'Maximum reconnection attempts reached',
        });
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionStatus('error');
      setIsConnected(false);
    };

    setSocket(ws);
  }, [addAgentUpdate, addNotification, setOnlineStatus]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      socket?.close(1000, 'Component unmounting');
    };
  }, [connect]);

  const sendCommand = useCallback((command: any) => {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(command));
    } else {
      addNotification({
        type: 'error',
        title: 'Connection Error',
        message: 'WebSocket is not connected',
        duration: 3000,
      });
    }
  }, [socket, addNotification]);

  const sendAgentStart = useCallback((agentId: string, agentType: string, taskType: string, parameters = {}) => {
    sendCommand({
      type: 'start_agent',
      agent_id: agentId,
      agent_type: agentType,
      task_type: taskType,
      config: parameters,
    });
  }, [sendCommand]);

  const sendAgentStop = useCallback((agentId: string) => {
    sendCommand({
      type: 'stop_agent',
      agent_id: agentId,
    });
  }, [sendCommand]);

  const sendPing = useCallback(() => {
    sendCommand({
      type: 'ping',
      timestamp: new Date().toISOString(),
    });
  }, [sendCommand]);

  return {
    isConnected,
    connectionStatus,
    sendCommand,
    sendAgentStart,
    sendAgentStop,
    sendPing,
  };
};