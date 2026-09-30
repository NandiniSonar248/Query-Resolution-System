/**
 * AppLayout — shared sidebar + main content shell used by Chat, History, Dashboard, Upload.
 * Provides consistent navigation, branding, and layout across all authenticated pages.
 */
import { NavLink, useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';

const NAV = [
  { to: '/home',      icon: '🏠', label: 'Home' },
  { to: '/chat',      icon: '💬', label: 'Knowledge Assistant' },
  { to: '/voice-chat',icon: '🎙️', label: 'Voice Agent' },
  { to: '/upload',    icon: '📁', label: 'Knowledge Base' },
  { to: '/history',   icon: '🕘', label: 'History' },
  { to: '/dashboard', icon: '📊', label: 'Query Analytics' },
];

export default function AppLayout({ children }) {
  const navigate = useNavigate();
  const { logout, user } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="app-layout">
      {/* ── Sidebar ─────────────────────────────────── */}
      <aside className="sidebar">
        {/* Brand */}
        <div style={{ marginBottom: 'var(--space-6)' }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 'var(--space-3)',
            padding: 'var(--space-3)',
          }}>
            <div style={{
              width: '38px', height: '38px', borderRadius: 'var(--radius-md)',
              background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent))',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '1.2rem', boxShadow: 'var(--shadow-glow-primary)',
              flexShrink: 0,
            }}>⚡</div>
            <div>
              <div style={{ fontWeight: 700, fontSize: '1rem', letterSpacing: '0.02em' }}>Query Resolution</div>
              <div className="text-xs text-muted">AI System</div>
            </div>
          </div>
        </div>

        {/* Nav Links */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)', flex: 1 }}>
          {NAV.map(({ to, icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              <span style={{ fontSize: '1.1rem' }}>{icon}</span>
              {label}
            </NavLink>
          ))}
        </nav>

        {/* User + Logout */}
        <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: 'var(--space-4)' }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 'var(--space-3)',
            padding: 'var(--space-3)',
            background: 'var(--color-bg-elevated)',
            borderRadius: 'var(--radius-md)',
            marginBottom: 'var(--space-3)'
          }}>
            <div style={{
              width: '32px', height: '32px', borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent))',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '0.85rem', fontWeight: 700, flexShrink: 0, color: 'white'
            }}>
              {user?.name?.[0]?.toUpperCase() || 'U'}
            </div>
            <div style={{ overflow: 'hidden', flex: 1 }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {user?.name || 'User'}
              </div>
              <div className="text-xs text-muted" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {user?.email || ''}
              </div>
            </div>
          </div>
          <button onClick={handleLogout} className="btn btn-ghost w-full" style={{ justifyContent: 'flex-start', gap: 'var(--space-3)' }}>
            <span>🚪</span> Logout
          </button>
        </div>
      </aside>

      {/* ── Main Content ────────────────────────────── */}
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
