import React from 'react';
import { Server, RefreshCw, Cpu, Check } from 'lucide-react';

export default function Navbar({
  activeTabTitle,
  onSeedTopology,
  onRefreshData,
  isSeeding,
  isRefreshing,
  hasServers,
}) {
  return (
    <header
      style={{
        backgroundColor: '#ffffff',
        borderBottom: '1px solid #e2e8f0',
        padding: '14px 28px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 40,
        boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.03)',
      }}
    >
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.8125rem', color: '#64748b' }}>CloudRoute AI</span>
          <span style={{ color: '#cbd5e1' }}>/</span>
          <span style={{ fontSize: '0.875rem', fontWeight: 700, color: '#0f172a' }}>
            {activeTabTitle}
          </span>
        </div>
        <p style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '2px' }}>
          Simulated Multi-Server Cloud Scheduling & Heuristic Optimization
        </p>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Virtualized Mode Badge */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: '#f1f5f9',
            padding: '6px 12px',
            borderRadius: '8px',
            border: '1px solid #e2e8f0',
            fontSize: '0.75rem',
            color: '#334155',
            fontWeight: 500,
          }}
        >
          <Cpu size={14} color="#2563eb" />
          <span>Local Simulation Sandbox</span>
        </div>

        {/* Seed Topology Button (functional button) */}
        <button
          onClick={onSeedTopology}
          disabled={isSeeding || hasServers}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: hasServers ? '#f8fafc' : '#2563eb',
            color: hasServers ? '#94a3b8' : '#ffffff',
            border: hasServers ? '1px solid #e2e8f0' : 'none',
            padding: '7px 14px',
            borderRadius: '8px',
            fontSize: '0.8125rem',
            fontWeight: 600,
            cursor: hasServers ? 'not-allowed' : 'pointer',
            transition: 'all 0.15s ease',
            boxShadow: hasServers ? 'none' : '0 2px 4px rgba(37, 99, 235, 0.2)',
          }}
          title={hasServers ? 'Default virtual servers already initialized' : 'Create 4 software-simulated virtual servers'}
        >
          {hasServers ? (
            <>
              <Check size={14} color="#10b981" />
              <span>Servers Active</span>
            </>
          ) : (
            <>
              <Server size={14} />
              <span>{isSeeding ? 'Initializing...' : 'Initialize Topology'}</span>
            </>
          )}
        </button>

        {/* Refresh Data Button (functional button) */}
        <button
          onClick={onRefreshData}
          disabled={isRefreshing}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: '#ffffff',
            color: '#334155',
            border: '1px solid #cbd5e1',
            padding: '7px 12px',
            borderRadius: '8px',
            fontSize: '0.8125rem',
            fontWeight: 600,
            transition: 'all 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#f8fafc')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#ffffff')}
          title="Reload metrics and resource states"
        >
          <RefreshCw
            size={14}
            style={{
              animation: isRefreshing ? 'spin 1s linear infinite' : 'none',
            }}
          />
          <span>Refresh</span>
        </button>
      </div>
    </header>
  );
}
