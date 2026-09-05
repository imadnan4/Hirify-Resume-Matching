import React from 'react';
import { HeroDashboard } from '../dashboard/HeroDashboard';

interface HeroSectionProps {
  onNavigate?: (page: string) => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ onNavigate }) => {
  return (
    <section style={{ padding: '48px 24px 64px', maxWidth: '1280px', margin: '0 auto' }}>
      {/* Top Banner Content */}
      <div style={{ textAlign: 'center', maxWidth: '840px', margin: '0 auto 48px' }}>
        {/* Pill Badge */}
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 14px', borderRadius: '9999px', background: 'var(--color-olive-200, #e9ece0)', color: 'var(--color-olive-950, #1b1d16)', fontSize: '12.5px', fontWeight: 600, marginBottom: '20px' }}>
          <span>Hirify v1.0</span>
          <span>•</span>
          <span>Autonomous Screening with RAG Grounding</span>
          <span style={{ background: 'var(--color-olive-950, #1b1d16)', color: '#fff', padding: '1px 6px', borderRadius: '9999px', fontSize: '10.5px' }}>ADR-0004</span>
        </div>

        {/* Headline */}
        <h1 style={{
          fontFamily: "'Familjen Grotesk', sans-serif",
          fontSize: 'clamp(36px, 5vw, 56px)',
          fontWeight: 700,
          letterSpacing: '-0.03em',
          lineHeight: '1.1',
          color: 'var(--color-olive-950, #1b1d16)',
          margin: '0 0 20px'
        }}>
          Candidate screening that proves every score with verbatim evidence.
        </h1>

        {/* Subtitle */}
        <p style={{
          fontSize: '17px',
          color: 'var(--color-olive-700, #404434)',
          lineHeight: '1.6',
          maxWidth: '720px',
          margin: '0 auto 28px'
        }}>
          Ingest job requirements and CVs. Ground every rating in verified resume citations with RAG and autonomous AI agent scoring — zero hallucinations, auditable knock-outs.
        </p>

        {/* CTAs */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '14px', flexWrap: 'wrap' }}>
          <button
            type="button"
            onClick={() => onNavigate && onNavigate('ranking')}
            style={{
              padding: '12px 24px',
              borderRadius: '9999px',
              background: 'var(--color-olive-950, #1b1d16)',
              color: '#fff',
              fontSize: '14.5px',
              fontWeight: 700,
              cursor: 'pointer',
              border: 'none',
              boxShadow: '0 4px 14px rgba(0,0,0,0.15)'
            }}
          >
            Launch Screening App →
          </button>
          <button
            type="button"
            onClick={() => onNavigate && onNavigate('test')}
            style={{
              padding: '12px 24px',
              borderRadius: '9999px',
              background: 'var(--color-olive-100, #fafbf8)',
              color: 'var(--color-olive-900, #2b2e21)',
              border: '1px solid var(--color-olive-300, #d5dac9)',
              fontSize: '14.5px',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Inspect Hero Sandbox (/test)
          </button>
        </div>
      </div>

      {/* Embedded Live 4-Column Hero Dashboard Container */}
      <div style={{
        width: '100%',
        maxWidth: '1240px',
        margin: '0 auto',
        borderRadius: '16px',
        overflow: 'hidden',
        boxShadow: '0 25px 60px -15px rgba(27,29,22,0.18)',
        border: '1px solid var(--color-olive-200, #e9ece0)'
      }}>
        <div style={{ overflowX: 'auto' }}>
          <div style={{ minWidth: '1100px' }}>
            <HeroDashboard onNavigate={onNavigate} />
          </div>
        </div>
      </div>
    </section>
  );
};
