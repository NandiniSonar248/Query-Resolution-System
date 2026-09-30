import React from 'react';

/**
 * Metric card for overview numbers.
 */
export function MetricCard({ label, value, unit = '', color = 'var(--color-primary)', icon }) {
  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '8px', padding: 'var(--space-6)' }}>
      <div style={{ fontSize: '1.5rem', marginBottom: 'var(--space-2)' }}>{icon}</div>
      <div style={{ fontSize: '2.5rem', fontWeight: 700, color, lineHeight: 1 }}>{value}{unit}</div>
      <div style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', fontWeight: 500 }}>{label}</div>
    </div>
  );
}

/**
 * Simple bar chart using plain CSS — no external dependencies.
 */
export function BarChart({ data, maxValue, color = 'var(--color-primary)', title }) {
  if (!data || data.length === 0) return null;
  const max = maxValue || Math.max(...data.map(d => d.value), 1);

  return (
    <div style={{ marginBottom: 'var(--space-6)' }}>
      {title && <h3 style={{ marginBottom: 'var(--space-3)', color: 'var(--color-text-primary)', fontSize: '1rem' }}>{title}</h3>}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
        {data.map((item, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <div style={{ width: '60px', fontSize: '0.8rem', color: 'var(--color-text-muted)', textAlign: 'right', flexShrink: 0 }}>
              {item.label}
            </div>
            <div style={{ flex: 1, backgroundColor: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-sm)', height: '24px', overflow: 'hidden' }}>
              <div style={{
                width: `${max > 0 ? (item.value / max) * 100 : 0}%`,
                height: '100%',
                backgroundColor: color,
                borderRadius: 'var(--radius-sm)',
                transition: 'width 0.5s ease',
                minWidth: item.value > 0 ? '4px' : '0',
                boxShadow: item.value > 0 ? `0 0 12px ${color.replace(')', ', 0.3)').replace('hsl', 'hsla')}` : 'none'
              }} />
            </div>
            <div style={{ width: '30px', fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-text-primary)' }}>
              {item.value}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Donut-style query type distribution using colored blocks.
 */
export function QueryTypeChart({ data }) {
  if (!data || data.length === 0) return (
    <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>No query type data yet.</p>
  );

  const colors = {
    factual: 'var(--color-primary)',
    procedural: 'var(--color-accent)',
    comparative: 'var(--color-warning)',
    ambiguous: 'var(--color-danger)',
    unknown: 'var(--color-text-muted)',
  };

  const total = data.reduce((s, d) => s + d.count, 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
      {data.map((item, i) => {
        const pct = total > 0 ? Math.round((item.count / total) * 100) : 0;
        const color = colors[item.type] || colors.unknown;
        return (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: color, flexShrink: 0, boxShadow: `0 0 8px ${color}` }} />
            <div style={{ flex: 1, fontSize: '0.95rem', textTransform: 'capitalize', color: 'var(--color-text-primary)' }}>{item.type}</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>{item.count} ({pct}%)</div>
          </div>
        );
      })}
    </div>
  );
}
