import React from 'react';

export type EvidenceStatus = 'observed' | 'derived' | 'metadata only' | 'blocked' | 'stale' | 'missing' | string;

interface StatusBadgeProps {
  status: EvidenceStatus;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const norm = (status || '').toLowerCase().trim();

  let bg = 'var(--status-stale-bg)';
  let color = 'var(--status-stale-text)';
  let border = 'var(--status-stale-border)';
  let icon = '•';

  switch (norm) {
    case 'observed':
      bg = 'var(--status-observed-bg)';
      color = 'var(--status-observed-text)';
      border = 'var(--status-observed-border)';
      icon = '✓';
      break;
    case 'derived':
      bg = 'var(--status-derived-bg)';
      color = 'var(--status-derived-text)';
      border = 'var(--status-derived-border)';
      icon = '⚙';
      break;
    case 'metadata only':
      bg = 'var(--status-metadata-bg)';
      color = 'var(--status-metadata-text)';
      border = 'var(--status-metadata-border)';
      icon = 'ℹ';
      break;
    case 'blocked':
      bg = 'var(--status-blocked-bg)';
      color = 'var(--status-blocked-text)';
      border = 'var(--status-blocked-border)';
      icon = '⊘';
      break;
    case 'missing':
      bg = 'var(--status-missing-bg)';
      color = 'var(--status-missing-text)';
      border = 'var(--status-missing-border)';
      icon = '✕';
      break;
    case 'stale':
      bg = 'var(--status-stale-bg)';
      color = 'var(--status-stale-text)';
      border = 'var(--status-stale-border)';
      icon = '⏱';
      break;
  }

  const padding = size === 'sm' ? '0.15rem 0.5rem' : '0.25rem 0.65rem';
  const fontSize = size === 'sm' ? '0.7rem' : '0.75rem';

  return (
    <span
      role="status"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.35rem',
        padding,
        fontSize,
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.04em',
        borderRadius: 'var(--radius-full)',
        backgroundColor: bg,
        color: color,
        border: `1px solid ${border}`,
        whiteSpace: 'nowrap',
      }}
      aria-label={`Evidence status: ${status}`}
    >
      <span aria-hidden="true">{icon}</span>
      <span>{status}</span>
    </span>
  );
};
