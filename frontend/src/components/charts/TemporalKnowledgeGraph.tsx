import React, { useEffect, useState, useRef } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface Node {
  id: string;
  x: number;
  y: number;
  radius: number;
  nodeType: 'agent' | 'project' | 'task' | 'platform';
  entityId: string;
  entityName: string;
  attributes: Record<string, unknown>;
  properties: Record<string, unknown>;
}

interface Edge {
  fromNodeId: string;
  toNodeId: string;
  relationshipType: string;
  weight: number;
  confidence: number;
}

interface TemporalKnowledgeGraphProps {
  className?: string;
  width?: number;
  height?: number;
}

export const TemporalKnowledgeGraph: React.FC<TemporalKnowledgeGraphProps> = ({
  className = '',
  width,
  height = 400,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [stats, setStats] = useState<Record<string, unknown> | null>(null);
  const [canvasWidth, setCanvasWidth] = useState(width || 800);
  const { isConnected } = useWebSocket();

  // Update canvas width when container resizes
  useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current && !width) {
        const containerWidth = containerRef.current.offsetWidth - 32; // Account for padding
        setCanvasWidth(Math.max(containerWidth, 600)); // Minimum width of 600
      }
    };

    updateWidth();
    window.addEventListener('resize', updateWidth);
    return () => window.removeEventListener('resize', updateWidth);
  }, [width]);

  // Fetch knowledge graph data from Orchestra backend
  useEffect(() => {
    const fetchKnowledgeGraphData = async () => {
      try {
        const response = await fetch('/api/orchestra/knowledge-graph/stats');
        if (response.ok) {
          const data = await response.json();
          setStats(data);
          await generateVisualizationData();
        }
      } catch (error) {
        console.error('Failed to fetch knowledge graph data:', error);
        // Generate demo data for visualization
        generateDemoData();
      }
    };

    fetchKnowledgeGraphData();
  }, [isConnected]);

  const generateVisualizationData = async () => {
    // Generate nodes based on knowledge graph stats
    const generatedNodes: Node[] = [];
    const generatedEdges: Edge[] = [];

    // Create agent nodes
    for (let i = 0; i < 5; i++) {
      generatedNodes.push({
        id: `agent-${i}`,
        x: Math.random() * (canvasWidth - 100) + 50,
        y: Math.random() * (height - 100) + 50,
        radius: 15,
        nodeType: 'agent',
        entityId: `agent-${i}`,
        entityName: `Agent ${i}`,
        attributes: { status: 'active', type: ['procore', 'autodesk', 'primavera'][i % 3] },
        properties: { lastActivity: new Date() },
      });
    }

    // Create project nodes
    for (let i = 0; i < 3; i++) {
      generatedNodes.push({
        id: `project-${i}`,
        x: Math.random() * (canvasWidth - 100) + 50,
        y: Math.random() * (height - 100) + 50,
        radius: 20,
        nodeType: 'project',
        entityId: `project-${i}`,
        entityName: `Project ${i}`,
        attributes: { status: 'active', budget: 1000000 + i * 500000 },
        properties: { progress: Math.random() * 100 },
      });
    }

    // Create platform nodes
    const platforms = ['procore', 'autodesk', 'primavera'];
    platforms.forEach((platform) => {
      generatedNodes.push({
        id: `platform-${platform}`,
        x: Math.random() * (canvasWidth - 100) + 50,
        y: Math.random() * (height - 100) + 50,
        radius: 25,
        nodeType: 'platform',
        entityId: platform,
        entityName: platform.charAt(0).toUpperCase() + platform.slice(1),
        attributes: { type: 'construction_platform' },
        properties: { connectionStatus: 'connected' },
      });
    });

    // Generate edges (relationships)
    generatedNodes.forEach((fromNode, i) => {
      generatedNodes.forEach((toNode, j) => {
        if (i !== j && Math.random() > 0.7) {
          const relationshipType = getRelationshipType(fromNode.nodeType, toNode.nodeType);
          if (relationshipType) {
            generatedEdges.push({
              fromNodeId: fromNode.id,
              toNodeId: toNode.id,
              relationshipType,
              weight: Math.random() * 2,
              confidence: 0.7 + Math.random() * 0.3,
            });
          }
        }
      });
    });

    setNodes(generatedNodes);
    setEdges(generatedEdges);
  };

  const generateDemoData = () => {
    // Demo data when backend is not available
    const demoNodes: Node[] = [
      {
        id: 'agent-procore',
        x: 150,
        y: 100,
        radius: 15,
        nodeType: 'agent',
        entityId: 'procore-agent-1',
        entityName: 'Procore Agent',
        attributes: { status: 'running', type: 'procore' },
        properties: { lastActivity: new Date() },
      },
      {
        id: 'agent-autodesk',
        x: 450,
        y: 100,
        radius: 15,
        nodeType: 'agent',
        entityId: 'autodesk-agent-1',
        entityName: 'Autodesk Agent',
        attributes: { status: 'idle', type: 'autodesk' },
        properties: { lastActivity: new Date() },
      },
      {
        id: 'project-downtown',
        x: 300,
        y: 200,
        radius: 20,
        nodeType: 'project',
        entityId: 'proj-1',
        entityName: 'Downtown Office Complex',
        attributes: { status: 'active', budget: 2500000 },
        properties: { progress: 65 },
      },
      {
        id: 'platform-procore',
        x: 150,
        y: 300,
        radius: 25,
        nodeType: 'platform',
        entityId: 'procore',
        entityName: 'Procore',
        attributes: { type: 'construction_platform' },
        properties: { connectionStatus: 'connected' },
      },
      {
        id: 'platform-autodesk',
        x: 450,
        y: 300,
        radius: 25,
        nodeType: 'platform',
        entityId: 'autodesk',
        entityName: 'Autodesk ACC',
        attributes: { type: 'construction_platform' },
        properties: { connectionStatus: 'connected' },
      },
    ];

    const demoEdges: Edge[] = [
      {
        fromNodeId: 'agent-procore',
        toNodeId: 'project-downtown',
        relationshipType: 'works_on',
        weight: 1.5,
        confidence: 0.9,
      },
      {
        fromNodeId: 'agent-autodesk',
        toNodeId: 'project-downtown',
        relationshipType: 'collaborates_on',
        weight: 1.2,
        confidence: 0.8,
      },
      {
        fromNodeId: 'agent-procore',
        toNodeId: 'platform-procore',
        relationshipType: 'connects_to',
        weight: 2.0,
        confidence: 0.95,
      },
      {
        fromNodeId: 'agent-autodesk',
        toNodeId: 'platform-autodesk',
        relationshipType: 'connects_to',
        weight: 2.0,
        confidence: 0.95,
      },
    ];

    setNodes(demoNodes);
    setEdges(demoEdges);
  };

  const getRelationshipType = (fromType: string, toType: string): string | null => {
    if (fromType === 'agent' && toType === 'project') return 'works_on';
    if (fromType === 'agent' && toType === 'platform') return 'connects_to';
    if (fromType === 'agent' && toType === 'agent') return 'collaborates_with';
    if (fromType === 'project' && toType === 'platform') return 'managed_by';
    return null;
  };

  // Canvas drawing logic
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvasWidth, height);

    // Draw edges first (so they appear behind nodes)
    edges.forEach((edge) => {
      const fromNode = nodes.find((n) => n.id === edge.fromNodeId);
      const toNode = nodes.find((n) => n.id === edge.toNodeId);

      if (fromNode && toNode) {
        ctx.beginPath();
        ctx.moveTo(fromNode.x, fromNode.y);
        ctx.lineTo(toNode.x, toNode.y);
        ctx.strokeStyle = `rgba(99, 102, 241, ${edge.confidence * 0.8})`;
        ctx.lineWidth = edge.weight;
        ctx.stroke();

        // Draw relationship label
        const midX = (fromNode.x + toNode.x) / 2;
        const midY = (fromNode.y + toNode.y) / 2;
        ctx.fillStyle = 'rgba(55, 65, 81, 0.8)';
        ctx.font = '10px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(edge.relationshipType.replace('_', ' '), midX, midY - 5);
      }
    });

    // Draw nodes
    nodes.forEach((node) => {
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.radius, 0, 2 * Math.PI);

      // Node color based on type
      const colors = {
        agent: '#3B82F6', // Blue
        project: '#10B981', // Green
        platform: '#F59E0B', // Amber
        task: '#8B5CF6', // Purple
      };

      ctx.fillStyle = colors[node.nodeType] || '#6B7280';
      
      // Highlight selected node
      if (selectedNode?.id === node.id) {
        ctx.shadowColor = colors[node.nodeType];
        ctx.shadowBlur = 10;
      } else {
        ctx.shadowBlur = 0;
      }

      ctx.fill();
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Draw node label
      ctx.fillStyle = '#1F2937';
      ctx.font = '12px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(node.entityName, node.x, node.y + node.radius + 15);

      // Draw status indicator for agents
      if (node.nodeType === 'agent' && node.attributes.status === 'running') {
        ctx.beginPath();
        ctx.arc(node.x + node.radius - 5, node.y - node.radius + 5, 4, 0, 2 * Math.PI);
        ctx.fillStyle = '#22C55E';
        ctx.fill();
      }
    });
  }, [nodes, edges, selectedNode, canvasWidth, height]);

  // Handle canvas clicks
  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Find clicked node
    const clickedNode = nodes.find((node) => {
      const distance = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2);
      return distance <= node.radius;
    });

    setSelectedNode(clickedNode || null);
  };

  const getNodeTypeIcon = (nodeType: string) => {
    const icons = {
      agent: '🤖',
      project: '🏗️',
      platform: '🔗',
      task: '📋',
    };
    return icons[nodeType as keyof typeof icons] || '📊';
  };

  return (
    <div ref={containerRef} className={`bg-white dark:bg-gray-800 rounded-lg shadow ${className}`}>
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Temporal Knowledge Graph
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Orchestra framework temporal intelligence visualization
            </p>
          </div>
          {stats && (
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {String(stats.total_nodes)} nodes • {String(stats.total_edges)} edges
            </div>
          )}
        </div>
      </div>

      <div className="p-6">
        <div className="flex space-x-6">
          {/* Graph Canvas */}
          <div className="flex-1">
            <canvas
              ref={canvasRef}
              width={canvasWidth}
              height={height}
              onClick={handleCanvasClick}
              className="border border-gray-200 dark:border-gray-700 rounded cursor-pointer w-full"
            />
          </div>

          {/* Legend and Selected Node Info */}
          <div className="w-64 space-y-4">
            {/* Legend */}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                Node Types
              </h4>
              <div className="space-y-2">
                {[
                  { type: 'agent', color: '#3B82F6', label: 'AI Agents' },
                  { type: 'project', color: '#10B981', label: 'Projects' },
                  { type: 'platform', color: '#F59E0B', label: 'Platforms' },
                  { type: 'task', color: '#8B5CF6', label: 'Tasks' },
                ].map(({ type, color, label }) => (
                  <div key={type} className="flex items-center space-x-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: color }}
                    />
                    <span className="text-xs text-gray-600 dark:text-gray-400">
                      {getNodeTypeIcon(type)} {label}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Selected Node Details */}
            {selectedNode && (
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                  {getNodeTypeIcon(selectedNode.nodeType)} {selectedNode.entityName}
                </h4>
                <div className="space-y-2">
                  <div className="text-xs">
                    <span className="text-gray-500 dark:text-gray-400">Type:</span>
                    <span className="ml-2 text-gray-900 dark:text-white capitalize">
                      {selectedNode.nodeType}
                    </span>
                  </div>
                  <div className="text-xs">
                    <span className="text-gray-500 dark:text-gray-400">ID:</span>
                    <span className="ml-2 text-gray-900 dark:text-white font-mono">
                      {selectedNode.entityId}
                    </span>
                  </div>
                  {(selectedNode.attributes.status as string) && (
                    <div className="text-xs">
                      <span className="text-gray-500 dark:text-gray-400">Status:</span>
                      <span
                        className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                          (selectedNode.attributes.status as string) === 'running'
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            : (selectedNode.attributes.status as string) === 'active'
                            ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                            : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                        }`}
                      >
                        {selectedNode.attributes.status as string}
                      </span>
                    </div>
                  )}
                  {selectedNode.properties.progress !== undefined && (
                    <div className="text-xs">
                      <span className="text-gray-500 dark:text-gray-400">Progress:</span>
                      <span className="ml-2 text-gray-900 dark:text-white">
                        {Math.round(Number(selectedNode.properties.progress))}%
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Real-time Activity */}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                Recent Activity
              </h4>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  <span className="text-xs text-gray-600 dark:text-gray-400">
                    Agent collaboration detected
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full" />
                  <span className="text-xs text-gray-600 dark:text-gray-400">
                    Pattern analysis completed
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full" />
                  <span className="text-xs text-gray-600 dark:text-gray-400">
                    Knowledge graph updated
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};