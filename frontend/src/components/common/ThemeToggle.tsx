import React, { useEffect, useState } from 'react';

interface ThemeToggleProps {
  isDark: boolean;
  onToggle: () => void;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ isDark, onToggle }) => {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('hide-toolbar') === '1' || params.get('clean') === '1') {
      setVisible(false);
    }
  }, []);

  if (!visible) return null;

  return (
    <button
      id="oatmeal-theme-toggle"
      type="button"
      onClick={onToggle}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      style={{
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        zIndex: 99999,
        fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        fontSize: '13px',
        fontWeight: 600,
        padding: '8px 14px',
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        borderRadius: '9999px',
        border: `1px solid ${isDark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.12)'}`,
        background: isDark ? '#262820' : '#ffffff',
        color: isDark ? '#f4f5f0' : '#1b1d16',
        boxShadow: '0 4px 14px rgba(0,0,0,0.12)',
        cursor: 'pointer',
        transition: 'transform 0.15s ease, box-shadow 0.15s ease',
      }}
    >
      <span aria-hidden="true" style={{ fontSize: '14px' }}>
        {isDark ? '🌙' : '☀️'}
      </span>
      <span>{isDark ? 'Dark' : 'Light'}</span>
    </button>
  );
};
