import React from 'react';

const StatCard = ({ label, value, icon: Icon, loading }) => {
  const formatNumber = (num) => {
    if (loading || num === null || num === undefined) return '---';
    return new Intl.NumberFormat('en-IN').format(num);
  };

  return (
    <div style={{
      background: '#fff',
      border: '1px solid var(--border)',
      borderRadius: '8px',
      padding: '20px',
      display: 'flex',
      alignItems: 'center',
      gap: '16px',
      transition: 'all 0.3s',
      cursor: 'default',
      flex: 1,
      minWidth: '200px'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.borderColor = 'var(--primary)';
      e.currentTarget.style.boxShadow = '0 4px 12px rgba(40, 116, 240, 0.1)';
      e.currentTarget.style.transform = 'translateY(-2px)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.borderColor = 'var(--border)';
      e.currentTarget.style.boxShadow = 'none';
      e.currentTarget.style.transform = 'translateY(0)';
    }}
    >
      <div style={{
        width: '48px',
        height: '48px',
        borderRadius: '8px',
        background: 'rgba(40, 116, 240, 0.08)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0
      }}>
        {loading ? (
          <div style={{
            width: '24px',
            height: '24px',
            border: '2px solid rgba(40, 116, 240, 0.2)',
            borderTop: '2px solid var(--primary)',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
        ) : (
          <Icon size={24} color="var(--primary)" strokeWidth={1.5} />
        )}
      </div>
      
      <div style={{ flex: 1, minWidth: 0 }}>
        <p style={{
          fontSize: '11px',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
          color: 'var(--text-gray)',
          margin: '0 0 4px 0'
        }}>
          {label}
        </p>
        <p style={{
          fontSize: '28px',
          fontWeight: 700,
          color: 'var(--text-dark)',
          margin: 0,
          lineHeight: 1
        }}>
          {formatNumber(value)}
        </p>
      </div>
    </div>
  );
};

export default StatCard;
