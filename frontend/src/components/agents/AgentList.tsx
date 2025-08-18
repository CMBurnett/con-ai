import React from 'react';
import { Agent } from '@/types/agents';
import { AgentCard } from './AgentCard';
import { useWebSocket } from '@/hooks/useWebSocket';

interface AgentListProps {
  agents: Agent[];
  onConfigureAgent?: (agentId: string) => void;
}

export const AgentList: React.FC<AgentListProps> = ({ agents, onConfigureAgent }) => {
  const { sendAgentStart, sendAgentStop } = useWebSocket();

  const handleStartAgent = (agentId: string) => {
    const agent = agents.find(a => a.id === agentId);
    if (agent) {
      // Start agent with a default task based on agent type
      const defaultTasks = {
        procore: 'extract_project_data',
        autodesk: 'coordinate_models',
        primavera: 'analyze_schedule',
        msproject: 'analyze_schedule',
        demo: 'simulation'
      };
      
      const taskType = defaultTasks[agent.type as keyof typeof defaultTasks] || 'extract_project_data';
      sendAgentStart(agentId, agent.type, taskType, agent.config.settings);
    }
  };

  const handleStopAgent = (agentId: string) => {
    sendAgentStop(agentId);
  };

  if (!agents || agents.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">🤖</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No agents configured</h3>
        <p className="text-gray-500">
          Set up your first construction automation agent to get started.
        </p>
      </div>
    );
  }

  // Group agents by type for better organization
  const groupedAgents = agents.reduce((groups, agent) => {
    const type = agent.type;
    if (!groups[type]) {
      groups[type] = [];
    }
    groups[type].push(agent);
    return groups;
  }, {} as Record<string, Agent[]>);

  const getGroupTitle = (type: string) => {
    switch (type) {
      case 'procore':
        return 'Procore Agents';
      case 'autodesk':
        return 'Autodesk Construction Cloud Agents';
      case 'primavera':
        return 'Oracle Primavera P6 Agents';
      case 'msproject':
        return 'Microsoft Project Agents';
      case 'demo':
        return 'Demo & Testing Agents';
      default:
        return 'Other Agents';
    }
  };

  return (
    <div className="space-y-8">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-gray-900">{agents.length}</div>
          <div className="text-sm text-gray-500">Total Agents</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-green-600">
            {agents.filter(a => a.status === 'running').length}
          </div>
          <div className="text-sm text-gray-500">Running</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-blue-600">
            {agents.filter(a => a.status === 'idle').length}
          </div>
          <div className="text-sm text-gray-500">Idle</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-red-600">
            {agents.filter(a => a.status === 'error').length}
          </div>
          <div className="text-sm text-gray-500">Errors</div>
        </div>
      </div>

      {/* Agent Groups */}
      {Object.entries(groupedAgents).map(([type, typeAgents]) => (
        <div key={type} className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 border-b border-gray-200 pb-2">
            {getGroupTitle(type)}
            <span className="ml-2 text-sm font-normal text-gray-500">
              ({typeAgents.length} agent{typeAgents.length !== 1 ? 's' : ''})
            </span>
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {typeAgents.map((agent) => (
              <AgentCard
                key={agent.id}
                agent={agent}
                onStart={handleStartAgent}
                onStop={handleStopAgent}
                onConfigure={onConfigureAgent}
              />
            ))}
          </div>
        </div>
      ))}

      {/* Quick Actions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-2">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors">
            Start All Idle Agents
          </button>
          <button className="bg-red-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-red-700 transition-colors">
            Stop All Running Agents
          </button>
          <button className="bg-gray-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-700 transition-colors">
            Add New Agent
          </button>
        </div>
      </div>
    </div>
  );
};