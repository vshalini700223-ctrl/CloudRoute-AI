import React from 'react';
import {
  LayoutDashboard,
  Cpu,
  GitCompare,
  History,
  Info,
  Cloud,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
} from 'lucide-react';

export default function Sidebar({
  activeTab,
  onTabChange,
  backendHealthy,
  isCheckingHealth,
  onRefreshHealth,
}) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, badge: null },
    { id: 'simulator', label: 'Workload Simulator', icon: Cpu, badge: 'Ready' },
    { id: 'comparison', label: 'Algorithm Comparison', icon: GitCompare, badge: null },
    { id: 'history', label: 'Simulation History', icon: History, badge: null },
    { id: 'about', label: 'About CloudRoute', icon: Info, badge: null },
  ];

  return (
    <aside
      style={{
        width: '260px',
        backgroundColor: '#0b132b',
        color: '#f8fafc',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        borderRight: '1px solid #1e293b',
        height: '100vh',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        userSelect: 'none',
      }}
    >
      {/* Brand Header */}
      <div>
        <div
          style={{
            padding: '24px 20px',
            borderBottom: '1px solid #1e293b',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
          }}
        >
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              backgroundColor: '#2563eb',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 16px rgba(37, 99, 235, 0.4)',
            }}
          >
            <Cloud size={22} color="#ffffff" />
          </div>
          <div>
            <div style={{ fontSize: '1.05rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#ffffff' }}>
              CloudRoute <span style={{ color: '#60a5fa' }}>AI</span>
            </div>
            <div style={{ fontSize: '0.72rem', color: '#94a3b8', fontWeight: 500 }}>
              Cloud Resource Allocator
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <div style={{ padding: '16px 12px' }}>
          <div
            style={{
              fontSize: '0.6875rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              color: '#64748b',
              padding: '0 12px 10px',
            }}
          >
            Core Navigation
          </div>

          <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onTabChange(item.id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    backgroundColor: isActive ? 'rgba(37, 99, 235, 0.18)' : 'transparent',
                    color: isActive ? '#60a5fa' : '#cbd5e1',
                    fontWeight: isActive ? 600 : 500,
                    fontSize: '0.875rem',
                    border: isActive ? '1px solid rgba(59, 130, 246, 0.35)' : '1px solid transparent',
                    transition: 'all 0.15s ease',
                    textAlign: 'left',
                    width: '100%',
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
                      e.currentTarget.style.color = '#ffffff';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = 'transparent';
                      e.currentTarget.style.color = '#cbd5e1';
                    }
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Icon size={18} color={isActive ? '#60a5fa' : '#94a3b8'} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span
                      style={{
                        fontSize: '0.65rem',
                        padding: '1px 6px',
                        borderRadius: '4px',
                        backgroundColor: '#1e293b',
                        color: '#38bdf8',
                        fontWeight: 600,
                      }}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Footer: Live Backend Status */}
      <div
        style={{
          padding: '16px',
          borderTop: '1px solid #1e293b',
          backgroundColor: '#070d1e',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '8px',
          }}
        >
          <span style={{ fontSize: '0.72rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
            Backend API
          </span>
          <button
            onClick={onRefreshHealth}
            title="Refresh backend status"
            disabled={isCheckingHealth}
            style={{
              color: '#94a3b8',
              padding: '4px',
              borderRadius: '4px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <RefreshCw
              size={13}
              style={{
                animation: isCheckingHealth ? 'spin 1s linear infinite' : 'none',
              }}
            />
          </button>
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '0.78rem',
            padding: '6px 10px',
            borderRadius: '6px',
            backgroundColor: backendHealthy ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
            border: backendHealthy ? '1px solid rgba(16, 185, 129, 0.25)' : '1px solid rgba(239, 68, 68, 0.25)',
          }}
        >
          {backendHealthy ? (
            <>
              <CheckCircle2 size={14} color="#10b981" />
              <span style={{ color: '#10b981', fontWeight: 600 }}>FastAPI Operational</span>
            </>
          ) : (
            <>
              <AlertCircle size={14} color="#f87171" />
              <span style={{ color: '#f87171', fontWeight: 600 }}>Backend Connecting...</span>
            </>
          )}
        </div>

        <div style={{ marginTop: '10px', fontSize: '0.68rem', color: '#64748b', textAlign: 'center' }}>
          Virtual Cloud Simulation Engine
        </div>
      </div>
    </aside>
  );
}
