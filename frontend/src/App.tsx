import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from '@/components/common/Layout';
import { DashboardEnhanced as Dashboard } from '@/pages/DashboardEnhanced';
import { Agents } from '@/pages/Agents';
import { DataTablesView } from '@/pages/DataTablesView';
import { Settings } from '@/pages/Settings';
import { Help } from '@/pages/Help';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/agents" element={<Agents />} />
            <Route path="/data" element={<DataTablesView />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/help" element={<Help />} />
          </Routes>
        </Layout>
      </Router>
    </ErrorBoundary>
  );
}

export default App;