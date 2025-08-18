import React, { useState, useEffect } from 'react';
import { useAgentStore } from '@/stores/agentStore';
import { useDataStore } from '@/stores/dataStore';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useUIStore } from '@/stores/uiStore';

// Import new visualization components
import { TemporalKnowledgeGraph } from '@/components/charts/TemporalKnowledgeGraph';
import { PredictiveAnalyticsChart } from '@/components/charts/PredictiveAnalyticsChart';
import { CrossPlatformCorrelationChart } from '@/components/charts/CrossPlatformCorrelationChart';
import { CollaborationInsightsChart } from '@/components/charts/CollaborationInsightsChart';
import { PatternDetectionChart } from '@/components/charts/PatternDetectionChart';
import { ExportDataPanel } from '@/components/charts/ExportDataPanel';

type DashboardView = 'overview' | 'analytics' | 'collaboration' | 'patterns' | 'export';

export const DashboardEnhanced: React.FC = () => {
  const { agents, activeAgents, recentUpdates, setAgents } = useAgentStore();
  const { projects, rfis, budgetItems, lastSync, isLoading } = useDataStore();
  const { isConnected, sendAgentStart, sendAgentStop } = useWebSocket();
  const { addNotification } = useUIStore();
  
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [currentView, setCurrentView] = useState<DashboardView>('overview');
  const [selectedProject, setSelectedProject] = useState<string>('proj-1');

  // Initialize demo agents (same as original)
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

  // Demo data initialization (same as original)
  useEffect(() => {
    const { setProjects, setRFIs, setBudgetItems, updateLastSync } = useDataStore.getState();
    
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

  const navigationItems = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'analytics', label: 'Predictive Analytics', icon: '🔮' },
    { id: 'collaboration', label: 'Collaboration', icon: '🤝' },
    { id: 'patterns', label: 'Pattern Detection', icon: '🔍' },
    { id: 'export', label: 'Data Export', icon: '📤' },
  ];

  const renderOverviewView = () => (
    <div className="space-y-6">
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

      {/* Temporal Knowledge Graph - Full Width */}
      <TemporalKnowledgeGraph className="w-full max-w-full" />

      {/* Cross-Platform Correlation - Full Width */}
      <CrossPlatformCorrelationChart className="w-full max-w-full" correlationType="schedule_budget" />

      {/* Orchestra AI Agents - Full Width Bottom Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Orchestra AI Agents</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">Manage your construction platform agents</p>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {agents.map((agent) => (
              <div key={agent.id} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                <div className="flex items-center space-x-3 mb-3">
                  <div className={`w-3 h-3 rounded-full ${
                    agent.status === 'running' ? 'bg-green-500 animate-pulse' :
                    agent.status === 'error' ? 'bg-red-500' :
                    agent.status === 'completed' ? 'bg-blue-500' :
                    'bg-gray-400'
                  }`}></div>
                  <div className="flex-1">
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white">{agent.name}</h4>
                    <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">{agent.type} Agent</p>
                  </div>
                </div>
                
                {agent.progress > 0 && (
                  <div className="mb-3">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-gray-500 dark:text-gray-400">Progress</span>
                      <span className="text-gray-900 dark:text-white">{agent.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                      <div 
                        className="bg-blue-600 h-1.5 rounded-full transition-all duration-300" 
                        style={{ width: `${agent.progress}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadge(agent.status)}`}>
                    {agent.status}
                  </span>
                  {agent.status === 'running' ? (
                    <button
                      onClick={() => handleStopAgent(agent.id)}
                      className="px-3 py-1 text-xs font-medium text-red-700 bg-red-100 rounded hover:bg-red-200 dark:bg-red-900 dark:text-red-200 dark:hover:bg-red-800 transition-colors"
                    >
                      Stop
                    </button>
                  ) : (
                    <button
                      onClick={() => handleStartAgent(agent.id)}
                      disabled={!isConnected}
                      className="px-3 py-1 text-xs font-medium text-green-700 bg-green-100 rounded hover:bg-green-200 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-green-900 dark:text-green-200 dark:hover:bg-green-800 transition-colors"
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
    </div>
  );

  const renderAnalyticsView = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PredictiveAnalyticsChart 
          projectId={selectedProject}
          predictionType="schedule_drift"
          className="w-full"
        />
        <PredictiveAnalyticsChart 
          projectId={selectedProject}
          predictionType="budget_variance"
          className="w-full"
        />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PredictiveAnalyticsChart 
          projectId={selectedProject}
          predictionType="quality_issues"
          className="w-full"
        />
        <PredictiveAnalyticsChart 
          projectId={selectedProject}
          predictionType="collaboration_effectiveness"
          className="w-full"
        />
      </div>
    </div>
  );

  const renderCollaborationView = () => (
    <div className="space-y-6">
      <CollaborationInsightsChart className="w-full" timeRange="7d" />
      <CrossPlatformCorrelationChart className="w-full" correlationType="collaboration_efficiency" />
    </div>
  );

  const renderPatternsView = () => (
    <div className="space-y-6">
      <PatternDetectionChart className="w-full" timeRange="24h" showAnomalies={true} showPatterns={true} />
    </div>
  );

  const renderExportView = () => (
    <div className="space-y-6">
      <ExportDataPanel className="w-full" />
    </div>
  );

  const renderCurrentView = () => {
    switch (currentView) {
      case 'overview':
        return renderOverviewView();
      case 'analytics':
        return renderAnalyticsView();
      case 'collaboration':
        return renderCollaborationView();
      case 'patterns':
        return renderPatternsView();
      case 'export':
        return renderExportView();
      default:
        return renderOverviewView();
    }
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
            Construction intelligence platform with AI-powered agents and temporal analytics
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            isConnected 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
              : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
          }`}>
            {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
          </div>
          
          {lastSync && (
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Last sync: {lastSync.toLocaleTimeString()}
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex space-x-1 bg-gray-100 dark:bg-gray-800 p-1 rounded-lg">
        {navigationItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setCurrentView(item.id as DashboardView)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
              currentView === item.id
                ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-white/50 dark:hover:bg-gray-700/50'
            }`}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </div>

      {/* Project Selector for Analytics */}
      {currentView === 'analytics' && (
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Select Project:
          </label>
          <select
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value)}
            className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Main Content */}
      {renderCurrentView()}
    </div>
  );
};