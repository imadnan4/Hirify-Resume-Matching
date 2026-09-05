import React from 'react';

interface CallToActionProps {
  onNavigate?: (page: string) => void;
}

export const CallToAction: React.FC<CallToActionProps> = ({ onNavigate }) => {
  return (
    <section style={{ padding: '64px 24px', maxWidth: '1280px', margin: '0 auto' }}>
      <div style={{
        padding: '56px 32px',
        borderRadius: '24px',
        background: 'var(--color-olive-200, #e9ece0)',
        border: '1px solid var(--color-olive-300, #d5dac9)',
        textAlign: 'center'
      }}>
        <h2 style={{
          fontFamily: "'Familjen Grotesk', sans-serif",
          fontSize: '36px',
          fontWeight: 700,
          color: 'var(--color-olive-950, #1b1d16)',
          margin: '0 0 14px'
        }}>
          Ready to experience verifiable candidate screening?
        </h2>
        <p style={{
          fontSize: '16px',
          color: 'var(--color-olive-800, #343729)',
          maxWidth: '620px',
          margin: '0 auto 28px',
          lineHeight: '1.5'
        }}>
          Upload your job requirements, batch ingest resumes, and inspect the grounded evidence dossier with zero hallucinations.
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '14px', flexWrap: 'wrap' }}>
          <button
            type="button"
            onClick={() => onNavigate && onNavigate('upload')}
            style={{
              padding: '12px 28px',
              borderRadius: '9999px',
              background: 'var(--color-olive-950, #1b1d16)',
              color: '#fff',
              fontSize: '14px',
              fontWeight: 700,
              cursor: 'pointer',
              border: 'none',
              boxShadow: '0 4px 12px rgba(27,29,22,0.15)'
            }}
          >
            Start Screening Run →
          </button>
          <button
            type="button"
            onClick={() => onNavigate && onNavigate('test')}
            style={{
              padding: '12px 28px',
              borderRadius: '9999px',
              background: 'var(--color-olive-50, #ffffff)',
              color: 'var(--color-olive-900, #2b2e21)',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
              border: '1px solid var(--color-olive-300, #d5dac9)'
            }}
          >
            Open Hero Verification Sandbox
          </button>
        </div>
      </div>
    </section>
  );
};
