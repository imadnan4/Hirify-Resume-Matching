import React from 'react';

export const FeaturesSection: React.FC = () => {
  const features = [
    {
      title: 'RAG Semantic Retrieval',
      spec: 'MiniLM-384 + PostgreSQL pgvector (ADR-0002 & ADR-0003)',
      desc: 'Resumes are chunked into ~350-token windows with 50-token overlap, indexed into pgvector for high-fidelity top-k similarity search across requirements.',
      icon: '⚡'
    },
    {
      title: '100% Verbatim Citations',
      spec: 'Zero Hallucinations (ADR-0005 & ADR-0007)',
      desc: 'Every score facet (Skills 35%, Experience 30%, Impact 20%, Edu 5%, Clarity 10%) references exact candidate quotes. No hallucinated qualifications permitted.',
      icon: '📜'
    },
    {
      title: 'Auditable Knock-Out Guardrails',
      spec: 'Cap ≤40 without silent dropouts (ADR-0005)',
      desc: 'Candidates failing essential criteria (e.g. missing work authorization or below minimum years) receive explicit KO tags and a score cap at ≤40 for transparent human review.',
      icon: '🛡️'
    }
  ];

  return (
    <section style={{ padding: '64px 24px', maxWidth: '1280px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 700, color: 'var(--color-olive-600, #5c624b)', marginBottom: '8px' }}>
          Autonomous Screening Pillars
        </div>
        <h2 style={{
          fontFamily: "'Familjen Grotesk', sans-serif",
          fontSize: '34px',
          fontWeight: 700,
          letterSpacing: '-0.02em',
          color: 'var(--color-olive-950, #1b1d16)',
          margin: 0
        }}>
          Built for recruiters who demand verifiable evidence.
        </h2>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
        {features.map((feat, i) => (
          <div
            key={i}
            style={{
              padding: '28px',
              borderRadius: '16px',
              background: 'var(--color-olive-50, #ffffff)',
              border: '1px solid var(--color-olive-200, #e9ece0)',
              boxShadow: '0 4px 16px rgba(0,0,0,0.03)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}
          >
            <div>
              <div style={{
                width: '44px',
                height: '44px',
                borderRadius: '12px',
                background: 'var(--color-olive-200, #e9ece0)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '20px',
                marginBottom: '16px'
              }}>
                {feat.icon}
              </div>
              <h3 style={{
                fontFamily: "'Familjen Grotesk', sans-serif",
                fontSize: '20px',
                fontWeight: 700,
                color: 'var(--color-olive-950, #1b1d16)',
                margin: '0 0 6px'
              }}>
                {feat.title}
              </h3>
              <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-olive-600, #5c624b)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '12px' }}>
                {feat.spec}
              </div>
              <p style={{ fontSize: '14px', color: 'var(--color-olive-700, #404434)', lineHeight: '1.6', margin: 0 }}>
                {feat.desc}
              </p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
