import { create } from 'zustand';
import { Project, RFI, BudgetItem } from '@/types/construction';

interface DataStore {
  projects: Project[];
  rfis: RFI[];
  budgetItems: BudgetItem[];
  lastSync: Date | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setProjects: (projects: Project[]) => void;
  setRFIs: (rfis: RFI[]) => void;
  setBudgetItems: (budgetItems: BudgetItem[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  updateLastSync: () => void;
  clearData: () => void;
}

export const useDataStore = create<DataStore>((set) => ({
  projects: [],
  rfis: [],
  budgetItems: [],
  lastSync: null,
  isLoading: false,
  error: null,

  setProjects: (projects) => set({ projects, error: null }),
  setRFIs: (rfis) => set({ rfis, error: null }),
  setBudgetItems: (budgetItems) => set({ budgetItems, error: null }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error, isLoading: false }),
  updateLastSync: () => set({ lastSync: new Date() }),
  clearData: () => set({ 
    projects: [], 
    rfis: [], 
    budgetItems: [], 
    lastSync: null, 
    error: null 
  }),
}));
