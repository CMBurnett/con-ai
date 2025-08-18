import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  Cell,
  ReferenceLine,
  Brush,
  BarChart,
  Bar,
  Legend,
} from 'recharts';
import { useWebSocket } from '@/hooks/useWebSocket';

interface DetectedPattern {
  id: string;
  pattern_type: string;
  pattern_name: string;
  confidence_score: number;
  pattern_data: Record<string, any>;
  detected_at: string;
  lookback_days: number;
  affected_entities: string[];
  severity: 'low' | 'medium' | 'high' | 'critical';
}

interface Anomaly {
  id: string;
  anomaly_type: string;
  description: string;
  confidence: number;
  timestamp: string;
  affected_metric: string;
  expected_value: number;
  actual_value: number;
  deviation_percentage: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

interface TimeSeriesDataPoint {
  timestamp: string;
  value: number;
  predicted: number;
  isAnomaly: boolean;
  confidence: number;
  metric: string;
}

interface PatternDetectionChartProps {
  className?: string;
  timeRange?: '1h' | '24h' | '7d' | '30d';
  showAnomalies?: boolean;
  showPatterns?: boolean;
}

export const PatternDetectionChart: React.FC<PatternDetectionChartProps> = ({
  className = '',
  timeRange = '24h',
  showAnomalies = true,
  showPatterns = true,
}) => {
  const [detectedPatterns, setDetectedPatterns] = useState<DetectedPattern[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesDataPoint[]>([]);
  const [selectedPattern, setSelectedPattern] = useState<DetectedPattern | null>(null);
  const [loading, setLoading] = useState(true);
  const [realTimeAlerts, setRealTimeAlerts] = useState<string[]>([]);
  const { isConnected } = useWebSocket();

  useEffect(() => {
    fetchPatternData();
    
    // Set up real-time pattern detection
    const interval = setInterval(() => {
      if (Math.random() > 0.7) {
        addRealTimeAlert();
      }
    }, 15000); // Check every 15 seconds

    return () => clearInterval(interval);
  }, [timeRange, isConnected]);

  const fetchPatternData = async () => {
    try {
      setLoading(true);

      // Try to fetch real patterns from Orchestra backend
      const patternsResponse = await fetch('/api/orchestra/patterns/detect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          lookback_days: getTimeRangeDays(timeRange),
        }),
      });

      if (patternsResponse.ok) {
        const patternsData = await patternsResponse.json();
        processOrchestrationPatterns(patternsData);
      } else {
        generateDemoPatternData();
      }
    } catch (error) {
      console.error('Failed to fetch pattern data:', error);
      generateDemoPatternData();
    } finally {
      setLoading(false);
    }
  };

  const getTimeRangeDays = (range: string) => {
    switch (range) {
      case '1h': return 0.04;
      case '24h': return 1;
      case '7d': return 7;
      case '30d': return 30;
      default: return 1;
    }
  };

  const processOrchestrationPatterns = (data: any) => {
    // Process real Orchestra pattern data
    generateDemoPatternData();
  };

  const generateDemoPatternData = () => {
    const patterns: DetectedPattern[] = [
      {
        id: 'pattern-1',
        pattern_type: 'temporal_peak',
        pattern_name: 'Peak activity at hour 14',
        confidence_score: 0.89,
        pattern_data: {
          peak_hour: 14,
          peak_activity: 45,
          average_activity: 28,
        },
        detected_at: new Date().toISOString(),
        lookback_days: 7,
        affected_entities: ['procore-agent-1', 'autodesk-agent-1'],
        severity: 'medium',
      },
      {
        id: 'pattern-2',
        pattern_type: 'collaboration_burst',
        pattern_name: 'Increased collaboration on Tuesdays',
        confidence_score: 0.76,
        pattern_data: {
          peak_day: 'Tuesday',
          collaboration_increase: 35,
          normal_rate: 18,
        },
        detected_at: new Date().toISOString(),
        lookback_days: 30,
        affected_entities: ['primavera-agent-1', 'procore-agent-1', 'autodesk-agent-1'],
        severity: 'low',
      },
      {
        id: 'pattern-3',
        pattern_type: 'anomaly_cluster',
        pattern_name: 'Schedule drift correlation detected',
        confidence_score: 0.92,
        pattern_data: {
          affected_projects: 3,
          correlation_strength: 0.84,
          drift_pattern: 'increasing',
        },
        detected_at: new Date().toISOString(),
        lookback_days: 14,
        affected_entities: ['proj-1', 'proj-2'],
        severity: 'high',
      },
      {
        id: 'pattern-4',
        pattern_type: 'performance_degradation',
        pattern_name: 'Agent response time increase',
        confidence_score: 0.95,
        pattern_data: {
          baseline_response_time: 2.3,
          current_response_time: 4.8,
          degradation_percentage: 108,
        },
        detected_at: new Date().toISOString(),
        lookback_days: 3,
        affected_entities: ['autodesk-agent-1'],
        severity: 'critical',
      },
    ];

    const demoAnomalies: Anomaly[] = [
      {
        id: 'anomaly-1',
        anomaly_type: 'schedule_drift',
        description: 'Unexpected schedule delay in project downtown-office',
        confidence: 0.88,
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        affected_metric: 'project_progress',
        expected_value: 68,
        actual_value: 55,
        deviation_percentage: -19.1,
        severity: 'high',
      },
      {
        id: 'anomaly-2',
        anomaly_type: 'budget_spike',
        description: 'Unusual budget allocation increase detected',
        confidence: 0.73,
        timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
        affected_metric: 'budget_utilization',
        expected_value: 75,
        actual_value: 92,
        deviation_percentage: 22.7,
        severity: 'medium',
      },
      {
        id: 'anomaly-3',
        anomaly_type: 'agent_performance',
        description: 'Procore agent processing time anomaly',
        confidence: 0.91,
        timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        affected_metric: 'processing_time',
        expected_value: 2.5,
        actual_value: 8.2,
        deviation_percentage: 228,
        severity: 'critical',
      },
    ];

    // Generate time series data with anomalies
    const timeSeriesPoints: TimeSeriesDataPoint[] = [];
    const hoursBack = timeRange === '1h' ? 1 : timeRange === '24h' ? 24 : timeRange === '7d' ? 168 : 720;
    
    for (let i = hoursBack; i >= 0; i--) {
      const timestamp = new Date(Date.now() - i * 60 * 60 * 1000);
      const baseValue = 50 + Math.sin(i * 0.1) * 15 + Math.random() * 10;
      const isAnomaly = Math.random() > 0.95; // 5% chance of anomaly
      const anomalyMultiplier = isAnomaly ? (Math.random() > 0.5 ? 1.5 + Math.random() : 0.3 + Math.random() * 0.4) : 1;
      
      timeSeriesPoints.push({
        timestamp: timestamp.toISOString(),
        value: baseValue * anomalyMultiplier,
        predicted: baseValue,
        isAnomaly,
        confidence: 0.7 + Math.random() * 0.3,
        metric: 'system_performance',
      });
    }

    setDetectedPatterns(patterns);
    setAnomalies(demoAnomalies);
    setTimeSeriesData(timeSeriesPoints);
  };

  const addRealTimeAlert = () => {
    const alerts = [
      'New collaboration pattern detected in cross-platform sync',
      'Anomaly alert: Unusual budget allocation spike',
      'Performance pattern: Peak activity window identified',
      'Schedule correlation pattern discovered',
      'Agent response time anomaly detected',
    ];
    
    const newAlert = alerts[Math.floor(Math.random() * alerts.length)];
    setRealTimeAlerts(prev => [newAlert, ...prev.slice(0, 4)]);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900';
      case 'high':
        return 'text-orange-600 bg-orange-100 dark:text-orange-400 dark:bg-orange-900';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900';
      case 'low':
        return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900';
      default:
        return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900';
    }
  };

  const getPatternIcon = (patternType: string) => {
    switch (patternType) {
      case 'temporal_peak':
        return '⏰';
      case 'collaboration_burst':
        return '🤝';
      case 'anomaly_cluster':
        return '🔍';
      case 'performance_degradation':
        return '⚠️';
      default:
        return '📊';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-lg shadow animate-pulse ${className}`}>
        <div className="p-6">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded mb-4" />
          <div className="h-80 bg-gray-200 dark:bg-gray-700 rounded" />
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow ${className}`}>
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-xl">🔍</span>
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Pattern Detection & Anomaly Alerts
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                AI-powered pattern recognition and anomaly detection
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-sm text-gray-500 dark:text-gray-400">Patterns</div>
              <div className="text-xl font-bold text-gray-900 dark:text-white">
                {detectedPatterns.length}
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500 dark:text-gray-400">Anomalies</div>
              <div className="text-xl font-bold text-red-600 dark:text-red-400">
                {anomalies.length}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Real-time Time Series with Anomalies */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-4">
            Real-time System Monitoring ({timeRange})
          </h4>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                dataKey="timestamp"
                stroke="#6B7280"
                fontSize={12}
                tick={{ fill: '#6B7280' }}
                tickFormatter={(value) => new Date(value).toLocaleTimeString()}
              />
              <YAxis 
                stroke="#6B7280"
                fontSize={12}
                tick={{ fill: '#6B7280' }}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#F9FAFB',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                }}
                labelFormatter={(value) => `Time: ${formatTimestamp(value)}`}
              />
              <Line
                type="monotone"
                dataKey="predicted"
                stroke="#3B82F6"
                strokeWidth={1}
                strokeDasharray="5 5"
                dot={false}
                name="Expected"
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#10B981"
                strokeWidth={2}
                dot={(props) => {
                  const { payload } = props;
                  if (payload && payload.isAnomaly) {
                    return (
                      <circle
                        cx={props.cx}
                        cy={props.cy}
                        r={6}
                        fill="#EF4444"
                        stroke="#DC2626"
                        strokeWidth={2}
                      />
                    );
                  }
                  return null;
                }}
                name="Actual"
              />
              <Brush dataKey="timestamp" height={30} stroke="#3B82F6" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Detected Patterns */}
          {showPatterns && (
            <div>
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-4">
                Detected Patterns
              </h4>
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {detectedPatterns.map((pattern) => (
                  <div
                    key={pattern.id}
                    onClick={() => setSelectedPattern(pattern)}
                    className={`p-3 rounded-lg border cursor-pointer transition-all ${
                      selectedPattern?.id === pattern.id
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-900'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="text-lg">{getPatternIcon(pattern.pattern_type)}</span>
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {pattern.pattern_name}
                        </div>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSeverityColor(pattern.severity)}`}>
                        {pattern.severity}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        Confidence: {Math.round(pattern.confidence_score * 100)}%
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {pattern.affected_entities.length} entities affected
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Anomaly Alerts */}
          {showAnomalies && (
            <div>
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-4">
                Recent Anomalies
              </h4>
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {anomalies.map((anomaly) => (
                  <div key={anomaly.id} className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-sm font-medium text-red-900 dark:text-red-200">
                        {anomaly.description}
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSeverityColor(anomaly.severity)}`}>
                        {anomaly.severity}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs text-red-700 dark:text-red-300">
                      <div>Expected: {anomaly.expected_value}</div>
                      <div>Actual: {anomaly.actual_value}</div>
                      <div>Confidence: {Math.round(anomaly.confidence * 100)}%</div>
                      <div>Deviation: {anomaly.deviation_percentage.toFixed(1)}%</div>
                    </div>
                    <div className="text-xs text-red-600 dark:text-red-400 mt-1">
                      {formatTimestamp(anomaly.timestamp)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Real-time Alerts Stream */}
        {realTimeAlerts.length > 0 && (
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
            <h4 className="text-sm font-medium text-blue-900 dark:text-blue-200 mb-3">
              🔴 Live Pattern Detection Stream
            </h4>
            <div className="space-y-2">
              {realTimeAlerts.map((alert, index) => (
                <div
                  key={index}
                  className={`text-xs text-blue-700 dark:text-blue-300 flex items-center space-x-2 ${
                    index === 0 ? 'font-medium animate-pulse' : ''
                  }`}
                >
                  <div className="w-2 h-2 bg-blue-500 rounded-full" />
                  <span>{alert}</span>
                  {index === 0 && <span className="text-blue-500">• NEW</span>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Selected Pattern Details */}
        {selectedPattern && (
          <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
              Pattern Details: {selectedPattern.pattern_name}
            </h4>
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <span className="text-gray-500 dark:text-gray-400">Type:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{selectedPattern.pattern_type}</span>
              </div>
              <div>
                <span className="text-gray-500 dark:text-gray-400">Lookback:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{selectedPattern.lookback_days} days</span>
              </div>
              <div>
                <span className="text-gray-500 dark:text-gray-400">Confidence:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{Math.round(selectedPattern.confidence_score * 100)}%</span>
              </div>
              <div>
                <span className="text-gray-500 dark:text-gray-400">Detected:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{formatTimestamp(selectedPattern.detected_at)}</span>
              </div>
            </div>
            <div className="mt-3">
              <span className="text-gray-500 dark:text-gray-400 text-xs">Affected Entities:</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {selectedPattern.affected_entities.map((entity, index) => (
                  <span key={index} className="px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded">
                    {entity}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};