import React, { useState } from 'react';
import { useAgentStore } from '@/stores/agentStore';
import { useDataStore } from '@/stores/dataStore';
import { DataTable } from '@/components/data/DataTable';
import { SearchInterface } from '@/components/data/SearchInterface';
import { DataSourceIndicator } from '@/components/data/DataSourceIndicator';

type DataTableType = 'projects' | 'rfis' | 'budgetItems' | 'agents' | 'agentUpdates' | 'temporalData' | 'predictions' | 'patterns';

interface DataTableConfig {
  id: DataTableType;
  label: string;
  description: string;
  icon: string;
  dataSource: {
    store?: string;
    api?: string;
    file?: string;
  };
}

const dataTableConfigs: DataTableConfig[] = [
  {
    id: 'projects',
    label: 'Projects',
    description: 'Construction project data and status information',
    icon: '🏗️',
    dataSource: {
      store: 'dataStore.ts → projects',
      file: 'frontend/src/stores/dataStore.ts',
    },
  },
  {
    id: 'rfis',
    label: 'RFIs',
    description: 'Request for Information documents and responses',
    icon: '❓',
    dataSource: {
      store: 'dataStore.ts → rfis',
      file: 'frontend/src/stores/dataStore.ts',
    },
  },
  {
    id: 'budgetItems',
    label: 'Budget Items',
    description: 'Project budget categories and financial tracking',
    icon: '💰',
    dataSource: {
      store: 'dataStore.ts → budgetItems',
      file: 'frontend/src/stores/dataStore.ts',
    },
  },
  {
    id: 'agents',
    label: 'AI Agents',
    description: 'Agent configurations and operational settings',
    icon: '🤖',
    dataSource: {
      store: 'agentStore.ts → agents',
      file: 'frontend/src/stores/agentStore.ts',
    },
  },
  {
    id: 'agentUpdates',
    label: 'Agent Updates',
    description: 'Real-time agent status updates and activity logs',
    icon: '📊',
    dataSource: {
      store: 'agentStore.ts → recentUpdates',
      file: 'frontend/src/stores/agentStore.ts',
    },
  },
  {
    id: 'temporalData',
    label: 'Temporal Data',
    description: 'Orchestra knowledge graph nodes and relationships',
    icon: '⏱️',
    dataSource: {
      api: '/api/orchestra/knowledge-graph/stats',
      file: 'backend/api/orchestra.py',
    },
  },
  {
    id: 'predictions',
    label: 'Predictions',
    description: 'AI-generated project outcome predictions',
    icon: '🔮',
    dataSource: {
      api: '/api/orchestra/predictions',
      file: 'backend/api/orchestra.py',
    },
  },
  {
    id: 'patterns',
    label: 'Detected Patterns',
    description: 'Pattern detection and anomaly analysis results',
    icon: '🔍',
    dataSource: {
      api: '/api/orchestra/patterns/detect',
      file: 'backend/api/orchestra.py',
    },
  },
];

export const DataTablesView: React.FC = () => {
  const [activeTable, setActiveTable] = useState<DataTableType>('projects');
  const [globalSearchQuery, setGlobalSearchQuery] = useState('');
  
  const { projects, rfis, budgetItems } = useDataStore();
  const { agents, recentUpdates } = useAgentStore();

  const getTableData = (tableType: DataTableType) => {
    switch (tableType) {
      case 'projects':
        return projects;
      case 'rfis':
        return rfis;
      case 'budgetItems':
        return budgetItems;
      case 'agents':
        return agents;
      case 'agentUpdates':
        return recentUpdates;
      case 'temporalData':
      case 'predictions':
      case 'patterns':
        // These will be loaded from Orchestra APIs
        return [];
      default:
        return [];
    }
  };

  const getTableColumns = (tableType: DataTableType) => {
    switch (tableType) {
      case 'projects':
        return [
          { key: 'id', label: 'Project ID', sortable: true },
          { key: 'name', label: 'Name', sortable: true },
          { key: 'status', label: 'Status', sortable: true },
          { key: 'progress', label: 'Progress', sortable: true, format: (value: number) => `${value}%` },
          { key: 'budget', label: 'Budget', sortable: true, format: (value: number) => `$${(value / 1000000).toFixed(1)}M` },
          { key: 'manager', label: 'Manager', sortable: true },
          { key: 'startDate', label: 'Start Date', sortable: true, format: (value: Date) => value.toLocaleDateString() },
          { key: 'endDate', label: 'End Date', sortable: true, format: (value: Date) => value.toLocaleDateString() },
        ];
      case 'rfis':
        return [
          { key: 'id', label: 'RFI ID', sortable: true },
          { key: 'title', label: 'Title', sortable: true },
          { key: 'status', label: 'Status', sortable: true },
          { key: 'priority', label: 'Priority', sortable: true },
          { key: 'submittedBy', label: 'Submitted By', sortable: true },
          { key: 'projectId', label: 'Project ID', sortable: true },
          { key: 'submittedDate', label: 'Submitted Date', sortable: true, format: (value: Date) => value.toLocaleDateString() },
        ];
      case 'budgetItems':
        return [
          { key: 'id', label: 'Budget ID', sortable: true },
          { key: 'category', label: 'Category', sortable: true },
          { key: 'budgetedAmount', label: 'Budgeted', sortable: true, format: (value: number) => `$${value.toLocaleString()}` },
          { key: 'actualAmount', label: 'Actual', sortable: true, format: (value: number) => `$${value.toLocaleString()}` },
          { key: 'projectId', label: 'Project ID', sortable: true },
          { key: 'variance', label: 'Variance', sortable: false, format: (_value: number, row: any) => {
            const variance = row.actualAmount - row.budgetedAmount;
            const color = variance > 0 ? 'text-red-600' : variance < 0 ? 'text-green-600' : 'text-gray-600';
            return <span className={color}>${variance.toLocaleString()}</span>;
          }},
        ];
      case 'agents':
        return [
          { key: 'id', label: 'Agent ID', sortable: true },
          { key: 'name', label: 'Name', sortable: true },
          { key: 'type', label: 'Type', sortable: true },
          { key: 'status', label: 'Status', sortable: true },
          { key: 'progress', label: 'Progress', sortable: true, format: (value: number) => `${value}%` },
          { key: 'lastRun', label: 'Last Run', sortable: true, format: (value: Date) => value ? value.toLocaleString() : 'Never' },
        ];
      case 'agentUpdates':
        return [
          { key: 'agentId', label: 'Agent ID', sortable: true },
          { key: 'status', label: 'Status', sortable: true },
          { key: 'message', label: 'Message', sortable: false },
          { key: 'timestamp', label: 'Timestamp', sortable: true, format: (value: Date) => value.toLocaleString() },
        ];
      default:
        return [];
    }
  };

  const activeConfig = dataTableConfigs.find(config => config.id === activeTable)!;
  const tableData = getTableData(activeTable);
  const tableColumns = getTableColumns(activeTable);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Data Tables
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Browse and analyze all construction data used in the Con-AI application
          </p>
        </div>
      </div>

      {/* Global Search */}
      <SearchInterface
        searchQuery={globalSearchQuery}
        onSearchChange={setGlobalSearchQuery}
        placeholder="Search across all data tables..."
      />

      {/* Data Table Navigation */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="-mb-px flex space-x-8 overflow-x-auto px-6" aria-label="Tabs">
            {dataTableConfigs.map((config) => (
              <button
                key={config.id}
                onClick={() => setActiveTable(config.id)}
                className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTable === config.id
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                <span className="text-lg">{config.icon}</span>
                <span>{config.label}</span>
                <span className="ml-2 bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400 py-0.5 px-2 rounded-full text-xs">
                  {getTableData(config.id).length}
                </span>
              </button>
            ))}
          </nav>
        </div>

        {/* Active Table Content */}
        <div className="p-6">
          {/* Table Header with Data Source Info */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{activeConfig.icon}</span>
                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                    {activeConfig.label}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {activeConfig.description}
                  </p>
                </div>
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {tableData.length} records
              </div>
            </div>
            
            {/* Data Source Indicator */}
            <DataSourceIndicator dataSource={activeConfig.dataSource} />
          </div>

          {/* Data Table */}
          <DataTable
            data={tableData as any[]}
            columns={tableColumns}
            searchQuery={globalSearchQuery}
            emptyMessage={`No ${activeConfig.label.toLowerCase()} data available`}
            onExport={(data) => {
              console.log(`Exporting ${activeConfig.label} data:`, data);
            }}
          />
        </div>
      </div>
    </div>
  );
};