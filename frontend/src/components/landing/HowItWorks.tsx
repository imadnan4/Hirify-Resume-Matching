import React from 'react';

export const HowItWorks: React.FC = () => {
  const steps = [
    {
      step: '01',
      title: 'Requisition & Criteria Intake',
      desc: 'Define role requirements split into REQ-1..5 facets. Set essential thresholds and hard knockout policies (e.g. work visa requirements).'
    },
    {
      step: '02',
      title: 'Document Ingest & MiniLM Chunking',
      desc: 'Upload PDF and TXT resumes. The parser chunks documents into ~350-token windows with 50-token overlap, embedded into 384-dimensional pgvectors.'
    },
    {
      step: '03',
      title: 'Autonomous Qwen Screening Loop',
      desc: 'The agent retrieves top-k chunks per requirement, calls tool functions to extract verbatim quotations, verifies citations, and assigns scores.'
    },
    {
      step: '04',
      title: 'Evidence Dossier & DB Interview Stub',
      desc: 'Inspect the auditable breakdown for every applicant. Trigger an interview stub in the database for qualifying candidates with zero email noise.'
    }
  ];

  return (
    <section style={{
      padding: '64px 24px',
      maxWidth: '1280px',
      margin: '0 auto',
      background: 'var(--color-olive-100, #fafbf8)',
      borderRadius: '24px',
      border: '1px solid var(--color-olive-200, #e9ece0)',
      marginBottom: '64px'
    }}>
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 700, color: 'var(--color-olive-600, #5c624b)', marginBottom: '8px' }}>
          Autonomous Execution
        </div>
        <h2 style={{
          fontFamily: "'Familjen Grotesk', sans-serif",
          fontSize: '34px',
          fontWeight: 700,
          letterSpacing: '-0.02em',
          color: 'var(--color-olive-950, #1b1d16)',
          margin: 0
        }}>
          How the screening agent processes candidate dossiers
        </h2>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
        {steps.map((s, i) => (
          <div
            key={i}
            style={{
              padding: '24px',
              borderRadius: '14px',
              background: 'var(--color-olive-50, #ffffff)',
              border: '1px solid var(--color-olive-200, #e9ece0)'
            }}
          >
            <div style={{
              fontFamily: "'Familjen Grotesk', sans-serif",
              fontSize: '28px',
              fontWeight: 700,
              color: 'var(--color-olive-400, #8f9779)',
              marginBottom: '10px'
            }}>
              {s.step}
            </div>
            <h3 style={{
              fontFamily: "'Familjen Grotesk', sans-serif",
              fontSize: '17px',
              fontWeight: 700,
              color: 'var(--color-olive-950, #1b1d16)',
              margin: '0 0 8px'
            }}>
              {s.title}
            </h3>
            <p style={{ fontSize: '13.5px', color: 'var(--color-olive-700, #404434)', lineHeight: '1.5', margin: 0 }}>
              {s.desc}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
};
