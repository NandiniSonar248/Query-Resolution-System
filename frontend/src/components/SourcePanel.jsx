import React, { useState } from 'react';

export default function SourcePanel({ citations }) {
  const [expanded, setExpanded] = useState(false);

  if (!citations || citations.length === 0) return null;

  // Deduplicate sources by document name for the collapsed view
  const uniqueDocs = [...new Set(citations.map(c => c.source_doc))];

  return (
    <div style={{ marginTop: 'var(--space-2)' }}>
      <button 
        onClick={() => setExpanded(!expanded)}
        className="btn btn-ghost btn-sm"
        style={{ 
          fontSize: '0.8rem', 
          color: 'var(--color-text-secondary)',
          padding: '4px 8px',
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-1)'
        }}
      >
        <span>{expanded ? '▼' : '▶'}</span> 
        {uniqueDocs.length} Source{uniqueDocs.length > 1 ? 's' : ''} ({citations.length} excerpts)
      </button>

      {expanded && (
        <div style={{ 
          marginTop: 'var(--space-3)', 
          display: 'flex', 
          flexDirection: 'column', 
          gap: 'var(--space-2)',
          background: 'var(--color-bg-base)',
          padding: 'var(--space-3)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--color-border-subtle)'
        }}>
          {citations.map((c, i) => (
            <div key={i} style={{ 
              fontSize: '0.8rem', 
              padding: 'var(--space-2)', 
              background: 'var(--color-bg-surface)', 
              borderRadius: 'var(--radius-sm)',
              borderLeft: '2px solid var(--color-primary)'
            }}>
              <div style={{ fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '2px' }}>
                📄 {c.source_doc}
              </div>
              <div style={{ color: 'var(--color-text-muted)', fontFamily: 'monospace', fontSize: '0.75rem' }}>
                Chunk ID: {c.chunk_id}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
