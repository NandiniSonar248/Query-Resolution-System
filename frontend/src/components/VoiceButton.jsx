import React from 'react';
import useSpeechRecognition from '../hooks/useSpeechRecognition';

export default function VoiceButton({ onTranscript }) {
  const { start, isListening, isSupported, transcript, resetTranscript } = useSpeechRecognition();

  // Watch for transcript updates
  React.useEffect(() => {
    if (transcript) {
      onTranscript(transcript);
    }
  }, [transcript, onTranscript]);

  // Reset when listening stops
  React.useEffect(() => {
    if (!isListening) {
      resetTranscript();
    }
  }, [isListening, resetTranscript]);

  if (!isSupported) return null;

  return (
    <button
      type="button"
      onClick={start}
      disabled={isListening}
      style={{
        background: 'none',
        border: 'none',
        fontSize: '1.5rem',
        cursor: isListening ? 'default' : 'pointer',
        padding: '8px',
        opacity: isListening ? 1 : 0.6,
        transition: 'all 0.2s',
        animation: isListening ? 'pulse 1.5s infinite' : 'none',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative'
      }}
      title="Speak your question"
    >
      🎤
      {/* Inline styles for the pulse animation */}
      <style>
        {`
          @keyframes pulse {
            0% { transform: scale(1); filter: drop-shadow(0 0 0 rgba(239, 68, 68, 0.7)); }
            50% { transform: scale(1.1); filter: drop-shadow(0 0 10px rgba(239, 68, 68, 0.9)); }
            100% { transform: scale(1); filter: drop-shadow(0 0 0 rgba(239, 68, 68, 0)); }
          }
        `}
      </style>
    </button>
  );
}
