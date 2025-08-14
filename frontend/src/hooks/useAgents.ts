import { useState, useCallback } from 'react';
import { Agent, AgentConfig } from '@/types/agents';
import { useWebSocket } from './useWebSocket';

export const useAgents = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(false);
  const { sendCommand } = useWebSocket();

  const startAgent = useCallback(async (agentId: string, config: AgentConfig) => {
    setLoading(true);
    try {
      sendCommand({
        type: 'start_agent',
        agent_id: agentId,
        config: config,
      });
      
      setAgents(prev => prev.map(agent => 
        agent.id === agentId 
          ? { ...agent, status: 'running', progress: 0 }
          : agent
      ));
    } catch (error) {
      console.error('Failed to start agent:', error);
    } finally {
      setLoading(false);
    }
  }, [sendCommand]);

  const stopAgent = useCallback(async (agentId: string) => {
    try {
      sendCommand({
        type: 'stop_agent',
        agent_id: agentId,
      });
      
      setAgents(prev => prev.map(agent => 
        agent.id === agentId 
          ? { ...agent, status: 'idle', progress: 0 }
          : agent
      ));
    } catch (error) {
      console.error('Failed to stop agent:', error);
    }
  }, [sendCommand]);

  return {
    agents,
    loading,
    startAgent,
    stopAgent,
    setAgents,
  };
};