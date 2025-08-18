import React, { useEffect } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useUIStore } from '@/stores/uiStore';
import { useAgentStore } from '@/stores/agentStore';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { isConnected, connectionStatus } = useWebSocket();
  const { sidebarOpen, notifications } = useUIStore();
  const { setAgents } = useAgentStore();

  // Initialize with some demo agents for testing
  useEffect(() => {
    const demoAgents = [
      {
        id: 'procore-agent-1',
        name: 'Procore Data Extractor',
        type: 'procore' as const,
        status: 'idle' as const,
        progress: 0,
        config: {
          id: 'procore-agent-1',
          agentType: 'procore',
          settings: {
            baseUrl: 'https://app.procore.com',
            projectId: 'demo-project',
          },
        },
      },
      {
        id: 'autodesk-agent-1',
        name: 'Autodesk ACC Sync',
        type: 'autodesk' as const,
        status: 'idle' as const,
        progress: 0,
        config: {
          id: 'autodesk-agent-1',
          agentType: 'autodesk',
          settings: {
            hubId: 'demo-hub',
            projectId: 'demo-project',
          },
        },
      },
      {
        id: 'demo-agent-1',
        name: 'Demo Testing Agent',
        type: 'demo' as const,
        status: 'idle' as const,
        progress: 0,
        config: {
          id: 'demo-agent-1',
          agentType: 'demo',
          settings: {
            simulationDuration: 10,
            stepCount: 5,
          },
        },
      },
    ];
    setAgents(demoAgents);
  }, [setAgents]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Notifications */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {notifications.map((notification) => (
          <NotificationCard key={notification.id} notification={notification} />
        ))}
      </div>

      {/* Connection Status Bar */}
      {!isConnected && (
        <div className="bg-red-500 text-white px-4 py-2 text-sm text-center">
          <span className="font-medium">Disconnected from server</span>
          <span className="ml-2 capitalize">({connectionStatus})</span>
        </div>
      )}

      <div className="flex h-screen">
        {/* Sidebar */}
        <Sidebar isOpen={sidebarOpen} />

        {/* Main Content */}
        <div className={`flex-1 flex flex-col transition-all duration-200 ${
          sidebarOpen ? 'ml-64' : 'ml-16'
        }`}>
          {/* Header */}
          <Header />

          {/* Page Content */}
          <main className="flex-1 overflow-auto p-6">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
};

// Notification Card Component
interface NotificationCardProps {
  notification: {
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    title: string;
    message: string;
    timestamp: Date;
  };
}

const NotificationCard: React.FC<NotificationCardProps> = ({ notification }) => {
  const removeNotification = useUIStore(state => state.removeNotification);

  const bgColor = {
    success: 'bg-green-500',
    error: 'bg-red-500', 
    warning: 'bg-yellow-500',
    info: 'bg-blue-500',
  }[notification.type];

  const icon = {
    success: '',
    error: '',
    warning: ' ',
    info: '9',
  }[notification.type];

  return (
    <div className={`${bgColor} text-white p-4 rounded-lg shadow-lg max-w-sm transition-all duration-300`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-2">
          <span className="text-lg font-bold">{icon}</span>
          <div>
            <h4 className="font-medium text-sm">{notification.title}</h4>
            <p className="text-xs mt-1 opacity-90">{notification.message}</p>
          </div>
        </div>
        <button
          onClick={() => removeNotification(notification.id)}
          className="text-white hover:text-gray-200 text-lg leading-none"
        >
          ×
        </button>
      </div>
    </div>
  );
};
