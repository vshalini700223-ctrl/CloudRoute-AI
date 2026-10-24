import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import DashboardPage from './pages/DashboardPage';
import SimulatorPage from './pages/SimulatorPage';
import ComparisonPage from './pages/ComparisonPage';
import HistoryPage from './pages/HistoryPage';
import AboutPage from './pages/AboutPage';
import CloudRouteAPI from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [backendHealthy, setBackendHealthy] = useState(false);
  const [isCheckingHealth, setIsCheckingHealth] = useState(false);
  const [isSeeding, setIsSeeding] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  // Real backend metrics and resource state
  const [metrics, setMetrics] = useState({
    total_virtual_servers: 0,
    total_tasks: 0,
    allocated_tasks: 0,
    unallocated_tasks: 0,
    avg_server_utilization: null,
    latest_makespan: null,
    has_simulations: false,
  });
  const [servers, setServers] = useState([]);
  const [simulations, setSimulations] = useState([]);

  const showToast = (message, type = 'info') => {
    setToastMessage({ message, type });
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Ping backend health
  const checkHealth = useCallback(async () => {
    setIsCheckingHealth(true);
    try {
      const data = await CloudRouteAPI.checkHealth();
      setBackendHealthy(data.status === 'healthy');
    } catch {
      setBackendHealthy(false);
    } finally {
      setIsCheckingHealth(false);
    }
  }, []);

  // Fetch all live data from backend
  const loadData = useCallback(async (showNotification = false) => {
    setIsRefreshing(true);
    try {
      const [m, s, sim] = await Promise.all([
        CloudRouteAPI.getDashboardMetrics().catch(() => null),
        CloudRouteAPI.getServers().catch(() => []),
        CloudRouteAPI.getSimulations().catch(() => []),
      ]);

      if (m) {
        setMetrics(m);
      }
      if (s) {
        setServers(s);
      }
      if (sim) {
        setSimulations(sim);
      }

      if (showNotification) {
        showToast('Dashboard resources and metrics refreshed from backend.', 'success');
      }
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    checkHealth();
    loadData();
  }, [checkHealth, loadData]);

  // Seed 4 default virtual servers
  const handleSeedTopology = async () => {
    setIsSeeding(true);
    try {
      const result = await CloudRouteAPI.seedDefaultResources();
      showToast(result.message || '4 Virtual Cloud Servers initialized successfully!', 'success');
      await loadData();
    } catch (err) {
      showToast(`Error initializing topology: ${err.message}`, 'error');
    } finally {
      setIsSeeding(false);
    }
  };

  const tabTitles = {
    dashboard: 'Resource Dashboard',
    simulator: 'Workload Simulator',
    comparison: 'Algorithm Comparison',
    history: 'Simulation History',
    about: 'About CloudRoute AI',
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#f8fafc' }}>
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        backendHealthy={backendHealthy}
        isCheckingHealth={isCheckingHealth}
        onRefreshHealth={checkHealth}
      />

      {/* Main Content Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <Navbar
          activeTabTitle={tabTitles[activeTab]}
          onSeedTopology={handleSeedTopology}
          onRefreshData={() => loadData(true)}
          isSeeding={isSeeding}
          isRefreshing={isRefreshing}
          hasServers={servers.length > 0}
        />

        {/* Dynamic Toast Banner */}
        {toastMessage && (
          <div
            style={{
              position: 'fixed',
              bottom: '24px',
              right: '24px',
              zIndex: 100,
              padding: '12px 20px',
              borderRadius: '8px',
              backgroundColor: toastMessage.type === 'error' ? '#ef4444' : '#0f172a',
              color: '#ffffff',
              fontSize: '0.875rem',
              fontWeight: 500,
              boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.25)',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              animation: 'fadeIn 0.2s ease',
            }}
          >
            <span>{toastMessage.message}</span>
            <button
              onClick={() => setToastMessage(null)}
              style={{ color: '#94a3b8', fontSize: '1rem', lineHeight: 1 }}
            >
              ✕
            </button>
          </div>
        )}

        {/* Active Page View */}
        <main style={{ flex: 1, padding: '28px', maxWidth: '1440px', width: '100%', margin: '0 auto' }}>
          {activeTab === 'dashboard' && (
            <DashboardPage
              metrics={metrics}
              servers={servers}
              onNavigate={setActiveTab}
              onSeedTopology={handleSeedTopology}
              isSeeding={isSeeding}
            />
          )}

          {activeTab === 'simulator' && (
            <SimulatorPage
              servers={servers}
              onNavigate={setActiveTab}
              onSeedTopology={handleSeedTopology}
              onSimulationFinished={() => loadData(false)}
            />
          )}

          {activeTab === 'comparison' && (
            <ComparisonPage
              servers={servers}
              onNavigate={setActiveTab}
              onSimulationFinished={() => loadData(false)}
            />
          )}

          {activeTab === 'history' && (
            <HistoryPage
              simulations={simulations}
              onNavigate={setActiveTab}
              onReload={() => loadData(false)}
            />
          )}

          {activeTab === 'about' && <AboutPage />}
        </main>
      </div>
    </div>
  );
}
