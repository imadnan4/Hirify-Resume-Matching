import React from 'react';

export const MetricsSection: React.FC = () => {
  const metrics = [
    { label: 'NDCG@5 Ranking Benchmark', value: '0.884', sub: 'Target: ≥0.75 • Exceeded by +0.134', color: '#15803d' },
    { label: 'Citation Faithfulness', value: '100%', sub: 'Zero uncited or hallucinated statements', color: '#15803d' },
    { label: 'Spearman Rank Correlation', value: '0.841', sub: 'High agreement with human recruiter ground truth', color: 'var(--color-olive-950, #1b1d16)' },
    { label: 'Knock-Out Enforcement', value: '≤40', sub: 'Strict cap applied without silent dropouts', color: '#b91c1c' }
  ];

  return (
    <section style={{ padding: '48px 24px', maxWidth: '1280px', margin: '0 auto' }}>
      <div style={{
        padding: '40px 32px',
        borderRadius: '20px',
        background: 'var(--color-olive-950, #1b1d16)',
        color: '#ffffff',
        boxShadow: '0 12px 36px rgba(27,29,22,0.2)'
      }}>
        <div style={{ textAlign: 'center', maxWidth: '640px', margin: '0 auto 36px' }}>
          <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 700, color: 'var(--color-olive-400, #8f9779)', marginBottom: '6px' }}>
            Auditable Quality Harness
          </div>
          <h2 style={{
            fontFamily: "'Familjen Grotesk', sans-serif",
            fontSize: '32px',
            fontWeight: 700,
            margin: 0
          }}>
            Held-out benchmark verification results
          </h2>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px' }}>
          {metrics.map((m, i) => (
            <div
              key={i}
              style={{
                padding: '24px',
                borderRadius: '12px',
                background: 'rgba(255,255,255,0.06)',
                border: '1px solid rgba(255,255,255,0.1)'
              }}
            >
              <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.7)', marginBottom: '8px' }}>
                {m.label}
              </div>
              <div style={{
                fontFamily: "'Familjen Grotesk', sans-serif",
                fontSize: '36px',
                fontWeight: 700,
                color: m.color === '#15803d' ? '#4ade80' : m.color === '#b91c1c' ? '#f87171' : '#ffffff',
                lineHeight: '1',
                marginBottom: '8px'
              }}>
                {m.value}
              </div>
              <div style={{ fontSize: '11.5px', color: 'rgba(255,255,255,0.6)' }}>
                {m.sub}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
