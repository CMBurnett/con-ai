import { create } from 'zustand';

interface UIStore {
  sidebarOpen: boolean;
  currentPage: string;
  notifications: Notification[];
  theme: 'light' | 'dark';
  isOnline: boolean;
  
  // Actions
  setSidebarOpen: (open: boolean) => void;
  setCurrentPage: (page: string) => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  setOnlineStatus: (online: boolean) => void;
  clearNotifications: () => void;
}

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  duration?: number; // Auto-dismiss after duration (ms)
}

export const useUIStore = create<UIStore>((set, get) => ({
  sidebarOpen: true,
  currentPage: 'dashboard',
  notifications: [],
  theme: 'light',
  isOnline: navigator.onLine,

  setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
  setCurrentPage: (currentPage) => set({ currentPage }),
  
  addNotification: (notification) => set((state) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
    };
    
    // Auto-remove notification after duration
    if (notification.duration) {
      setTimeout(() => {
        get().removeNotification(newNotification.id);
      }, notification.duration);
    }
    
    return {
      notifications: [...state.notifications, newNotification],
    };
  }),
  
  removeNotification: (id) => set((state) => ({
    notifications: state.notifications.filter(n => n.id !== id),
  })),
  
  setTheme: (theme) => set({ theme }),
  setOnlineStatus: (isOnline) => set({ isOnline }),
  clearNotifications: () => set({ notifications: [] }),
}));

// Hook to automatically update online status
if (typeof window !== 'undefined') {
  window.addEventListener('online', () => useUIStore.getState().setOnlineStatus(true));
  window.addEventListener('offline', () => useUIStore.getState().setOnlineStatus(false));
}
