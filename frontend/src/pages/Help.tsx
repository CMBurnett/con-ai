import React from 'react';

export const Help: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Help & Documentation
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Learn how to use Con-AI and the Orchestra framework
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Getting Started */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Getting Started</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-900 dark:text-white">1. Connect to Platforms</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Configure agents for Procore, Autodesk Construction Cloud, or Primavera P6
                </p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-900 dark:text-white">2. Start Agents</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Launch AI agents to extract and synchronize project data
                </p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-900 dark:text-white">3. Monitor Progress</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Track real-time updates and view extracted construction data
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Key Features</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center mt-0.5">
                  <svg className="w-3 h-3 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">Real-time Synchronization</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Live updates from construction platforms</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center mt-0.5">
                  <svg className="w-3 h-3 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">AI-Powered Intelligence</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Automated data extraction and analysis</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center mt-0.5">
                  <svg className="w-3 h-3 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">Multi-Platform Support</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Works with major construction software</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Troubleshooting */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Troubleshooting</h3>
        </div>
        <div className="p-6">
          <div className="space-y-6">
            <div>
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Common Issues</h4>
              <div className="space-y-4">
                <div>
                  <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300">Agent Won't Start</h5>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Check that the backend server is running on port 8080 and WebSocket connection is established.
                  </p>
                </div>
                <div>
                  <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300">Connection Issues</h5>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Verify your network connection and ensure the Orchestra backend is accessible.
                  </p>
                </div>
                <div>
                  <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300">No Data Appearing</h5>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Make sure agents are properly configured with valid platform credentials.
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Support</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                For additional support, check the GitHub repository or contact the development team.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
