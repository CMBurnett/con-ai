import React from 'react';
import { useAgentStore } from '@/stores/agentStore';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useUIStore } from '@/stores/uiStore';

export const Agents: React.FC = () => {
  const { agents, activeAgents } = useAgentStore();
  const { isConnected, sendAgentStart, sendAgentStop } = useWebSocket();
  const { addNotification } = useUIStore();

  const handleStartAgent = async (agentId: string) => {
    const agent = agents.find(a => a.id === agentId);
    if (!agent) return;

    try {
      sendAgentStart(agentId, agent.type, 'extract_project_data', {
        projectId: 'demo-project',
        extractionType: 'full_sync',
      });
      
      addNotification({
        type: 'info',
        title: 'Agent Started',
        message: `${agent.name} is now running`,
        duration: 3000,
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Start Failed',
        message: `Failed to start ${agent.name}`,
        duration: 5000,
      });
    }
  };

  const handleStopAgent = async (agentId: string) => {
    const agent = agents.find(a => a.id === agentId);
    if (!agent) return;

    try {
      sendAgentStop(agentId);
      
      addNotification({
        type: 'info',
        title: 'Agent Stopped',
        message: `${agent.name} has been stopped`,
        duration: 3000,
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Stop Failed',
        message: `Failed to stop ${agent.name}`,
        duration: 5000,
      });
    }
  };

  const getStatusBadge = (status: string) => {
    const colors = {
      idle: 'bg-gray-100 text-gray-800',
      running: 'bg-green-100 text-green-800',
      completed: 'bg-blue-100 text-blue-800',
      error: 'bg-red-100 text-red-800',
    };
    return colors[status as keyof typeof colors] || colors.idle;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Agent Management
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Configure and monitor your construction platform agents
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            isConnected 
              ? 'bg-green-100 text-green-800' 
              : 'bg-red-100 text-red-800'
          }`}>
            {activeAgents.length} active agents
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {agents.map((agent) => (
          <div key={agent.id} className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    agent.status === 'running' ? 'bg-green-500 animate-pulse' :
                    agent.status === 'error' ? 'bg-red-500' :
                    agent.status === 'completed' ? 'bg-blue-500' :
                    'bg-gray-400'
                  }`}></div>
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">{agent.name}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 capitalize">{agent.type} Agent</p>
                  </div>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadge(agent.status)}`}>
                  {agent.status}
                </span>
              </div>

              {agent.progress > 0 && (
                <div className="mb-4">
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-gray-500 dark:text-gray-400">Progress</span>
                    <span className="text-gray-900 dark:text-white">{agent.progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                      style={{ width: `${agent.progress}%` }}
                    ></div>
                  </div>
                </div>
              )}

              <div className="space-y-3">
                <div className="text-sm">
                  <span className="font-medium text-gray-700 dark:text-gray-300">Configuration:</span>
                  <div className="mt-1 text-gray-600 dark:text-gray-400">
                    {Object.entries(agent.config.settings || {}).length > 0 ? (
                      <ul className="list-disc list-inside space-y-1">
                        {Object.entries(agent.config.settings).slice(0, 3).map(([key, value]) => (
                          <li key={key} className="truncate">
                            <span className="font-mono text-xs">{key}:</span> {String(value)}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <span className="italic">Default configuration</span>
                    )}
                  </div>
                </div>

                {agent.lastRun && (
                  <div className="text-sm">
                    <span className="font-medium text-gray-700 dark:text-gray-300">Last Run:</span>
                    <span className="ml-2 text-gray-600 dark:text-gray-400">
                      {agent.lastRun.toLocaleString()}
                    </span>
                  </div>
                )}
              </div>

              <div className="mt-6 flex space-x-3">
                {agent.status === 'running' ? (
                  <button
                    onClick={() => handleStopAgent(agent.id)}
                    className="flex-1 px-4 py-2 text-sm font-medium text-red-700 bg-red-100 rounded-lg hover:bg-red-200 dark:bg-red-900 dark:text-red-200 dark:hover:bg-red-800"
                  >
                    Stop Agent
                  </button>
                ) : (
                  <button
                    onClick={() => handleStartAgent(agent.id)}
                    disabled={!isConnected}
                    className="flex-1 px-4 py-2 text-sm font-medium text-green-700 bg-green-100 rounded-lg hover:bg-green-200 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-green-900 dark:text-green-200 dark:hover:bg-green-800"
                  >
                    Start Agent
                  </button>
                )}
                <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600">
                  Configure
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {agents.length === 0 && (
        <div className="text-center py-12">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No agents configured</h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Get started by adding your first construction platform agent.</p>
          <div className="mt-6">
            <button className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
              Add Agent
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
