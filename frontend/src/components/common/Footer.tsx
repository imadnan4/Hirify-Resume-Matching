import React from 'react';

interface FooterProps {
  onNavigate?: (page: string) => void;
}

export const Footer: React.FC<FooterProps> = ({ onNavigate }) => {
  return (
    <footer style={{
      background: 'var(--color-olive-100, #fafbf8)',
      borderTop: '1px solid var(--color-olive-200, #e9ece0)',
      padding: '48px 24px 32px',
      marginTop: '80px'
    }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '32px',
          marginBottom: '40px'
        }}>
          {/* Col 1: Brand & Tagline */}
          <div>
            <img
              src="/assets/logos/hirify-familjen__color=olive-950.svg"
              alt="Hirify"
              width="100"
              height="26"
              style={{ marginBottom: '12px' }}
            />
            <p style={{ fontSize: '13px', color: 'var(--color-olive-700, #404434)', lineHeight: '1.5', maxWidth: '280px' }}>
              Autonomous candidate screening agent with RAG citation verification and auditable knock-out guardrails.
            </p>
            <div style={{ fontSize: '12px', color: 'var(--color-olive-600, #5c624b)', marginTop: '8px' }}>
              Theme: Olive Familjen • v1.0
            </div>
          </div>

          {/* Col 2: Screening Pipeline */}
          <div>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-olive-950, #1b1d16)', marginBottom: '12px' }}>
              Agent Architecture
            </div>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '13px', color: 'var(--color-olive-700, #404434)' }}>
              <li>Model: Qwen 3.8-Max (xkiro)</li>
              <li>Embeddings: MiniLM-L6-v2 (384-dim)</li>
              <li>Vector Store: PostgreSQL pgvector</li>
              <li>Scoring Rubric: 5-Facet YAML</li>
            </ul>
          </div>

          {/* Col 3: Navigation Views */}
          <div>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-olive-950, #1b1d16)', marginBottom: '12px' }}>
              Demo Workspace
            </div>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '13px' }}>
              <li>
                <button type="button" onClick={() => onNavigate && onNavigate('upload')} style={{ background: 'none', border: 'none', padding: 0, color: 'var(--color-olive-700, #404434)', cursor: 'pointer', fontSize: '13px' }}>
                  Requisition & CV Ingestion
                </button>
              </li>
              <li>
                <button type="button" onClick={() => onNavigate && onNavigate('ranking')} style={{ background: 'none', border: 'none', padding: 0, color: 'var(--color-olive-700, #404434)', cursor: 'pointer', fontSize: '13px' }}>
                  Candidate Ranking Table
                </button>
              </li>
              <li>
                <button type="button" onClick={() => onNavigate && onNavigate('eval')} style={{ background: 'none', border: 'none', padding: 0, color: 'var(--color-olive-700, #404434)', cursor: 'pointer', fontSize: '13px' }}>
                  Evaluation Benchmarks
                </button>
              </li>
              <li>
                <button type="button" onClick={() => onNavigate && onNavigate('test')} style={{ background: 'none', border: 'none', padding: 0, color: 'var(--color-olive-700, #404434)', cursor: 'pointer', fontSize: '13px' }}>
                  Hero Verification Sandbox (/test)
                </button>
              </li>
            </ul>
          </div>

          {/* Col 4: Guardrails & Compliance */}
          <div>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-olive-950, #1b1d16)', marginBottom: '12px' }}>
              Guardrails & Specs
            </div>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '13px', color: 'var(--color-olive-700, #404434)' }}>
              <li>ADR-0004: FastAPI + Vite React</li>
              <li>ADR-0005: KO Score Caps (≤40)</li>
              <li>ADR-0007: 100% Citation Faithfulness</li>
              <li>No Auth / Single Workspace</li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div style={{
          paddingTop: '24px',
          borderTop: '1px solid var(--color-olive-200, #e9ece0)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '12px',
          color: 'var(--color-olive-600, #5c624b)'
        }}>
          <div>© 2026 Hirify AI • Autonomous Candidate Screening Agent</div>
          <div style={{ display: 'flex', gap: '16px' }}>
            <span>Privacy Policy</span>
            <span>Terms of Service</span>
            <span>Zero Hallucinations</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
