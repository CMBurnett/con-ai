import { create } from 'zustand';
import { Agent, AgentUpdate } from '@/types/agents';

interface AgentStore {
  agents: Agent[];
  activeAgents: string[];
  recentUpdates: AgentUpdate[];
  
  // Actions
  setAgents: (agents: Agent[]) => void;
  updateAgent: (agentId: string, updates: Partial<Agent>) => void;
  addAgentUpdate: (update: AgentUpdate) => void;
  clearUpdates: () => void;
  startAgent: (agentId: string, taskType: string, parameters?: any) => void;
  stopAgent: (agentId: string) => void;
}

export const useAgentStore = create<AgentStore>((set, get) => ({
  agents: [],
  activeAgents: [],
  recentUpdates: [],

  setAgents: (agents) => set({ agents }),

  updateAgent: (agentId, updates) => set((state) => ({
    agents: state.agents.map((agent) => 
      agent.id === agentId ? { ...agent, ...updates } : agent
    ),
  })),

  addAgentUpdate: (update) => set((state) => {
    // Update the agent status based on the update
    const updatedAgents = state.agents.map((agent) => 
      agent.id === update.agentId 
        ? { ...agent, status: update.status, progress: update.progress, lastRun: update.timestamp }
        : agent
    );

    // Update active agents list
    const activeAgents = updatedAgents
      .filter(agent => agent.status === 'running')
      .map(agent => agent.id);

    return {
      agents: updatedAgents,
      activeAgents,
      recentUpdates: [...state.recentUpdates.slice(-99), update], // Keep last 100 updates
    };
  }),

  clearUpdates: () => set({ recentUpdates: [] }),

  startAgent: (agentId, taskType, parameters = {}) => {
    // This will be called by components to trigger agent start
    // The actual WebSocket command will be sent by the component
    set((state) => ({
      agents: state.agents.map((agent) => 
        agent.id === agentId 
          ? { ...agent, status: 'running', progress: 0 }
          : agent
      ),
    }));
  },

  stopAgent: (agentId) => {
    // This will be called by components to trigger agent stop
    set((state) => ({
      agents: state.agents.map((agent) => 
        agent.id === agentId 
          ? { ...agent, status: 'idle', progress: 0 }
          : agent
      ),
    }));
  },
}));
