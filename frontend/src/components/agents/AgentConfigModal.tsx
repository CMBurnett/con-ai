import React, { useState } from 'react';
import { AgentType } from '@/types/agents';

interface AgentConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  agentType: AgentType;
  agentName: string;
  onSave: (config: AgentConfig) => void;
}

interface AgentConfig {
  agentType: AgentType;
  settings: Record<string, string>;
  enabled: boolean;
}

const defaultConfigs: Record<AgentType, Record<string, string>> = {
  procore: {
    baseUrl: 'https://app.procore.com',
    projectId: '',
    dataTypes: 'projects,rfis,budgets',
  },
  autodesk: {
    baseUrl: 'https://construction.autodesk.com',
    hubId: '',
    projectId: '',
    dataTypes: 'models,issues,drawings',
  },
  primavera: {
    baseUrl: 'https://cloud.primavera.oracle.com',
    projectId: '',
    dataTypes: 'schedules,resources,progress',
  },
  msproject: {
    baseUrl: 'https://project.microsoft.com',
    projectUrl: '',
    dataTypes: 'schedule,tasks,resources,progress',
    extractionFrequency: 'daily',
  },
  email: {
    emailProvider: 'gmail',
    emailAddress: '',
    authType: 'oauth2',
    monitoredFolders: 'INBOX',
    processingInterval: '300',
    dataTypes: 'rfi,schedule,budget,project',
  },
  demo: {
    simulationDuration: '10',
    stepCount: '5',
  },
};

export const AgentConfigModal: React.FC<AgentConfigModalProps> = ({
  isOpen,
  onClose,
  agentType,
  agentName,
  onSave,
}) => {
  const [config, setConfig] = useState<Record<string, string>>(
    defaultConfigs[agentType] || {}
  );
  const [isTestingConnection, setIsTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'success' | 'error'>('idle');

  if (!isOpen) return null;

  const handleSave = () => {
    onSave({
      agentType,
      settings: config,
      enabled: true,
    });
    onClose();
  };

  const handleTestConnection = async () => {
    setIsTestingConnection(true);
    setConnectionStatus('idle');
    
    try {
      // Simulate connection test - in real implementation this would call backend
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      if (agentType === 'msproject' && config.baseUrl === 'https://project.microsoft.com') {
        setConnectionStatus('success');
      } else {
        setConnectionStatus('error');
      }
    } catch {
      setConnectionStatus('error');
    } finally {
      setIsTestingConnection(false);
    }
  };

  interface ConfigField {
    key: string;
    label: string;
    type: string;
    readonly?: boolean;
    placeholder?: string;
    required?: boolean;
    options?: string[];
  }

  const getConfigFields = (): ConfigField[] => {
    switch (agentType) {
      case 'msproject':
        return [
          { key: 'baseUrl', label: 'Microsoft Project URL', type: 'url', readonly: true },
          { key: 'projectUrl', label: 'Specific Project URL (optional)', type: 'url', placeholder: 'https://project.microsoft.com/projects/your-project-id' },
          { key: 'dataTypes', label: 'Data to Extract', type: 'select', options: [
            'schedule,tasks,resources,progress',
            'schedule,tasks',
            'resources,progress',
            'all'
          ]},
          { key: 'extractionFrequency', label: 'Extraction Frequency', type: 'select', options: [
            'daily',
            'weekly',
            'manual'
          ]},
        ];
      case 'procore':
        return [
          { key: 'baseUrl', label: 'Procore Base URL', type: 'url', readonly: true },
          { key: 'projectId', label: 'Project ID', type: 'text', required: true },
          { key: 'dataTypes', label: 'Data Types', type: 'text' },
        ];
      case 'autodesk':
        return [
          { key: 'baseUrl', label: 'Autodesk Construction Cloud URL', type: 'url', readonly: true },
          { key: 'hubId', label: 'Hub ID', type: 'text', required: true },
          { key: 'projectId', label: 'Project ID', type: 'text', required: true },
          { key: 'dataTypes', label: 'Data Types', type: 'text' },
        ];
      case 'primavera':
        return [
          { key: 'baseUrl', label: 'Primavera P6 URL', type: 'url', readonly: true },
          { key: 'projectId', label: 'Project ID', type: 'text', required: true },
          { key: 'dataTypes', label: 'Data Types', type: 'text' },
        ];
      case 'email':
        return [
          { key: 'emailProvider', label: 'Email Provider', type: 'select', options: ['gmail', 'outlook', 'custom'] },
          { key: 'emailAddress', label: 'Email Address', type: 'email', required: true, placeholder: 'your-email@example.com' },
          { key: 'authType', label: 'Authentication Type', type: 'select', options: ['oauth2', 'app_password'] },
          { key: 'monitoredFolders', label: 'Monitored Folders', type: 'text', placeholder: 'INBOX,Construction,Projects' },
          { key: 'processingInterval', label: 'Processing Interval (seconds)', type: 'number', placeholder: '300' },
          { key: 'dataTypes', label: 'Data Types to Extract', type: 'select', options: [
            'rfi,schedule,budget,project',
            'rfi,schedule',
            'budget,project',
            'all'
          ]},
        ];
      case 'demo':
        return [
          { key: 'simulationDuration', label: 'Simulation Duration (seconds)', type: 'number' },
          { key: 'stepCount', label: 'Step Count', type: 'number' },
        ];
      default:
        return [];
    }
  };

  const fields = getConfigFields();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            Configure {agentName}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="space-y-4">
          {agentType === 'msproject' && (
            <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                💡 This agent will use your existing Microsoft 365 browser session. 
                Make sure you're signed in to Project for the Web.
              </p>
            </div>
          )}

          {agentType === 'email' && (
            <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg">
              <p className="text-sm text-green-800 dark:text-green-200">
                📧 This agent monitors your email for construction-related communications.
                OAuth2 authentication is recommended for security. All data stays local.
              </p>
            </div>
          )}

          {fields.map((field) => (
            <div key={field.key}>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {field.label}
                {field.required && <span className="text-red-500"> *</span>}
              </label>
              
              {field.type === 'select' ? (
                <select
                  value={config[field.key] || ''}
                  onChange={(e) => setConfig({ ...config, [field.key]: e.target.value })}
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  {field.options?.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  type={field.type}
                  value={config[field.key] || ''}
                  onChange={(e) => setConfig({ ...config, [field.key]: e.target.value })}
                  placeholder={field.placeholder}
                  readOnly={field.readonly}
                  className={`block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                    field.readonly ? 'bg-gray-100 dark:bg-gray-600' : ''
                  }`}
                />
              )}
            </div>
          ))}

          {/* Connection Test */}
          <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
            <button
              onClick={handleTestConnection}
              disabled={isTestingConnection}
              className="w-full px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 border border-blue-600 rounded-lg hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed dark:text-blue-400 dark:border-blue-400 dark:hover:bg-blue-900/20"
            >
              {isTestingConnection ? 'Testing Connection...' : 'Test Connection'}
            </button>
            
            {connectionStatus === 'success' && (
              <div className="mt-2 p-2 bg-green-50 text-green-800 text-sm rounded dark:bg-green-900/20 dark:text-green-200">
                ✅ Connection successful!
              </div>
            )}
            
            {connectionStatus === 'error' && (
              <div className="mt-2 p-2 bg-red-50 text-red-800 text-sm rounded dark:bg-red-900/20 dark:text-red-200">
                ❌ Connection failed. Please check your settings and ensure you're signed in.
              </div>
            )}
          </div>
        </div>

        <div className="flex space-x-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
          >
            Save Configuration
          </button>
        </div>
      </div>
    </div>
  );
};