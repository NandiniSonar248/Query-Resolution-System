import { Link } from 'react-router-dom';
import AppLayout from '../components/AppLayout';
import useAuthStore from '../store/authStore';

export default function Home() {
  const { user } = useAuthStore();

  const features = [
    {
      title: "Knowledge Base",
      description: "Upload and index your enterprise documents (PDF, DOCX, CSV) securely.",
      icon: "📁",
      link: "/upload",
      color: "var(--color-primary)"
    },
    {
      title: "Knowledge Assistant",
      description: "Interact with your data via text. High-speed RAG-powered responses.",
      icon: "💬",
      link: "/chat",
      color: "var(--color-accent)"
    },
    {
      title: "Voice Agent",
      description: "Hands-free interaction. Speak naturally and get voice responses.",
      icon: "🎙️",
      link: "/voice-chat",
      color: "var(--color-warning)"
    },
    {
      title: "Query Analytics",
      description: "Track system confidence, discover knowledge gaps, and optimize data.",
      icon: "📊",
      link: "/dashboard",
      color: "var(--color-success)"
    }
  ];

  return (
    <AppLayout>
      <div className="page-content animate-fade-in" style={{ maxWidth: '1200px', margin: '0 auto', width: '100%', padding: 'var(--space-8)' }}>
        
        {/* Hero Section */}
        <div style={{ textAlign: 'center', marginBottom: 'var(--space-12)' }}>
          <div style={{ 
            display: 'inline-block', 
            padding: 'var(--space-2) var(--space-4)', 
            background: 'hsla(220, 80%, 50%, 0.1)', 
            color: 'var(--color-primary)', 
            borderRadius: '999px',
            fontSize: '0.875rem',
            fontWeight: 600,
            marginBottom: 'var(--space-4)'
          }}>
            🚀 Welcome to the Future of Query Resolution
          </div>
          <h1 style={{ fontSize: '3rem', fontWeight: 800, marginBottom: 'var(--space-4)', letterSpacing: '-0.02em' }}>
            Hello, {user?.name || 'User'}!
          </h1>
          <p style={{ fontSize: '1.25rem', color: 'var(--color-text-muted)', maxWidth: '600px', margin: '0 auto', lineHeight: 1.6 }}>
            Empower your workflow with AI. Upload your documents, ask questions, and let the intelligent assistant resolve your queries instantly.
          </p>
        </div>

        {/* Features Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-6)' }}>
          {features.map((f, i) => (
            <Link to={f.link} key={i} style={{ textDecoration: 'none', color: 'inherit' }}>
              <div className="card" style={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column', 
                transition: 'transform 0.2s, box-shadow 0.2s',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = 'var(--shadow-lg)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
              }}
              >
                <div style={{ 
                  width: '50px', height: '50px', 
                  borderRadius: '12px', 
                  backgroundColor: `${f.color}15`, // adding transparency
                  color: f.color,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '1.5rem',
                  marginBottom: 'var(--space-4)'
                }}>
                  {f.icon}
                </div>
                <h3 style={{ fontSize: '1.25rem', marginBottom: 'var(--space-2)' }}>{f.title}</h3>
                <p style={{ color: 'var(--color-text-muted)', lineHeight: 1.5, flex: 1 }}>{f.description}</p>
                <div style={{ marginTop: 'var(--space-4)', color: f.color, fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                  Explore <span style={{ fontSize: '1.2rem' }}>→</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
        
      </div>
    </AppLayout>
  );
}
