import React, { useState, useEffect } from 'react';
import { Home } from './pages/Home';
import { UploadView } from './pages/UploadView';
import { RankingView } from './pages/RankingView';
import { CandidateDetailView } from './pages/CandidateDetailView';
import { EvalView } from './pages/EvalView';
import { Test } from './pages/Test';
import { Pricing } from './pages/Pricing';
import { About } from './pages/About';
import { PrivacyPolicy } from './pages/PrivacyPolicy';
import { NotFound } from './pages/NotFound';
import { Navbar } from './components/common/Navbar';
import { Footer } from './components/common/Footer';
import { ThemeToggle } from './components/common/ThemeToggle';

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<string>(() => {
    const params = new URLSearchParams(window.location.search);
    const p = params.get('page');
    if (p) return p.replace(/\.html$/, '');
    const pathname = window.location.pathname.replace(/^\//, '').replace(/\.html$/, '');
    if (pathname && pathname !== 'index') return pathname;
    return 'home';
  });

  const [selectedCandidateId, setSelectedCandidateId] = useState<string>('cand-1');

  const [isDark, setIsDark] = useState<boolean>(() => {
    const saved = localStorage.getItem('oatmeal-theme');
    if (saved === 'dark') return true;
    if (saved === 'light') return false;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  const applyThemeToDOM = (dark: boolean) => {
    if (!dark) {
      document.documentElement.style.backgroundColor = 'var(--color-olive-100, #fafbf8)';
      document.documentElement.style.colorScheme = 'light';
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
    } else {
      document.documentElement.style.backgroundColor = 'var(--color-olive-950, #1b1d16)';
      document.documentElement.style.colorScheme = 'dark';
      document.documentElement.classList.remove('light');
      document.documentElement.classList.add('dark');
    }
    try {
      localStorage.setItem('oatmeal-theme', dark ? 'dark' : 'light');
    } catch (e) {}
  };

  useEffect(() => {
    applyThemeToDOM(isDark);
  }, [isDark]);

  const handleNavigate = (page: string, candidateId?: string) => {
    const cleanPage = page.replace(/^\.\//, '').replace(/\.html$/, '');
    if (candidateId) {
      setSelectedCandidateId(candidateId);
    }
    setCurrentPage(cleanPage);
    const url = new URL(window.location.href);
    url.searchParams.set('page', cleanPage);
    if (candidateId) {
      url.searchParams.set('candidate', candidateId);
    } else {
      url.searchParams.delete('candidate');
    }
    window.history.pushState({}, '', url.toString());
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  useEffect(() => {
    const handlePopState = () => {
      const params = new URLSearchParams(window.location.search);
      const p = params.get('page') || 'home';
      const c = params.get('candidate');
      if (c) setSelectedCandidateId(c);
      setCurrentPage(p.replace(/\.html$/, ''));
    };
    window.addEventListener('popstate', handlePopState);

    const handleLinkClick = (e: MouseEvent) => {
      const target = (e.target as HTMLElement).closest('a');
      if (!target) return;
      const href = target.getAttribute('href');
      if (!href) return;
      if (href.startsWith('./') && href.endsWith('.html')) {
        e.preventDefault();
        handleNavigate(href);
      }
    };
    document.addEventListener('click', handleLinkClick);

    return () => {
      window.removeEventListener('popstate', handlePopState);
      document.removeEventListener('click', handleLinkClick);
    };
  }, []);

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <Home onNavigate={handleNavigate} />;
      case 'upload':
        return <UploadView onNavigate={handleNavigate} />;
      case 'ranking':
        return <RankingView onNavigate={handleNavigate} />;
      case 'candidate':
        return <CandidateDetailView candidateId={selectedCandidateId} onNavigate={handleNavigate} />;
      case 'eval':
        return <EvalView onNavigate={handleNavigate} />;
      case 'pricing':
        return <Pricing onNavigate={handleNavigate} />;
      case 'about':
        return <About onNavigate={handleNavigate} />;
      case 'privacy-policy':
        return <PrivacyPolicy onNavigate={handleNavigate} />;
      case '404':
        return <NotFound onNavigate={handleNavigate} />;
      case 'test':
        return <Test onNavigate={handleNavigate} />;
      default:
        return <Home onNavigate={handleNavigate} />;
    }
  };

  return (
    <>
      <Navbar
        currentPage={currentPage}
        isDark={isDark}
        onNavigate={handleNavigate}
      />

      <main>
        {renderPage()}
      </main>

      <Footer onNavigate={handleNavigate} />

      <ThemeToggle
        isDark={isDark}
        onToggle={() => setIsDark((prev) => !prev)}
      />
    </>
  );
};
