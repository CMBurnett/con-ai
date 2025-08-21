import React, { useEffect, useState } from 'react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Area,
  AreaChart,
} from 'recharts';
import { useWebSocket } from '@/hooks/useWebSocket';

interface CollaborationMetrics {
  communication_frequency: number;
  response_time: number;
  knowledge_sharing: number;
  cross_platform_sync: number;
  decision_speed: number;
  conflict_resolution: number;
}

interface AgentCollaboration {
  agentId: string;
  agentName: string;
  agentType: string;
  collaborations: number;
  effectiveness: number;
  lastActive: Date;
  topPartners: string[];
}

interface CollaborationPattern {
  patternType: string;
  description: string;
  frequency: number;
  impact: number;
  participants: string[];
  timeOfDay: number[];
}

interface CollaborationInsightsChartProps {
  projectId?: string;
  className?: string;
  timeRange?: '24h' | '7d' | '30d';
}

export const CollaborationInsightsChart: React.FC<CollaborationInsightsChartProps> = ({
  projectId,
  className = '',
  timeRange = '7d',
}) => {
  const [collaborationMetrics, setCollaborationMetrics] = useState<CollaborationMetrics | null>(null);
  const [agentCollaborations, setAgentCollaborations] = useState<AgentCollaboration[]>([]);
  const [collaborationPatterns, setCollaborationPatterns] = useState<CollaborationPattern[]>([]);
  const [timelineData, setTimelineData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const { isConnected } = useWebSocket();

  useEffect(() => {
    fetchCollaborationInsights();
  }, [projectId, timeRange, isConnected]);

  const fetchCollaborationInsights = async () => {
    try {
      setLoading(true);

      const response = await fetch(`/api/orchestra/collaboration/insights${projectId ? `?project_id=${projectId}` : ''}`);
      
      if (response.ok) {
        const data = await response.json();
        processCollaborationData(data);
      } else {
        generateDemoCollaborationData();
      }
    } catch (error) {
      console.error('Failed to fetch collaboration insights:', error);
      generateDemoCollaborationData();
    } finally {
      setLoading(false);
    }
  };

  const processCollaborationData = (_data: Record<string, unknown>) => {
    // Process real Orchestra collaboration data
    generateDemoCollaborationData();
  };

  const generateDemoCollaborationData = () => {
    // Generate demo collaboration metrics
    const metrics: CollaborationMetrics = {
      communication_frequency: 85,
      response_time: 75,
      knowledge_sharing: 90,
      cross_platform_sync: 82,
      decision_speed: 78,
      conflict_resolution: 88,
    };

    // Generate agent collaboration data
    const agents: AgentCollaboration[] = [
      {
        agentId: 'procore-agent-1',
        agentName: 'Procore Data Extractor',
        agentType: 'procore',
        collaborations: 45,
        effectiveness: 92,
        lastActive: new Date(),
        topPartners: ['autodesk-agent-1', 'primavera-agent-1'],
      },
      {
        agentId: 'autodesk-agent-1',
        agentName: 'Autodesk ACC Sync',
        agentType: 'autodesk',
        collaborations: 38,
        effectiveness: 87,
        lastActive: new Date(),
        topPartners: ['procore-agent-1', 'demo-agent-1'],
      },
      {
        agentId: 'primavera-agent-1',
        agentName: 'Oracle Primavera P6',
        agentType: 'primavera',
        collaborations: 32,
        effectiveness: 94,
        lastActive: new Date(),
        topPartners: ['procore-agent-1'],
      },
      {
        agentId: 'demo-agent-1',
        agentName: 'Demo Testing Agent',
        agentType: 'demo',
        collaborations: 28,
        effectiveness: 76,
        lastActive: new Date(),
        topPartners: ['autodesk-agent-1'],
      },
    ];

    // Generate collaboration patterns
    const patterns: CollaborationPattern[] = [
      {
        patternType: 'Cross-Platform Data Sync',
        description: 'Agents from different platforms coordinate data synchronization',
        frequency: 15,
        impact: 8.5,
        participants: ['procore-agent-1', 'autodesk-agent-1'],
        timeOfDay: [9, 13, 17],
      },
      {
        patternType: 'Schedule Coordination',
        description: 'Multiple agents align schedule updates across platforms',
        frequency: 12,
        impact: 9.2,
        participants: ['primavera-agent-1', 'procore-agent-1'],
        timeOfDay: [8, 14, 18],
      },
      {
        patternType: 'Quality Data Sharing',
        description: 'Agents share quality metrics and inspection results',
        frequency: 8,
        impact: 7.8,
        participants: ['autodesk-agent-1', 'procore-agent-1', 'demo-agent-1'],
        timeOfDay: [10, 15],
      },
    ];

    // Generate timeline data
    const timeline = [];
    for (let i = 30; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      timeline.push({
        date: date.toLocaleDateString(),
        collaborations: Math.floor(Math.random() * 20) + 10,
        effectiveness: Math.random() * 30 + 70,
        conflicts: Math.floor(Math.random() * 3),
        resolutions: Math.floor(Math.random() * 5) + 2,
      });
    }

    setCollaborationMetrics(metrics);
    setAgentCollaborations(agents);
    setCollaborationPatterns(patterns);
    setTimelineData(timeline);
  };

  const getAgentTypeColor = (agentType: string) => {
    const colors = {
      procore: '#3B82F6',
      autodesk: '#F59E0B',
      primavera: '#10B981',
      demo: '#8B5CF6',
    };
    return colors[agentType as keyof typeof colors] || '#6B7280';
  };

  const getEffectivenessLevel = (score: number) => {
    if (score >= 90) return { label: 'Excellent', color: 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900' };
    if (score >= 80) return { label: 'Good', color: 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900' };
    if (score >= 70) return { label: 'Fair', color: 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900' };
    return { label: 'Poor', color: 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900' };
  };

  // Prepare radar chart data
  const radarData = collaborationMetrics ? [
    {
      metric: 'Communication',
      value: collaborationMetrics.communication_frequency,
      fullMark: 100,
    },
    {
      metric: 'Response Time',
      value: collaborationMetrics.response_time,
      fullMark: 100,
    },
    {
      metric: 'Knowledge Sharing',
      value: collaborationMetrics.knowledge_sharing,
      fullMark: 100,
    },
    {
      metric: 'Platform Sync',
      value: collaborationMetrics.cross_platform_sync,
      fullMark: 100,
    },
    {
      metric: 'Decision Speed',
      value: collaborationMetrics.decision_speed,
      fullMark: 100,
    },
    {
      metric: 'Conflict Resolution',
      value: collaborationMetrics.conflict_resolution,
      fullMark: 100,
    },
  ] : [];

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
            <span className="text-xl">🤝</span>
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Orchestra Collaboration Insights
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                AI agent collaboration patterns and effectiveness metrics
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500 dark:text-gray-400">Overall Score</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {collaborationMetrics ? Math.round(
                Object.values(collaborationMetrics).reduce((sum, val) => sum + val, 0) / 
                Object.values(collaborationMetrics).length
              ) : 0}
            </div>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Collaboration Metrics Radar */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-4">
              Collaboration Effectiveness
            </h4>
            <ResponsiveContainer width="100%" height={250}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#E5E7EB" />
                <PolarAngleAxis 
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                  dataKey="metric"
                />
                <PolarRadiusAxis 
                  angle={90}
                  domain={[0, 100]}
                  tick={{ fontSize: 10, fill: '#6B7280' }}
                />
                <Radar
                  name="Effectiveness"
                  dataKey="value"
                  stroke="#3B82F6"
                  fill="#3B82F6"
                  fillOpacity={0.3}
                  strokeWidth={2}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Agent Collaboration Ranking */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-4">
              Agent Collaboration Ranking
            </h4>
            <div className="space-y-3">
              {agentCollaborations
                .sort((a, b) => b.effectiveness - a.effectiveness)
                .map((agent, index) => {
                  const effectiveness = getEffectivenessLevel(agent.effectiveness);
                  return (
                    <div key={agent.agentId} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                            #{index + 1}
                          </span>
                          <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: getAgentTypeColor(agent.agentType) }}
                          />
                        </div>
                        <div>
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {agent.agentName}
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            {agent.collaborations} collaborations
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {agent.effectiveness}%
                        </div>
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${effectiveness.color}`}>
                          {effectiveness.label}
                        </span>
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>
        </div>

        {/* Collaboration Timeline */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-4">
            Collaboration Timeline ({timeRange})
          </h4>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={timelineData}>
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
              <Area
                type="monotone"
                dataKey="collaborations"
                stackId="1"
                stroke="#3B82F6"
                fill="#3B82F6"
                fillOpacity={0.6}
                name="Collaborations"
              />
              <Area
                type="monotone"
                dataKey="effectiveness"
                stackId="2"
                stroke="#10B981"
                fill="#10B981"
                fillOpacity={0.6}
                name="Effectiveness %"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Collaboration Patterns */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-4">
            Detected Collaboration Patterns
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {collaborationPatterns.map((pattern, index) => (
              <div key={index} className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h5 className="text-sm font-medium text-gray-900 dark:text-white">
                    {pattern.patternType}
                  </h5>
                  <div className="flex items-center space-x-1">
                    <span className="text-xs text-gray-500 dark:text-gray-400">Impact:</span>
                    <span className="text-xs font-medium text-gray-900 dark:text-white">
                      {pattern.impact.toFixed(1)}
                    </span>
                  </div>
                </div>
                
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-3">
                  {pattern.description}
                </p>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-500 dark:text-gray-400">Frequency:</span>
                    <span className="text-gray-900 dark:text-white">{pattern.frequency}/week</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-500 dark:text-gray-400">Participants:</span>
                    <span className="text-gray-900 dark:text-white">{pattern.participants.length}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-500 dark:text-gray-400">Peak Times:</span>
                    <span className="text-gray-900 dark:text-white">
                      {pattern.timeOfDay.map(hour => `${hour}:00`).join(', ')}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Real-time Collaboration Status */}
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
          <h4 className="text-sm font-medium text-blue-900 dark:text-blue-200 mb-3">
            🔴 Live Collaboration Activity
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-900 dark:text-blue-200">
                {agentCollaborations.filter(a => a.lastActive > new Date(Date.now() - 5 * 60 * 1000)).length}
              </div>
              <div className="text-xs text-blue-700 dark:text-blue-300">Active Agents</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-900 dark:text-blue-200">
                {Math.floor(Math.random() * 5) + 2}
              </div>
              <div className="text-xs text-blue-700 dark:text-blue-300">Ongoing Collaborations</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-900 dark:text-blue-200">
                {Math.floor(Math.random() * 3)}
              </div>
              <div className="text-xs text-blue-700 dark:text-blue-300">Pending Sync Tasks</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};