import React, { useState, useEffect } from 'react';
import { useAgentStore } from '@/stores/agentStore';
import { useDataStore } from '@/stores/dataStore';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useUIStore } from '@/stores/uiStore';

export const Dashboard: React.FC = () => {
  const { agents, activeAgents, recentUpdates, setAgents } = useAgentStore();
  const { projects, rfis, budgetItems, lastSync, isLoading } = useDataStore();
  const { isConnected, sendAgentStart, sendAgentStop } = useWebSocket();
  const { addNotification } = useUIStore();
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  // Initialize demo agents
  useEffect(() => {
    const demoAgents = [
      {
        id: 'procore-agent-1',
        name: 'Procore Data Extractor',
        type: 'procore' as const,
        status: 'idle' as const,
        progress: 0,
        config: {
          id: 'procore-agent-1',
          agentType: 'procore',
          settings: {
            baseUrl: 'https://app.procore.com',
            projectId: 'demo-project',
          },
        },
      },
      {
        id: 'autodesk-agent-1',
        name: 'Autodesk ACC Sync',
        type: 'autodesk' as const,
        status: 'idle' as const,
        progress: 0,
        config: {
          id: 'autodesk-agent-1',
          agentType: 'autodesk',
          settings: {
            hubId: 'demo-hub',
            projectId: 'demo-project',
          },
        },
      },
      {
        id: 'primavera-agent-1',
        name: 'Oracle Primavera P6',
        type: 'primavera' as const,
        status: 'idle' as const,
        progress: 0,
        config: {
          id: 'primavera-agent-1',
          agentType: 'primavera',
          settings: {
            baseUrl: 'https://cloud.primavera.oracle.com',
            projectId: 'demo-project',
          },
        },
      },
      {
        id: 'msproject-agent-1',
        name: 'Microsoft Project Scheduler',
        type: 'msproject' as const,
        status: 'idle' as const,
        progress: 0,
        config: {
          id: 'msproject-agent-1',
          agentType: 'msproject',
          settings: {
            baseUrl: 'https://project.microsoft.com',
            projectId: 'demo-project',
          },
        },
      },
      {
        id: 'demo-agent-1',
        name: 'Demo Testing Agent',
        type: 'demo' as const,
        status: 'idle' as const,
        progress: 0,
        config: {
          id: 'demo-agent-1',
          agentType: 'demo',
          settings: {
            simulationDuration: 10,
            stepCount: 5,
          },
        },
      },
    ];
    
    setAgents(demoAgents);
  }, [setAgents]);

  // Demo data for visualization
  useEffect(() => {
    const { setProjects, setRFIs, setBudgetItems, updateLastSync } = useDataStore.getState();
    
    // Set demo data
    setProjects([
      {
        id: 'proj-1',
        name: 'Downtown Office Complex',
        status: 'active',
        progress: 65,
        budget: 2500000,
        startDate: new Date('2024-01-15'),
        endDate: new Date('2025-03-30'),
        manager: 'John Smith',
      },
      {
        id: 'proj-2', 
        name: 'Residential Tower A',
        status: 'planning',
        progress: 15,
        budget: 4200000,
        startDate: new Date('2024-06-01'),
        endDate: new Date('2026-08-15'),
        manager: 'Sarah Johnson',
      },
    ]);

    setRFIs([
      {
        id: 'rfi-1',
        title: 'HVAC System Specifications',
        description: 'Need clarification on HVAC requirements for floors 5-8',
        status: 'open',
        priority: 'high',
        submittedBy: 'Mike Wilson',
        submittedDate: new Date('2025-08-15'),
        projectId: 'proj-1',
      },
      {
        id: 'rfi-2',
        title: 'Foundation Depth Requirements',
        description: 'Soil report indicates need for deeper foundation',
        status: 'pending',
        priority: 'critical',
        submittedBy: 'Lisa Chen',
        submittedDate: new Date('2025-08-14'),
        projectId: 'proj-2',
      },
    ]);

    setBudgetItems([
      {
        id: 'budget-1',
        category: 'Labor',
        budgetedAmount: 800000,
        actualAmount: 750000,
        projectId: 'proj-1',
      },
      {
        id: 'budget-2',
        category: 'Materials',
        budgetedAmount: 1200000,
        actualAmount: 1350000,
        projectId: 'proj-1',
      },
    ]);

    updateLastSync();
  }, []);

  const handleStartAgent = async (agentId: string) => {
    const agent = agents.find(a => a.id === agentId);
    if (!agent) return;

    setSelectedAgent(agentId);
    
    try {
      // Send command to Orchestra backend
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
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Orchestra Dashboard
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Construction intelligence platform with AI-powered agents
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            isConnected 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
              : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
          }`}>
            {isConnected ? ' Connected' : ' Disconnected'}
          </div>
          
          {lastSync && (
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Last sync: {lastSync.toLocaleTimeString()}
            </div>
          )}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Projects</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{projects.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Agents</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{activeAgents.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
              <svg className="w-6 h-6 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Open RFIs</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{rfis.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Budget</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                ${(projects.reduce((sum, p) => sum + p.budget, 0) / 1000000).toFixed(1)}M
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Agent Management */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Agents List */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">AI Agents</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">Manage your construction platform agents</p>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {agents.map((agent) => (
                <div key={agent.id} className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${
                        agent.status === 'running' ? 'bg-green-500 animate-pulse' :
                        agent.status === 'error' ? 'bg-red-500' :
                        agent.status === 'completed' ? 'bg-blue-500' :
                        'bg-gray-400'
                      }`}></div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 dark:text-white">{agent.name}</h4>
                        <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">{agent.type} Agent</p>
                      </div>
                    </div>
                    {agent.progress > 0 && (
                      <div className="mt-2">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-gray-500 dark:text-gray-400">Progress</span>
                          <span className="text-gray-900 dark:text-white">{agent.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 mt-1">
                          <div 
                            className="bg-blue-600 h-1.5 rounded-full transition-all duration-300" 
                            style={{ width: `${agent.progress}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadge(agent.status)}`}>
                      {agent.status}
                    </span>
                    {agent.status === 'running' ? (
                      <button
                        onClick={() => handleStopAgent(agent.id)}
                        className="px-3 py-1 text-xs font-medium text-red-700 bg-red-100 rounded hover:bg-red-200 dark:bg-red-900 dark:text-red-200 dark:hover:bg-red-800"
                      >
                        Stop
                      </button>
                    ) : (
                      <button
                        onClick={() => handleStartAgent(agent.id)}
                        disabled={!isConnected}
                        className="px-3 py-1 text-xs font-medium text-green-700 bg-green-100 rounded hover:bg-green-200 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-green-900 dark:text-green-200 dark:hover:bg-green-800"
                      >
                        Start
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Recent Activity</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">Latest agent updates and system events</p>
          </div>
          <div className="p-6">
            <div className="space-y-4 max-h-80 overflow-y-auto">
              {recentUpdates.length > 0 ? (
                recentUpdates.slice(-10).reverse().map((update, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className={`w-2 h-2 mt-2 rounded-full flex-shrink-0 ${
                      update.status === 'running' ? 'bg-green-500' :
                      update.status === 'error' ? 'bg-red-500' :
                      update.status === 'completed' ? 'bg-blue-500' :
                      'bg-gray-400'
                    }`}></div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-900 dark:text-white">
                        <span className="font-medium">{update.agentId}</span>
                        {update.message && <span className="ml-2">{update.message}</span>}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {update.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <svg className="mx-auto h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">No recent activity</p>
                  <p className="text-xs text-gray-400 dark:text-gray-500">Start an agent to see updates here</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Projects Overview */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Projects Overview</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">Current construction projects and their status</p>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {projects.map((project) => (
              <div key={project.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">{project.name}</h4>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    project.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                    project.status === 'planning' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                    'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                  }`}>
                    {project.status}
                  </span>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-500 dark:text-gray-400">Progress</span>
                    <span className="text-gray-900 dark:text-white">{project.progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                      style={{ width: `${project.progress}%` }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                    <span>Budget: ${(project.budget / 1000000).toFixed(1)}M</span>
                    <span>Manager: {project.manager}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
