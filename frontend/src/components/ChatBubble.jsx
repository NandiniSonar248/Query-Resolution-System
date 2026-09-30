import React from 'react';
import ConfidenceBadge from './ConfidenceBadge';
import SourcePanel from './SourcePanel';

export default function ChatBubble({ message }) {
  const isUser = message.role === 'user';
  const isClarification = message.role === 'clarification';

  const alignmentStyle = {
    display: 'flex',
    justifyContent: isUser ? 'flex-end' : 'flex-start',
    marginBottom: 'var(--space-6)',
    width: '100%',
  };

  const bubbleStyle = {
    maxWidth: '85%',
    padding: 'var(--space-4) var(--space-5)',
    borderRadius: 'var(--radius-lg)',
    boxShadow: 'var(--shadow-sm)',
    lineHeight: '1.5',
    position: 'relative',
  };

  if (isUser) {
    Object.assign(bubbleStyle, {
      background: 'linear-gradient(135deg, var(--color-primary), var(--color-primary-dark))',
      color: 'white',
      borderBottomRightRadius: '4px',
      boxShadow: 'var(--shadow-glow-primary)',
    });
  } else if (isClarification) {
    Object.assign(bubbleStyle, {
      background: 'hsla(38, 92%, 55%, 0.1)',
      border: '1px solid hsla(38, 92%, 55%, 0.3)',
      borderLeft: '4px solid var(--color-warning)',
      color: 'var(--color-text-primary)',
      borderBottomLeftRadius: '4px',
    });
  } else {
    // Assistant message
    Object.assign(bubbleStyle, {
      background: 'var(--color-bg-elevated)',
      border: '1px solid var(--color-border)',
      color: 'var(--color-text-primary)',
      borderBottomLeftRadius: '4px',
    });
  }

  return (
    <div style={alignmentStyle} className="animate-fade-in-up">
      <div style={bubbleStyle}>
        
        {/* Author Label */}
        <div style={{ 
          fontSize: '0.75rem', 
          fontWeight: 600, 
          marginBottom: 'var(--space-2)',
          color: isUser ? 'rgba(255,255,255,0.8)' : isClarification ? 'var(--color-warning)' : 'var(--color-primary)',
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-2)'
        }}>
          {isUser ? '👤 You' : '⚡ QueryAI'}
          
          {/* Confidence Badge (only for Assistant answers) */}
          {!isUser && !isClarification && message.confidence_score !== undefined && (
            <div style={{ marginLeft: 'auto' }}>
              <ConfidenceBadge score={message.confidence_score} label={message.confidence_label} />
            </div>
          )}
        </div>

        {/* Message Text */}
        <div style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', fontSize: '0.95rem' }}>
          {message.content}
        </div>

        {/* Source Panel (only for Assistant answers) */}
        {!isUser && !isClarification && message.citations && message.citations.length > 0 && (
          <div style={{ marginTop: 'var(--space-4)', paddingTop: 'var(--space-4)', borderTop: `1px solid ${isUser ? 'rgba(255,255,255,0.2)' : 'var(--color-border-subtle)'}` }}>
            <SourcePanel citations={message.citations} />
          </div>
        )}
      </div>
    </div>
  );
}
