import React, { useState, useEffect } from 'react';
import '../styles/test.css';
import { HeroDashboard } from '../components/dashboard/HeroDashboard';

interface TestProps {
  onNavigate?: (page: string) => void;
}

export const Test: React.FC<TestProps> = ({ onNavigate }) => {
  const [mode, setMode] = useState<'live' | 'original' | 'overlay' | 'side'>('live');
  const [opacity, setOpacity] = useState<number>(50);
  const [isFit, setIsFit] = useState<boolean>(true);
  const [scale, setScale] = useState<number>(1);

  const toggleFlip = () => {
    if (mode === 'original' || (mode === 'overlay' && opacity === 0)) {
      setMode('live');
      setOpacity(100);
    } else {
      setMode('original');
      setOpacity(0);
    }
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName;
      if (e.code === 'Space' && tag !== 'INPUT' && tag !== 'TEXTAREA') {
        e.preventDefault();
        toggleFlip();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [mode, opacity]);

  const [isDark, setIsDark] = useState<boolean>(() => {
    return document.documentElement.classList.contains('dark') ||
      (!document.documentElement.classList.contains('light') &&
        window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
  });

  useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.classList.contains('dark'));
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  const toggleTheme = () => {
    const nextDark = !isDark;
    setIsDark(nextDark);
    if (nextDark) {
      document.documentElement.classList.remove('light');
      document.documentElement.classList.add('dark');
      document.documentElement.style.backgroundColor = 'var(--color-olive-950, #1b1d16)';
      document.documentElement.style.colorScheme = 'dark';
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
      document.documentElement.style.backgroundColor = 'var(--color-olive-100, #fafbf8)';
      document.documentElement.style.colorScheme = 'light';
    }
    try {
      localStorage.setItem('oatmeal-theme', nextDark ? 'dark' : 'light');
    } catch (e) {}
  };

  useEffect(() => {
    const calculateScale = () => {
      if (!isFit) {
        setScale(1);
        return;
      }
      const availableWidth = window.innerWidth - 48;
      const targetWidth = mode === 'side' ? 1720 * 2 + 64 : 1720;
      const calculatedScale = Math.min(1, Math.max(0.3, availableWidth / targetWidth));
      setScale(calculatedScale);
    };

    calculateScale();
    window.addEventListener('resize', calculateScale);
    return () => window.removeEventListener('resize', calculateScale);
  }, [isFit, mode]);

  const refAsset = '/assets/screenshots/1.webp';

  const renderDashboard = () => (
    <div
      style={{
        opacity: mode === 'original' ? 0 : mode === 'overlay' ? opacity / 100 : 1,
        pointerEvents: mode === 'original' ? 'none' : 'auto',
      }}
    >
      <HeroDashboard onNavigate={onNavigate} />
    </div>
  );

  return (
    <div className="test-sandbox-root" style={{ minHeight: '100vh', background: 'var(--color-olive-950, #1b1d16)' }}>
      {/* Verification Toolbar */}
      <div className="test-toolbar">
        <div className="test-nav-group">
          <button
            type="button"
            className="test-btn"
            onClick={() => onNavigate ? onNavigate('home') : (window.location.href = '/')}
            style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m15 18-6-6 6-6"/></svg>
            Back to Hirify
          </button>
          <span style={{ color: 'var(--db-text-muted)', margin: '0 4px' }}>|</span>
          <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--db-text-primary)' }}>Screening Dashboard Mode:</span>
          <button
            type="button"
            className={`test-btn ${mode === 'live' ? 'active' : ''}`}
            onClick={() => { setMode('live'); setOpacity(100); }}
          >
            Live Code (100%)
          </button>
          <button
            type="button"
            className={`test-btn ${mode === 'original' ? 'active' : ''}`}
            onClick={() => { setMode('original'); setOpacity(0); }}
          >
            Original Ref (100%)
          </button>
          <button
            type="button"
            className={`test-btn ${mode === 'overlay' ? 'active' : ''}`}
            onClick={() => setMode('overlay')}
          >
            Overlay Diff
          </button>
          <button
            type="button"
            className={`test-btn ${mode === 'side' ? 'active' : ''}`}
            onClick={() => setMode('side')}
          >
            Side-by-Side
          </button>
          <button
            type="button"
            className="test-btn"
            style={{ fontWeight: 600, background: 'var(--db-col2-active)' }}
            onClick={toggleFlip}
            title="Press Spacebar to toggle"
          >
            🔄 Flip (Code / Ref)
          </button>
        </div>

        {mode === 'overlay' && (
          <div className="test-nav-group">
            <div className="test-slider-wrap">
              <button type="button" className="test-btn" style={{ padding: '2px 8px', fontSize: '11px' }} onClick={() => setOpacity(0)}>0% Ref</button>
              <input
                type="range"
                min="0"
                max="100"
                value={opacity}
                onChange={(e) => setOpacity(Number(e.target.value))}
                style={{ width: '120px' }}
              />
              <button type="button" className="test-btn" style={{ padding: '2px 8px', fontSize: '11px' }} onClick={() => setOpacity(100)}>100% Code</button>
              <button type="button" className="test-btn" style={{ padding: '2px 8px', fontSize: '11px' }} onClick={() => setOpacity(50)}>50%</button>
              <span style={{ fontWeight: 600, minWidth: '32px', color: 'var(--db-text-primary)' }}>{opacity}%</span>
            </div>
          </div>
        )}

        <div className="test-nav-group">
          <span style={{ fontSize: '11px', color: 'var(--db-text-muted)', marginRight: '4px' }}>💡 Space: Flip</span>
          <button type="button" className="test-btn" onClick={toggleTheme}>
            {isDark ? (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>
                </svg>
                <span>Light Mode</span>
              </>
            ) : (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>
                </svg>
                <span>Dark Mode</span>
              </>
            )}
          </button>

          <button
            type="button"
            className={`test-btn ${isFit ? 'active' : ''}`}
            onClick={() => setIsFit(!isFit)}
          >
            {isFit ? 'Actual Size (100%)' : 'Fit Screen (Scale)'}
          </button>
        </div>
      </div>

      {/* Main Viewport */}
      <div className="dashboard-viewport">
        <div className="dashboard-scaler" style={{ transform: `scale(${scale})` }}>
          {mode === 'side' ? (
            <div className="side-by-side-container">
              <div className="side-col">
                <div className="side-col-header">1. Live Coded Hirify Screening Agent (HTML / CSS):</div>
                {renderDashboard()}
              </div>
              <div className="side-col">
                <div className="side-col-header">2. Original Oatmeal Hero Asset:</div>
                <img
                  src={refAsset}
                  alt="Original Reference Screenshot"
                  style={{
                    width: '1720px',
                    height: '995px',
                    borderRadius: '12px',
                    border: '1px solid var(--db-border)',
                    boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)',
                  }}
                />
              </div>
            </div>
          ) : (
            <div className="comparison-container">
              {(mode === 'overlay' || mode === 'original') && (
                <img
                  className="comparison-screenshot"
                  src={refAsset}
                  alt="Original Reference Screenshot"
                  style={{ opacity: 1 }}
                />
              )}
              {renderDashboard()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
