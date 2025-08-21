export type AgentType = 'procore' | 'autodesk' | 'primavera' | 'msproject' | 'email' | 'demo';

export interface Agent {
  id: string;
  name: string;
  type: AgentType;
  status: 'idle' | 'running' | 'error' | 'completed';
  progress: number;
  lastRun?: Date;
  config: AgentConfig;
}

export interface AgentConfig {
  id: string;
  agentType: string;
  settings: Record<string, any>;
  schedule?: ScheduleConfig;
}

export interface ScheduleConfig {
  enabled: boolean;
  frequency: 'hourly' | 'daily' | 'weekly';
  time?: string;
}

export interface AgentUpdate {
  agentId: string;
  status: Agent['status'];
  progress: number;
  message: string;
  data?: any;
  timestamp: Date;
}