export interface Project {
  id: string;
  name: string;
  status: 'planning' | 'active' | 'delayed' | 'completed';
  budget: number;
  actualCost: number;
  progress: number;
  startDate: Date;
  endDate: Date;
  platform: 'procore' | 'autodesk' | 'primavera';
}

export interface RFI {
  id: string;
  projectId: string;
  title: string;
  status: 'open' | 'pending' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'critical';
  createdDate: Date;
  dueDate?: Date;
  assignee: string;
}

export interface BudgetItem {
  category: string;
  budgeted: number;
  actual: number;
  variance: number;
  variancePercent: number;
}