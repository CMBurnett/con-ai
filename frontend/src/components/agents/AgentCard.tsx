import React from 'react';
import { Agent } from '@/types/agents';

interface AgentCardProps {
  agent: Agent;
  onStart?: (agentId: string) => void;
  onStop?: (agentId: string) => void;
  onConfigure?: (agentId: string) => void;
}

export const AgentCard: React.FC<AgentCardProps> = ({ 
  agent, 
  onStart, 
  onStop, 
  onConfigure 
}) => {
  const getAgentIcon = (type: string) => {
    switch (type) {
      case 'procore':
        return '<×';
      case 'autodesk':
        return '=Ð';
      case 'primavera':
        return '=Å';
      case 'msproject':
        return '=Ê';
      case 'demo':
        return '>ê';
      default:
        return '>';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'error':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'completed':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPlatformName = (type: string) => {
    switch (type) {
      case 'procore':
        return 'Procore';
      case 'autodesk':
        return 'Autodesk ACC';
      case 'primavera':
        return 'Oracle Primavera P6';
      case 'msproject':
        return 'Microsoft Project';
      case 'demo':
        return 'Demo';
      default:
        return 'Unknown';
    }
  };

  const isRunning = agent.status === 'running';

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="text-2xl">{getAgentIcon(agent.type)}</div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
            <p className="text-sm text-gray-500">{getPlatformName(agent.type)}</p>
          </div>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(agent.status)}`}>
          {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
        </div>
      </div>

      {/* Progress Bar */}
      {isRunning && (
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>Progress</span>
            <span>{agent.progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${agent.progress}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Agent Details */}
      <div className="space-y-2 mb-4">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Agent ID:</span>
          <span className="text-gray-900 font-mono text-xs">{agent.id}</span>
        </div>
        {agent.lastRun && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Last Run:</span>
            <span className="text-gray-900">{new Date(agent.lastRun).toLocaleDateString()}</span>
          </div>
        )}
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Configuration:</span>
          <span className="text-gray-900">{Object.keys(agent.config.settings).length} settings</span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-2">
        {isRunning ? (
          <button
            onClick={() => onStop?.(agent.id)}
            className="flex-1 bg-red-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-red-700 transition-colors"
          >
            Stop Agent
          </button>
        ) : (
          <button
            onClick={() => onStart?.(agent.id)}
            className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            Start Agent
          </button>
        )}
        <button
          onClick={() => onConfigure?.(agent.id)}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors"
        >
          Configure
        </button>
      </div>

      {/* Settings Preview */}
      {agent.config.settings && Object.keys(agent.config.settings).length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Current Settings</h4>
          <div className="space-y-1">
            {Object.entries(agent.config.settings).slice(0, 3).map(([key, value]) => (
              <div key={key} className="flex justify-between text-xs">
                <span className="text-gray-500 truncate">{key}:</span>
                <span className="text-gray-700 truncate ml-2" title={String(value)}>
                  {String(value).length > 20 ? `${String(value).substring(0, 20)}...` : String(value)}
                </span>
              </div>
            ))}
            {Object.keys(agent.config.settings).length > 3 && (
              <div className="text-xs text-gray-400">
                +{Object.keys(agent.config.settings).length - 3} more settings...
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};