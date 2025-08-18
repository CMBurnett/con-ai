import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  Legend,
  ReferenceLine,
} from 'recharts';
import { useWebSocket } from '@/hooks/useWebSocket';

interface PredictionData {
  prediction_type: string;
  predicted_drift_days?: number;
  predicted_variance_percent?: number;
  predicted_risk_probability?: number;
  predicted_effectiveness_score?: number;
  confidence_score: number;
  risk_level: string;
  recommendations: string[];
  contributing_factors?: any;
}

interface HistoricalDataPoint {
  date: string;
  actual: number;
  predicted: number;
  confidence: number;
}

interface PredictiveAnalyticsChartProps {
  projectId: string;
  predictionType: 'schedule_drift' | 'budget_variance' | 'quality_issues' | 'collaboration_effectiveness';
  className?: string;
  showHistorical?: boolean;
}

export const PredictiveAnalyticsChart: React.FC<PredictiveAnalyticsChartProps> = ({
  projectId,
  predictionType,
  className = '',
  showHistorical = true,
}) => {
  const [predictionData, setPredictionData] = useState<PredictionData | null>(null);
  const [historicalData, setHistoricalData] = useState<HistoricalDataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { isConnected } = useWebSocket();

  useEffect(() => {
    fetchPredictionData();
    if (showHistorical) {
      generateHistoricalData();
    }
  }, [projectId, predictionType, isConnected]);

  const fetchPredictionData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/orchestra/predictions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_id: projectId,
          prediction_types: [predictionType],
          horizon_days: 30,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setPredictionData(data.predictions[predictionType]);
      } else {
        // Generate demo prediction data
        generateDemoPredictionData();
      }
    } catch (error) {
      console.error('Failed to fetch prediction data:', error);
      generateDemoPredictionData();
    } finally {
      setLoading(false);
    }
  };

  const generateDemoPredictionData = () => {
    const demoData: Record<string, PredictionData> = {
      schedule_drift: {
        prediction_type: 'schedule_drift',
        predicted_drift_days: 5.2,
        confidence_score: 0.85,
        risk_level: 'medium',
        recommendations: [
          'Increase resource allocation to critical tasks',
          'Review dependencies for potential bottlenecks',
          'Implement daily stand-ups for better coordination',
        ],
        contributing_factors: {
          resource_utilization: 0.78,
          weather_impact: 0.15,
          change_orders: 2,
        },
      },
      budget_variance: {
        prediction_type: 'budget_variance',
        predicted_variance_percent: 8.5,
        confidence_score: 0.78,
        risk_level: 'medium',
        recommendations: [
          'Review material cost estimates',
          'Negotiate better rates with suppliers',
          'Implement cost control measures',
        ],
        contributing_factors: {
          material_cost_variance: 0.12,
          labor_cost_variance: 0.05,
          change_orders: 3,
        },
      },
      quality_issues: {
        prediction_type: 'quality_issues',
        predicted_risk_probability: 0.35,
        confidence_score: 0.72,
        risk_level: 'medium',
        recommendations: [
          'Increase quality inspections',
          'Review contractor performance',
          'Implement additional training programs',
        ],
      },
      collaboration_effectiveness: {
        prediction_type: 'collaboration_effectiveness',
        predicted_effectiveness_score: 0.73,
        confidence_score: 0.68,
        risk_level: 'good',
        recommendations: [
          'Improve communication protocols',
          'Implement project management tools',
          'Schedule regular team coordination meetings',
        ],
      },
    };

    setPredictionData(demoData[predictionType]);
  };

  const generateHistoricalData = () => {
    const data: HistoricalDataPoint[] = [];
    const baseValue = getBaseValue();
    
    for (let i = 30; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      const trend = Math.sin(i * 0.3) * 2;
      const noise = (Math.random() - 0.5) * baseValue * 0.2;
      const actual = Math.max(0, baseValue + trend + noise);
      const predicted = actual + (Math.random() - 0.5) * baseValue * 0.1;
      
      data.push({
        date: date.toLocaleDateString(),
        actual: Math.round(actual * 100) / 100,
        predicted: Math.round(predicted * 100) / 100,
        confidence: 0.6 + Math.random() * 0.3,
      });
    }
    
    setHistoricalData(data);
  };

  const getBaseValue = () => {
    switch (predictionType) {
      case 'schedule_drift':
        return 3;
      case 'budget_variance':
        return 5;
      case 'quality_issues':
        return 0.3;
      case 'collaboration_effectiveness':
        return 0.7;
      default:
        return 1;
    }
  };

  const getChartConfig = () => {
    switch (predictionType) {
      case 'schedule_drift':
        return {
          title: 'Schedule Drift Prediction',
          unit: 'days',
          color: '#EF4444',
          description: 'Predicted delay in project schedule',
          icon: '📅',
        };
      case 'budget_variance':
        return {
          title: 'Budget Variance Prediction',
          unit: '%',
          color: '#F59E0B',
          description: 'Predicted budget overrun percentage',
          icon: '💰',
        };
      case 'quality_issues':
        return {
          title: 'Quality Issues Risk',
          unit: 'probability',
          color: '#8B5CF6',
          description: 'Probability of quality issues occurring',
          icon: '⚠️',
        };
      case 'collaboration_effectiveness':
        return {
          title: 'Collaboration Effectiveness',
          unit: 'score',
          color: '#10B981',
          description: 'Team collaboration effectiveness score',
          icon: '🤝',
        };
      default:
        return {
          title: 'Prediction',
          unit: '',
          color: '#6B7280',
          description: 'Predictive analytics',
          icon: '📊',
        };
    }
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low':
        return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900';
      case 'high':
        return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900';
      case 'good':
        return 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900';
      case 'excellent':
        return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900';
      default:
        return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900';
    }
  };

  const formatValue = (value: number, unit: string) => {
    if (unit === 'probability') {
      return `${Math.round(value * 100)}%`;
    }
    if (unit === 'score') {
      return `${Math.round(value * 100)}/100`;
    }
    return `${value}${unit}`;
  };

  const getCurrentPredictionValue = () => {
    if (!predictionData) return 0;
    
    switch (predictionType) {
      case 'schedule_drift':
        return predictionData.predicted_drift_days || 0;
      case 'budget_variance':
        return predictionData.predicted_variance_percent || 0;
      case 'quality_issues':
        return predictionData.predicted_risk_probability || 0;
      case 'collaboration_effectiveness':
        return predictionData.predicted_effectiveness_score || 0;
      default:
        return 0;
    }
  };

  const config = getChartConfig();

  if (loading) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-lg shadow animate-pulse ${className}`}>
        <div className="p-6">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded mb-4" />
          <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded" />
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow ${className}`}>
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-xl">{config.icon}</span>
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                {config.title}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {config.description}
              </p>
            </div>
          </div>
          {predictionData && (
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatValue(getCurrentPredictionValue(), config.unit)}
              </div>
              <div className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getRiskLevelColor(predictionData.risk_level)}`}>
                {predictionData.risk_level} risk
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="p-6">
        {showHistorical && historicalData.length > 0 && (
          <div className="mb-6">
            <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-4">
              Historical Trend & Prediction
            </h4>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={historicalData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis 
                  dataKey="date" 
                  stroke="#6B7280"
                  fontSize={12}
                  tick={{ fill: '#6B7280' }}
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
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="actual"
                  stroke="#3B82F6"
                  strokeWidth={2}
                  dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                  name="Actual"
                />
                <Line
                  type="monotone"
                  dataKey="predicted"
                  stroke={config.color}
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={{ fill: config.color, strokeWidth: 2, r: 4 }}
                  name="Predicted"
                />
                {predictionData && (
                  <ReferenceLine 
                    y={getCurrentPredictionValue()} 
                    stroke={config.color}
                    strokeDasharray="8 8"
                    label={{ value: "Current Prediction", position: "right" }}
                  />
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {predictionData && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Confidence & Risk */}
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                Prediction Confidence
              </h4>
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Confidence</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {Math.round(predictionData.confidence_score * 100)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${predictionData.confidence_score * 100}%` }}
                  />
                </div>
              </div>

              {predictionData.contributing_factors && (
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                    Contributing Factors
                  </h4>
                  <div className="space-y-2">
                    {Object.entries(predictionData.contributing_factors).map(([factor, value]) => (
                      <div key={factor} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                          {factor.replace('_', ' ')}
                        </span>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {typeof value === 'number' ? 
                            (value < 1 ? `${Math.round(value * 100)}%` : value) : 
                            value
                          }
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Recommendations */}
            <div>
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                AI Recommendations
              </h4>
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                <ul className="space-y-2">
                  {predictionData.recommendations.map((recommendation, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0" />
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {recommendation}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};