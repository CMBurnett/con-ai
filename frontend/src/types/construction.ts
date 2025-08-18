export interface Project {
  id: string;
  name: string;
  status: 'planning' | 'active' | 'delayed' | 'completed';
  budget: number;
  progress: number;
  startDate: Date;
  endDate: Date;
  manager: string;
  platform?: 'procore' | 'autodesk' | 'primavera';
}

export interface RFI {
  id: string;
  projectId: string;
  title: string;
  description: string;
  status: 'open' | 'pending' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'critical';
  submittedBy: string;
  submittedDate: Date;
  dueDate?: Date;
}

export interface BudgetItem {
  id: string;
  projectId: string;
  category: string;
  budgetedAmount: number;
  actualAmount: number;
}