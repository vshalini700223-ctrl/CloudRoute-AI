import React from 'react';

/**
 * Reusable StatCard component for Cloud Dashboard.
 * Displays metric values or clear honest empty state indicators.
 */
export default function StatCard({
  title,
  value,
  subtext,
  icon: Icon,
  variant = 'blue',
  badgeText,
  isEmpty = false,
  emptyMessage = 'No data yet',
}) {
  const variantStyles = {
    blue: {
      border: 'border-blue-500/20',
      iconBg: '#eff6ff',
      iconColor: '#2563eb',
    },
    navy: {
      border: 'border-slate-300',
      iconBg: '#0f172a',
      iconColor: '#ffffff',
    },
    emerald: {
      border: 'border-emerald-500/20',
      iconBg: '#ecfdf5',
      iconColor: '#10b981',
    },
    amber: {
      border: 'border-amber-500/20',
      iconBg: '#fffbeb',
      iconColor: '#f59e0b',
    },
    purple: {
      border: 'border-purple-500/20',
      iconBg: '#f5f3ff',
      iconColor: '#8b5cf6',
    },
  };

  const style = variantStyles[variant] || variantStyles.blue;

  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        borderRadius: '12px',
        padding: '20px',
        border: '1px solid #e2e8f0',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        position: 'relative',
        transition: 'transform 0.15s ease, box-shadow 0.15s ease',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = '0 6px 12px -2px rgba(15, 23, 42, 0.08)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.05)';
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div>
          <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            {title}
          </span>
          {badgeText && (
            <span
              style={{
                marginLeft: '8px',
                fontSize: '0.7rem',
                fontWeight: 600,
                padding: '2px 6px',
                borderRadius: '6px',
                backgroundColor: '#eff6ff',
                color: '#2563eb',
              }}
            >
              {badgeText}
            </span>
          )}
        </div>
        {Icon && (
          <div
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: style.iconBg,
              color: style.iconColor,
              flexShrink: 0,
            }}
          >
            <Icon size={20} />
          </div>
        )}
      </div>

      <div>
        {isEmpty ? (
          <div>
            <div style={{ fontSize: '1.25rem', fontWeight: 600, color: '#94a3b8' }}>
              —
            </div>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '2px' }}>
              {emptyMessage}
            </div>
          </div>
        ) : (
          <div>
            <div style={{ fontSize: '1.875rem', fontWeight: 700, color: '#0f172a', lineHeight: 1.1 }}>
              {value}
            </div>
            {subtext && (
              <div style={{ fontSize: '0.8125rem', color: '#64748b', marginTop: '6px' }}>
                {subtext}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
