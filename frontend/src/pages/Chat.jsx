import { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { queryApi, historyApi } from '../api';
import AppLayout from '../components/AppLayout';
import ChatBubble from '../components/ChatBubble';
import VoiceButton from '../components/VoiceButton';
import useSpeechSynthesis from '../hooks/useSpeechSynthesis';

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [voiceEnabled, setVoiceEnabled] = useState(true);

  const { speak, isSupported: isTTSSupported, cancel } = useSpeechSynthesis();
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const location = useLocation();

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);
  useEffect(() => { return () => cancel(); }, [cancel]);

  // Load existing session if navigated from History page
  useEffect(() => {
    if (location.state?.sessionId) {
      (async () => {
        try {
          const { data } = await historyApi.session(location.state.sessionId);
          setSessionId(data.id);
          setMessages(data.messages || []);
        } catch (err) { console.error('Failed to load session', err); }
      })();
    }
  }, [location.state]);

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const { data } = await queryApi.ask({ query: text, session_id: sessionId });
      if (!sessionId && data.session_id) setSessionId(data.session_id);

      const aiMsg = {
        role: data.clarification_needed ? 'clarification' : 'assistant',
        content: data.clarification_needed ? data.clarifying_question : data.answer,
        confidence_label: data.confidence_label,
        confidence_score: data.confidence_score,
        citations: data.citations || [],
        clarification_needed: data.clarification_needed,
        clarifying_question: data.clarifying_question,
      };
      setMessages(prev => [...prev, aiMsg]);

      // Only Voice Agent should auto-speak now.
      // if (voiceEnabled && isTTSSupported) {
      //   speak(aiMsg.content);
      // }
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: '❌ Error — could not get a response. Please try again.' }]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setSessionId(null);
    cancel();
    inputRef.current?.focus();
  };

  return (
    <AppLayout>
      <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>

        {/* ── Top bar ─────────────────────────────── */}
        <header style={{
          padding: 'var(--space-4) var(--space-6)',
          borderBottom: '1px solid var(--color-border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'var(--color-bg-surface)',
          flexShrink: 0,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <div>
              <h2 style={{ fontSize: '1rem', margin: 0 }}>
                {sessionId ? `Session #${sessionId}` : 'New Conversation'}
              </h2>
              <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', margin: 0 }}>
                {messages.length === 0 ? 'Start asking questions' : `${messages.length} messages`}
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center' }}>
            {isTTSSupported && (
              <button
                className="btn btn-ghost btn-icon"
                onClick={() => { setVoiceEnabled(v => !v); cancel(); }}
                title={voiceEnabled ? 'Mute voice' : 'Enable voice'}
                style={{ fontSize: '1.1rem' }}
              >
                {voiceEnabled ? '🔊' : '🔇'}
              </button>
            )}
            <button className="btn btn-secondary btn-sm" onClick={startNewChat}>
              + New Chat
            </button>
          </div>
        </header>

        {/* ── Messages ────────────────────────────── */}
        <div style={{ flex: 1, overflowY: 'auto', padding: 'var(--space-6)' }}>
          {messages.length === 0 ? (
            <div style={{
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
              height: '100%', gap: 'var(--space-4)', textAlign: 'center',
            }}>
              <div style={{ fontSize: '4rem' }}>🧠</div>
              <h3 style={{ color: 'var(--color-text-secondary)' }}>Ask anything about your documents</h3>
              <p className="text-muted text-sm">Upload PDFs, manuals, or handbooks and start querying them instantly</p>
              <div style={{
                display: 'flex', gap: 'var(--space-3)', marginTop: 'var(--space-4)',
                flexWrap: 'wrap', justifyContent: 'center',
              }}>
                {['What is the dress code?', 'Explain the leave policy', 'What are the working hours?'].map(q => (
                  <button
                    key={q}
                    className="btn btn-secondary btn-sm"
                    onClick={() => { setInput(q); inputRef.current?.focus(); }}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div style={{ maxWidth: '800px', margin: '0 auto' }}>
              {messages.map((msg, i) => <ChatBubble key={i} message={msg} />)}
              {loading && (
                <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: 'var(--space-4)' }}>
                  <div className="card" style={{
                    padding: 'var(--space-4) var(--space-5)',
                    display: 'flex', alignItems: 'center', gap: 'var(--space-3)',
                    maxWidth: '200px',
                  }}>
                    <span className="spinner" />
                    <span className="text-sm text-muted">Thinking…</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* ── Input bar ───────────────────────────── */}
        <div style={{
          padding: 'var(--space-4) var(--space-6)',
          borderTop: '1px solid var(--color-border)',
          background: 'var(--color-bg-surface)',
          flexShrink: 0,
        }}>
          <form onSubmit={handleSubmit} style={{
            display: 'flex', gap: 'var(--space-3)', maxWidth: '800px', margin: '0 auto',
          }}>
            <VoiceButton onTranscript={t => setInput(t)} />
            <input
              ref={inputRef}
              type="text"
              className="input"
              placeholder="Ask a question about your documents…"
              value={input}
              onChange={e => setInput(e.target.value)}
              disabled={loading}
              style={{ flex: 1 }}
            />
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !input.trim()}
            >
              {loading ? <><span className="spinner" style={{ width: 16, height: 16 }} /> Sending</> : 'Send →'}
            </button>
          </form>
        </div>
      </div>
    </AppLayout>
  );
}
