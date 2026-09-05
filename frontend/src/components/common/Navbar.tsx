import React from 'react';

interface NavbarProps {
  currentPage: string;
  isDark: boolean;
  onNavigate: (page: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentPage, isDark, onNavigate }) => {
  return (
    <header
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 50,
        background: isDark ? 'var(--color-olive-950, #1b1d16)' : 'var(--color-olive-100, #fafbf8)',
        borderBottom: '1px solid var(--color-olive-200, rgba(0,0,0,0.06))',
        backdropFilter: 'blur(8px)',
        transition: 'background-color 0.2s ease'
      }}
    >
      <div
        style={{
          maxWidth: '1280px',
          margin: '0 auto',
          padding: '12px 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}
      >
        {/* Brand Logo & Tagline */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
          <a
            href="/"
            onClick={(e) => { e.preventDefault(); onNavigate('home'); }}
            style={{ display: 'inline-flex', alignItems: 'center', textDecoration: 'none' }}
          >
            <img
              src="/assets/logos/hirify-familjen__color=olive-950.svg"
              alt="Hirify"
              width="108"
              height="28"
              style={{ display: isDark ? 'none' : 'block' }}
            />
            <img
              src="/assets/logos/hirify-familjen__color=white.svg"
              alt="Hirify"
              width="108"
              height="28"
              style={{ display: isDark ? 'block' : 'none' }}
            />
          </a>

          {/* Workflow Navigation Links */}
          <nav style={{ display: 'flex', alignItems: 'center', gap: '18px' }}>
            <button
              type="button"
              onClick={() => onNavigate('upload')}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '13.5px',
                fontWeight: currentPage === 'upload' ? 700 : 500,
                color: currentPage === 'upload' ? 'var(--color-olive-950, #1b1d16)' : 'var(--color-olive-700, #404434)',
                cursor: 'pointer',
                padding: '4px 0'
              }}
            >
              1. Ingest & Criteria
            </button>
            <button
              type="button"
              onClick={() => onNavigate('ranking')}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '13.5px',
                fontWeight: currentPage === 'ranking' ? 700 : 500,
                color: currentPage === 'ranking' ? 'var(--color-olive-950, #1b1d16)' : 'var(--color-olive-700, #404434)',
                cursor: 'pointer',
                padding: '4px 0'
              }}
            >
              2. Candidate Ranking
            </button>
            <button
              type="button"
              onClick={() => onNavigate('eval')}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '13.5px',
                fontWeight: currentPage === 'eval' ? 700 : 500,
                color: currentPage === 'eval' ? 'var(--color-olive-950, #1b1d16)' : 'var(--color-olive-700, #404434)',
                cursor: 'pointer',
                padding: '4px 0'
              }}
            >
              3. Benchmark Evals
            </button>
            <button
              type="button"
              onClick={() => onNavigate('test')}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '13.5px',
                fontWeight: currentPage === 'test' ? 700 : 500,
                color: currentPage === 'test' ? 'var(--color-olive-950, #1b1d16)' : 'var(--color-olive-700, #404434)',
                cursor: 'pointer',
                padding: '4px 0'
              }}
            >
              Hero Sandbox (/test)
            </button>
          </nav>
        </div>

        {/* Right CTA */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            type="button"
            onClick={() => onNavigate('ranking')}
            style={{
              padding: '8px 18px',
              borderRadius: '9999px',
              background: 'var(--color-olive-950, #1b1d16)',
              color: '#fff',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              border: 'none',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}
          >
            Launch Screening App →
          </button>
        </div>
      </div>
    </header>
  );
};
