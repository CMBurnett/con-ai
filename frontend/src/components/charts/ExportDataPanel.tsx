import React, { useState } from 'react';
import { useDataStore } from '@/stores/dataStore';
import { useAgentStore } from '@/stores/agentStore';

interface ExportConfig {
  dataTypes: string[];
  formats: string[];
  dateRange: {
    start: Date;
    end: Date;
  };
  includeMetadata: boolean;
  includeAnalytics: boolean;
  includePredictions: boolean;
  customFilters: Record<string, any>;
}

interface ExportDataPanelProps {
  className?: string;
  onExportComplete?: (exportedData: any) => void;
}

export const ExportDataPanel: React.FC<ExportDataPanelProps> = ({
  className = '',
  onExportComplete,
}) => {
  const { projects, rfis, budgetItems } = useDataStore();
  const { agents, recentUpdates } = useAgentStore();
  
  const [exportConfig, setExportConfig] = useState<ExportConfig>({
    dataTypes: ['projects'],
    formats: ['json'],
    dateRange: {
      start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
      end: new Date(),
    },
    includeMetadata: true,
    includeAnalytics: false,
    includePredictions: false,
    customFilters: {},
  });
  
  const [isExporting, setIsExporting] = useState(false);
  const [exportHistory, setExportHistory] = useState<any[]>([]);
  const [previewData, setPreviewData] = useState<any>(null);

  const dataTypeOptions = [
    { id: 'projects', label: 'Projects', count: projects.length, icon: '🏗️' },
    { id: 'rfis', label: 'RFIs', count: rfis.length, icon: '❓' },
    { id: 'budgetItems', label: 'Budget Items', count: budgetItems.length, icon: '💰' },
    { id: 'agents', label: 'Agent Data', count: agents.length, icon: '🤖' },
    { id: 'agentUpdates', label: 'Agent Updates', count: recentUpdates.length, icon: '📊' },
    { id: 'temporalAnalytics', label: 'Temporal Analytics', count: 0, icon: '⏱️' },
    { id: 'collaborationInsights', label: 'Collaboration Insights', count: 0, icon: '🤝' },
    { id: 'patterns', label: 'Detected Patterns', count: 0, icon: '🔍' },
    { id: 'predictions', label: 'Predictive Analytics', count: 0, icon: '🔮' },
  ];

  const formatOptions = [
    { id: 'json', label: 'JSON', icon: '📄', description: 'JavaScript Object Notation' },
    { id: 'csv', label: 'CSV', icon: '📊', description: 'Comma Separated Values' },
    { id: 'excel', label: 'Excel', icon: '📗', description: 'Microsoft Excel format' },
    { id: 'pdf', label: 'PDF', icon: '📕', description: 'Portable Document Format' },
    { id: 'xml', label: 'XML', icon: '📰', description: 'Extensible Markup Language' },
  ];

  const handleDataTypeChange = (dataType: string, checked: boolean) => {
    setExportConfig(prev => ({
      ...prev,
      dataTypes: checked
        ? [...prev.dataTypes, dataType]
        : prev.dataTypes.filter(dt => dt !== dataType),
    }));
  };

  const handleFormatChange = (format: string, checked: boolean) => {
    setExportConfig(prev => ({
      ...prev,
      formats: checked
        ? [...prev.formats, format]
        : prev.formats.filter(f => f !== format),
    }));
  };

  const generatePreview = () => {
    const sampleData = buildExportData(true); // Generate sample with limited data
    setPreviewData(sampleData);
  };

  const buildExportData = (isPreview = false) => {
    const exportData: any = {
      metadata: {
        exportedAt: new Date().toISOString(),
        orchestraVersion: '1.0.0',
        dataTypes: exportConfig.dataTypes,
        dateRange: exportConfig.dateRange,
        totalRecords: 0,
      },
      data: {},
    };

    if (exportConfig.includeMetadata) {
      exportData.metadata.systemInfo = {
        platform: 'Orchestra Construction Intelligence',
        generatedBy: 'AI Agent System',
        temporalIntelligence: true,
      };
    }

    // Build data based on selected types
    if (exportConfig.dataTypes.includes('projects')) {
      const projectData = isPreview ? projects.slice(0, 2) : projects;
      exportData.data.projects = projectData.map(project => ({
        ...project,
        startDate: project.startDate.toISOString(),
        endDate: project.endDate.toISOString(),
        exportedFields: ['id', 'name', 'status', 'budget', 'progress', 'manager'],
      }));
      exportData.metadata.totalRecords += projectData.length;
    }

    if (exportConfig.dataTypes.includes('rfis')) {
      const rfiData = isPreview ? rfis.slice(0, 3) : rfis;
      exportData.data.rfis = rfiData.map(rfi => ({
        ...rfi,
        submittedDate: rfi.submittedDate.toISOString(),
        dueDate: rfi.dueDate?.toISOString(),
      }));
      exportData.metadata.totalRecords += rfiData.length;
    }

    if (exportConfig.dataTypes.includes('budgetItems')) {
      const budgetData = isPreview ? budgetItems.slice(0, 2) : budgetItems;
      exportData.data.budgetItems = budgetData.map(item => ({
        ...item,
        variance: item.actualAmount - item.budgetedAmount,
        variancePercentage: ((item.actualAmount - item.budgetedAmount) / item.budgetedAmount) * 100,
      }));
      exportData.metadata.totalRecords += budgetData.length;
    }

    if (exportConfig.dataTypes.includes('agents')) {
      const agentData = isPreview ? agents.slice(0, 2) : agents;
      exportData.data.agents = agentData.map(agent => ({
        id: agent.id,
        name: agent.name,
        type: agent.type,
        status: agent.status,
        progress: agent.progress,
        lastRun: agent.lastRun?.toISOString(),
        configuration: agent.config,
      }));
      exportData.metadata.totalRecords += agentData.length;
    }

    if (exportConfig.dataTypes.includes('agentUpdates')) {
      const updateData = isPreview ? recentUpdates.slice(0, 5) : recentUpdates;
      exportData.data.agentUpdates = updateData.map(update => ({
        ...update,
        timestamp: update.timestamp.toISOString(),
      }));
      exportData.metadata.totalRecords += updateData.length;
    }

    // Add Orchestra-specific temporal analytics if requested
    if (exportConfig.dataTypes.includes('temporalAnalytics') && exportConfig.includeAnalytics) {
      exportData.data.temporalAnalytics = {
        knowledgeGraphStats: {
          totalNodes: 156,
          totalEdges: 289,
          nodeTypes: {
            agents: 5,
            projects: 3,
            platforms: 3,
            tasks: 145,
          },
          lastUpdated: new Date().toISOString(),
        },
        consolidationCycles: [
          {
            cycleDate: new Date().toISOString(),
            patternsDetected: 4,
            dataQualityScore: 0.92,
            processingTime: 5.2,
          },
        ],
      };
    }

    // Add collaboration insights
    if (exportConfig.dataTypes.includes('collaborationInsights') && exportConfig.includeAnalytics) {
      exportData.data.collaborationInsights = {
        overallEffectiveness: 84.5,
        agentCollaborations: [
          {
            agentPair: ['procore-agent-1', 'autodesk-agent-1'],
            collaborationCount: 45,
            effectivenessScore: 92,
          },
          {
            agentPair: ['primavera-agent-1', 'procore-agent-1'],
            collaborationCount: 32,
            effectivenessScore: 88,
          },
        ],
        peakCollaborationHours: [9, 13, 17],
        crossPlatformSyncRate: 96.8,
      };
    }

    // Add detected patterns
    if (exportConfig.dataTypes.includes('patterns')) {
      exportData.data.patterns = [
        {
          id: 'pattern-temporal-1',
          type: 'temporal_peak',
          name: 'Peak activity at hour 14',
          confidence: 0.89,
          detectedAt: new Date().toISOString(),
          affectedEntities: ['procore-agent-1', 'autodesk-agent-1'],
        },
        {
          id: 'pattern-collab-1',
          type: 'collaboration_burst',
          name: 'Increased collaboration on Tuesdays',
          confidence: 0.76,
          detectedAt: new Date().toISOString(),
          affectedEntities: ['primavera-agent-1', 'procore-agent-1'],
        },
      ];
    }

    // Add predictions if requested
    if (exportConfig.dataTypes.includes('predictions') && exportConfig.includePredictions) {
      exportData.data.predictions = {
        projectOutcomes: [
          {
            projectId: 'proj-1',
            scheduleDrift: {
              predictedDays: 5.2,
              confidence: 0.85,
              riskLevel: 'medium',
            },
            budgetVariance: {
              predictedPercent: 8.5,
              confidence: 0.78,
              riskLevel: 'medium',
            },
          },
        ],
        systemPredictions: {
          nextMaintenanceWindow: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
          expectedLoadIncrease: 12.5,
          resourceOptimizationOpportunities: 3,
        },
      };
    }

    return exportData;
  };

  const performExport = async () => {
    setIsExporting(true);
    
    try {
      const exportData = buildExportData();
      
      // Simulate API call to Orchestra backend for additional data
      try {
        const response = await fetch('/api/orchestra/export', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            dataTypes: exportConfig.dataTypes,
            dateRange: exportConfig.dateRange,
            includeAnalytics: exportConfig.includeAnalytics,
            includePredictions: exportConfig.includePredictions,
          }),
        });
        
        if (response.ok) {
          const orchestraData = await response.json();
          exportData.data.orchestraSpecific = orchestraData;
        }
      } catch (error) {
        console.log('Orchestra backend not available, using local data only');
      }

      // Process exports for each format
      for (const format of exportConfig.formats) {
        await exportInFormat(exportData, format);
      }

      // Add to export history
      const exportRecord = {
        id: Date.now().toString(),
        timestamp: new Date(),
        dataTypes: exportConfig.dataTypes,
        formats: exportConfig.formats,
        recordCount: exportData.metadata.totalRecords,
        fileSize: JSON.stringify(exportData).length,
      };
      
      setExportHistory(prev => [exportRecord, ...prev.slice(0, 9)]);
      
      if (onExportComplete) {
        onExportComplete(exportData);
      }

    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const exportInFormat = async (data: any, format: string) => {
    const filename = `orchestra-export-${Date.now()}`;
    
    switch (format) {
      case 'json':
        downloadFile(JSON.stringify(data, null, 2), `${filename}.json`, 'application/json');
        break;
      case 'csv':
        const csvData = convertToCSV(data);
        downloadFile(csvData, `${filename}.csv`, 'text/csv');
        break;
      case 'excel':
        // Would use a library like xlsx in real implementation
        const excelData = JSON.stringify(data, null, 2);
        downloadFile(excelData, `${filename}.xlsx`, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
        break;
      case 'pdf':
        // Would use a library like jsPDF in real implementation
        const pdfData = formatForPDF(data);
        downloadFile(pdfData, `${filename}.pdf`, 'application/pdf');
        break;
      case 'xml':
        const xmlData = convertToXML(data);
        downloadFile(xmlData, `${filename}.xml`, 'application/xml');
        break;
    }
  };

  const convertToCSV = (data: any) => {
    let csv = '';
    
    // Convert each data type to CSV format
    for (const [dataType, items] of Object.entries(data.data)) {
      if (Array.isArray(items) && items.length > 0) {
        csv += `\n# ${dataType.toUpperCase()}\n`;
        const headers = Object.keys(items[0]);
        csv += headers.join(',') + '\n';
        
        items.forEach((item: any) => {
          const values = headers.map(header => {
            const value = item[header];
            return typeof value === 'string' ? `"${value.replace(/"/g, '""')}"` : value;
          });
          csv += values.join(',') + '\n';
        });
      }
    }
    
    return csv;
  };

  const convertToXML = (data: any) => {
    let xml = '<?xml version="1.0" encoding="UTF-8"?>\n<orchestraExport>\n';
    xml += `  <metadata>\n`;
    xml += `    <exportedAt>${data.metadata.exportedAt}</exportedAt>\n`;
    xml += `    <totalRecords>${data.metadata.totalRecords}</totalRecords>\n`;
    xml += `  </metadata>\n`;
    xml += `  <data>\n`;
    
    for (const [dataType, items] of Object.entries(data.data)) {
      xml += `    <${dataType}>\n`;
      if (Array.isArray(items)) {
        items.forEach((item: any) => {
          xml += `      <item>\n`;
          for (const [key, value] of Object.entries(item)) {
            xml += `        <${key}>${value}</${key}>\n`;
          }
          xml += `      </item>\n`;
        });
      }
      xml += `    </${dataType}>\n`;
    }
    
    xml += `  </data>\n</orchestraExport>`;
    return xml;
  };

  const formatForPDF = (data: any) => {
    // This would create actual PDF content with jsPDF or similar
    return `Orchestra Export Report\n\nGenerated: ${data.metadata.exportedAt}\nTotal Records: ${data.metadata.totalRecords}\n\n${JSON.stringify(data, null, 2)}`;
  };

  const downloadFile = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow ${className}`}>
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2">
          <span className="text-xl">📤</span>
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Orchestra Data Export
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Export construction intelligence data in multiple formats
            </p>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Data Type Selection */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
            Select Data Types
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {dataTypeOptions.map((option) => (
              <label key={option.id} className="flex items-center space-x-2 p-2 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-900 cursor-pointer">
                <input
                  type="checkbox"
                  checked={exportConfig.dataTypes.includes(option.id)}
                  onChange={(e) => handleDataTypeChange(option.id, e.target.checked)}
                  className="text-blue-600 rounded"
                />
                <span className="text-lg">{option.icon}</span>
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    {option.label}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {option.count} records
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Format Selection */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
            Export Formats
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
            {formatOptions.map((format) => (
              <label key={format.id} className="flex items-center space-x-2 p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-900 cursor-pointer">
                <input
                  type="checkbox"
                  checked={exportConfig.formats.includes(format.id)}
                  onChange={(e) => handleFormatChange(format.id, e.target.checked)}
                  className="text-blue-600 rounded"
                />
                <div className="text-center">
                  <div className="text-xl">{format.icon}</div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    {format.label}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {format.description}
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Export Options */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
              Export Options
            </h4>
            <div className="space-y-3">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={exportConfig.includeMetadata}
                  onChange={(e) => setExportConfig(prev => ({ ...prev, includeMetadata: e.target.checked }))}
                  className="text-blue-600 rounded"
                />
                <span className="text-sm text-gray-900 dark:text-white">Include metadata</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={exportConfig.includeAnalytics}
                  onChange={(e) => setExportConfig(prev => ({ ...prev, includeAnalytics: e.target.checked }))}
                  className="text-blue-600 rounded"
                />
                <span className="text-sm text-gray-900 dark:text-white">Include temporal analytics</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={exportConfig.includePredictions}
                  onChange={(e) => setExportConfig(prev => ({ ...prev, includePredictions: e.target.checked }))}
                  className="text-blue-600 rounded"
                />
                <span className="text-sm text-gray-900 dark:text-white">Include predictive analytics</span>
              </label>
            </div>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
              Date Range
            </h4>
            <div className="space-y-3">
              <div>
                <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Start Date</label>
                <input
                  type="date"
                  value={exportConfig.dateRange.start.toISOString().split('T')[0]}
                  onChange={(e) => setExportConfig(prev => ({
                    ...prev,
                    dateRange: { ...prev.dateRange, start: new Date(e.target.value) }
                  }))}
                  className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">End Date</label>
                <input
                  type="date"
                  value={exportConfig.dateRange.end.toISOString().split('T')[0]}
                  onChange={(e) => setExportConfig(prev => ({
                    ...prev,
                    dateRange: { ...prev.dateRange, end: new Date(e.target.value) }
                  }))}
                  className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-3">
          <button
            onClick={generatePreview}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 rounded-md transition-colors"
          >
            Generate Preview
          </button>
          <button
            onClick={performExport}
            disabled={isExporting || exportConfig.dataTypes.length === 0 || exportConfig.formats.length === 0}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-md transition-colors"
          >
            {isExporting ? 'Exporting...' : 'Export Data'}
          </button>
        </div>

        {/* Preview Data */}
        {previewData && (
          <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
              Export Preview
            </h4>
            <pre className="text-xs text-gray-600 dark:text-gray-400 bg-white dark:bg-gray-800 p-3 rounded border max-h-64 overflow-auto">
              {JSON.stringify(previewData, null, 2)}
            </pre>
          </div>
        )}

        {/* Export History */}
        {exportHistory.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
              Recent Exports
            </h4>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {exportHistory.map((export_) => (
                <div key={export_.id} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-900 rounded text-xs">
                  <div>
                    <div className="text-gray-900 dark:text-white">
                      {export_.dataTypes.join(', ')} • {export_.formats.join(', ')}
                    </div>
                    <div className="text-gray-500 dark:text-gray-400">
                      {export_.recordCount} records • {Math.round(export_.fileSize / 1024)}KB
                    </div>
                  </div>
                  <div className="text-gray-500 dark:text-gray-400">
                    {export_.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};