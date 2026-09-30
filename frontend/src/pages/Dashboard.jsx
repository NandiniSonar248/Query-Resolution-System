import { useState, useEffect } from 'react';
import { analyticsApi } from '../api';
import AppLayout from '../components/AppLayout';
import { MetricCard, BarChart, QueryTypeChart } from '../components/AnalyticsCharts';

import toast from 'react-hot-toast';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async (showLoading = true) => {
    try {
      if (showLoading && !data) setLoading(true);
      const { data: res } = await analyticsApi.dashboard();
      setData(res);
      setError(null);
    } catch (err) {
      setError('Failed to load analytics.');
      console.error(err);
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  const handleReset = async () => {
    if (!window.confirm("Are you sure you want to clear all analytics data? This cannot be undone.")) return;
    try {
      await analyticsApi.reset();
      toast.success("Analytics data reset successfully.");
      fetchData(true);
    } catch (err) {
      console.error(err);
      toast.error("Failed to reset analytics.");
    }
  };

  useEffect(() => {
    fetchData();
    const intervalId = setInterval(() => fetchData(false), 10000);
    return () => clearInterval(intervalId);
  }, []);

  return (
    <AppLayout>
      <div style={{ padding: 'var(--space-8) var(--space-6)', maxWidth: '1200px', margin: '0 auto', width: '100%', overflowY: 'auto', height: '100%' }}>
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-8)' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '2rem' }}>Query Analytics</h1>
            <p style={{ marginTop: 'var(--space-2)', color: 'var(--color-text-muted)' }}>Query statistics and knowledge gap detection</p>
          </div>
          <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
            <button onClick={handleReset} className="btn btn-ghost" style={{ color: 'var(--color-danger)' }}>
              🗑️ Reset Data
            </button>
            <button onClick={() => fetchData(true)} className="btn btn-secondary">
              🔄 Refresh Data
            </button>
          </div>
        </header>

        {loading && !data && (
          <div style={{ textAlign: 'center', marginTop: 'var(--space-12)' }}>
            <span className="spinner" style={{ width: 40, height: 40, margin: '0 auto' }} />
          </div>
        )}

        {error && <div className="error-msg mb-6">{error}</div>}

        {data && (
          <div className="animate-fade-in-up">
            {/* Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 'var(--space-4)', marginBottom: 'var(--space-8)' }}>
              <MetricCard icon="💬" label="Total Queries" value={data.overview.total_queries} color="var(--color-primary)" />
              <MetricCard 
                icon="🎯" 
                label="Avg Confidence" 
                value={data.overview.avg_confidence_pct} 
                unit="%" 
                color={data.overview.avg_confidence_pct > 70 ? 'var(--color-success)' : data.overview.avg_confidence_pct > 50 ? 'var(--color-warning)' : 'var(--color-danger)'} 
              />
              <MetricCard icon="🔍" label="Knowledge Gaps" value={data.overview.total_knowledge_gaps} color="var(--color-warning)" />
              <MetricCard icon="❌" label="Unanswered Queries" value={data.overview.unanswered_queries} color="var(--color-danger)" />
            </div>

            {/* Charts Row */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-6)', marginBottom: 'var(--space-8)' }}>
              <div className="card">
                <h3 style={{ marginBottom: 'var(--space-4)', color: 'var(--color-text-primary)' }}>📈 Query Volume (Last 7 Days)</h3>
                <BarChart data={data.daily_volume.map(d => ({ label: d.date.slice(5), value: d.count }))} color="var(--color-primary)" />
              </div>
              <div className="card">
                <h3 style={{ marginBottom: 'var(--space-4)', color: 'var(--color-text-primary)' }}>🗂️ Query Types</h3>
                <QueryTypeChart data={data.query_type_distribution} />
              </div>
            </div>

            {/* Knowledge Gap Table */}
            <div className="card">
              <h3 style={{ marginBottom: 'var(--space-2)', color: 'var(--color-text-primary)' }}>🔍 Knowledge Gap Log</h3>
              <p className="text-muted text-sm mb-6">Queries where the system had low confidence or couldn't find an answer.</p>
              
              {data.knowledge_gaps.length === 0 ? (
                <div style={{ padding: 'var(--space-6)', textAlign: 'center', background: 'hsla(142, 71%, 45%, 0.1)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '2rem', marginBottom: 'var(--space-2)' }}>✅</div>
                  <div style={{ color: 'var(--color-success)', fontWeight: 600 }}>No knowledge gaps detected!</div>
                  <div className="text-sm" style={{ color: 'hsla(142, 71%, 45%, 0.8)' }}>The system is answering all queries with high confidence.</div>
                </div>
              ) : (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                    <thead>
                      <tr>
                        <th style={{ textAlign: 'left', padding: '12px 16px', borderBottom: '1px solid var(--color-border)', color: 'var(--color-text-secondary)', fontWeight: 600 }}>Query</th>
                        <th style={{ textAlign: 'left', padding: '12px 16px', borderBottom: '1px solid var(--color-border)', color: 'var(--color-text-secondary)', fontWeight: 600 }}>Type</th>
                        <th style={{ textAlign: 'center', padding: '12px 16px', borderBottom: '1px solid var(--color-border)', color: 'var(--color-text-secondary)', fontWeight: 600 }}>Confidence</th>
                        <th style={{ textAlign: 'center', padding: '12px 16px', borderBottom: '1px solid var(--color-border)', color: 'var(--color-text-secondary)', fontWeight: 600 }}>Answered?</th>
                        <th style={{ textAlign: 'left', padding: '12px 16px', borderBottom: '1px solid var(--color-border)', color: 'var(--color-text-secondary)', fontWeight: 600 }}>Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.knowledge_gaps.map((gap, i) => (
                        <tr key={gap.id} style={{ backgroundColor: i % 2 === 0 ? 'transparent' : 'var(--color-bg-elevated)' }}>
                          <td style={{ padding: '12px 16px', borderBottom: '1px solid var(--color-border)', color: 'var(--color-text-primary)' }}>{gap.query_text}</td>
                          <td style={{ padding: '12px 16px', borderBottom: '1px solid var(--color-border)', textTransform: 'capitalize', color: 'var(--color-text-secondary)' }}>{gap.query_type || '—'}</td>
                          <td style={{ padding: '12px 16px', borderBottom: '1px solid var(--color-border)', textAlign: 'center' }}>
                            {gap.confidence_score !== null ? (
                              <span className={`badge ${gap.confidence_score >= 60 ? 'badge-high' : gap.confidence_score >= 40 ? 'badge-medium' : 'badge-low'}`}>
                                {gap.confidence_score}%
                              </span>
                            ) : '—'}
                          </td>
                          <td style={{ padding: '12px 16px', borderBottom: '1px solid var(--color-border)', textAlign: 'center' }}>{gap.was_answered ? '✅' : '❌'}</td>
                          <td style={{ padding: '12px 16px', borderBottom: '1px solid var(--color-border)', color: 'var(--color-text-muted)', fontSize: '0.8rem' }}>
                            {gap.created_at ? new Date(gap.created_at).toLocaleString() : '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
