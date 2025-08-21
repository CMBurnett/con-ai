import React from 'react';

interface DataSourceIndicatorProps {
  dataSource: {
    store?: string;
    api?: string;
    file?: string;
  };
}

export const DataSourceIndicator: React.FC<DataSourceIndicatorProps> = ({ dataSource }) => {
  const getSourceIcon = () => {
    if (dataSource.store) return '🗃️';
    if (dataSource.api) return '🌐';
    return '📁';
  };

  const getSourceType = () => {
    if (dataSource.store) return 'Store';
    if (dataSource.api) return 'API';
    return 'File';
  };

  const getSourcePath = () => {
    if (dataSource.store) return dataSource.store;
    if (dataSource.api) return dataSource.api;
    return dataSource.file || 'Unknown';
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  return (
    <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <span className="text-lg">{getSourceIcon()}</span>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Data Source:
            </span>
            <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded-full">
              {getSourceType()}
            </span>
          </div>
        </div>
        
        <button
          onClick={() => copyToClipboard(dataSource.file || getSourcePath())}
          className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 flex items-center space-x-1"
          title="Copy file path to clipboard"
        >
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <span>Copy</span>
        </button>
      </div>
      
      <div className="mt-2 space-y-1">
        {dataSource.store && (
          <div className="text-xs text-gray-600 dark:text-gray-400">
            <span className="font-medium">Store Path:</span> {dataSource.store}
          </div>
        )}
        
        {dataSource.api && (
          <div className="text-xs text-gray-600 dark:text-gray-400">
            <span className="font-medium">API Endpoint:</span> {dataSource.api}
          </div>
        )}
        
        {dataSource.file && (
          <div className="text-xs text-gray-600 dark:text-gray-400">
            <span className="font-medium">File Location:</span> 
            <code className="ml-1 px-1 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-xs font-mono">
              {dataSource.file}
            </code>
          </div>
        )}
      </div>
      
      <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          💡 This shows where the data is stored and managed in the application codebase
        </p>
      </div>
    </div>
  );
};