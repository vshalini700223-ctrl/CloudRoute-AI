import React from 'react';
import { Layers } from 'lucide-react';

/**
 * Reusable EmptyState component.
 * Adheres to rule: "Initially show a clear empty state when there are no simulation results. Never invent performance metrics."
 */
export default function EmptyState({
  title = 'No Simulation Runs Yet',
  description = 'No workload allocation simulations have been executed. Run a simulation to evaluate algorithm makespan and virtual server utilization.',
  icon: Icon = Layers,
  actionText,
  onAction,
}) {
  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        border: '1px dashed #cbd5e1',
        borderRadius: '14px',
        padding: '48px 24px',
        textAlign: 'center',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        margin: '16px 0',
      }}
    >
      <div
        style={{
          width: '56px',
          height: '56px',
          borderRadius: '14px',
          backgroundColor: '#eff6ff',
          color: '#2563eb',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '16px',
        }}
      >
        <Icon size={28} />
      </div>

      <h3 style={{ fontSize: '1.125rem', fontWeight: 700, color: '#0f172a', marginBottom: '8px' }}>
        {title}
      </h3>

      <p style={{ fontSize: '0.875rem', color: '#64748b', maxWidth: '480px', lineHeight: 1.6, marginBottom: actionText ? '20px' : '0' }}>
        {description}
      </p>

      {actionText && onAction && (
        <button
          onClick={onAction}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: '#2563eb',
            color: '#ffffff',
            padding: '10px 18px',
            borderRadius: '8px',
            fontSize: '0.875rem',
            fontWeight: 600,
            boxShadow: '0 2px 4px rgba(37, 99, 235, 0.2)',
            transition: 'background-color 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#1d4ed8')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#2563eb')}
        >
          {actionText}
        </button>
      )}
    </div>
  );
}
