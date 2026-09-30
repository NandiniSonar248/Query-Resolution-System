import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { historyApi } from '../api';
import AppLayout from '../components/AppLayout';

export default function History() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const { data } = await historyApi.sessions();
        setSessions(data);
      } catch {
        toast.error('Failed to load history');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    try {
      await historyApi.deleteSession(id);
      setSessions(prev => prev.filter(s => s.id !== id));
      toast.success('Session deleted');
    } catch {
      toast.error('Failed to delete session');
    }
  };

  const openSession = (id) => {
    navigate('/chat', { state: { sessionId: id } });
  };

  return (
    <AppLayout>
      <div style={{ padding: 'var(--space-8) var(--space-6)', maxWidth: '1000px', margin: '0 auto', width: '100%' }}>
        <header style={{ marginBottom: 'var(--space-8)' }}>
          <h1 style={{ margin: 0, fontSize: '2rem' }}>Conversation History</h1>
          <p style={{ marginTop: 'var(--space-2)', color: 'var(--color-text-muted)' }}>
            Review past conversations and reload them into the chat.
          </p>
        </header>

        {loading ? (
          <div style={{ textAlign: 'center', marginTop: 'var(--space-12)' }}>
            <span className="spinner" style={{ width: 40, height: 40, margin: '0 auto' }} />
          </div>
        ) : sessions.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: 'var(--space-12)' }}>
            <div style={{ fontSize: '3rem', marginBottom: 'var(--space-4)' }}>📭</div>
            <h3 style={{ marginBottom: 'var(--space-2)' }}>No conversations yet</h3>
            <p className="text-muted" style={{ marginBottom: 'var(--space-6)' }}>
              Start asking questions in the chat to build up your history.
            </p>
            <button className="btn btn-primary" onClick={() => navigate('/chat')}>
              Go to Chat →
            </button>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            {sessions.map(s => (
              <div 
                key={s.id} 
                className="card"
                onClick={() => openSession(s.id)}
                style={{
                  padding: 'var(--space-4) var(--space-5)',
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  cursor: 'pointer', transition: 'all 0.2s',
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.borderColor = 'var(--color-primary)';
                  e.currentTarget.style.transform = 'translateY(-1px)';
                  e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.borderColor = 'var(--color-border)';
                  e.currentTarget.style.transform = 'none';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, fontSize: '1.05rem', color: 'var(--color-text-primary)' }}>
                    {s.title || 'Untitled Conversation'}
                  </div>
                  <div className="text-sm text-muted" style={{ marginTop: 'var(--space-1)' }}>
                    {new Date(s.created_at).toLocaleString()} • {s.messages?.length || 0} messages
                  </div>
                </div>
                
                <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
                  <button 
                    className="btn btn-secondary btn-sm"
                    onClick={(e) => { e.stopPropagation(); openSession(s.id); }}
                  >
                    Open
                  </button>
                  <button 
                    className="btn btn-ghost btn-icon"
                    onClick={(e) => handleDelete(s.id, e)}
                    title="Delete session"
                    style={{ color: 'var(--color-danger)' }}
                  >
                    🗑
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
