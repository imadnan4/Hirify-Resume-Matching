import React from 'react';
import { HeroSection } from '../components/landing/HeroSection';
import { FeaturesSection } from '../components/landing/FeaturesSection';
import { HowItWorks } from '../components/landing/HowItWorks';
import { MetricsSection } from '../components/landing/MetricsSection';
import { FaqSection } from '../components/landing/FaqSection';
import { CallToAction } from '../components/landing/CallToAction';
import '../styles/test.css';

interface HomeProps {
  onNavigate?: (page: string) => void;
}

export const Home: React.FC<HomeProps> = ({ onNavigate }) => {
  return (
    <div className="hirify-home-page" style={{ minHeight: '100vh', background: 'var(--color-olive-100, #fafbf8)' }}>
      {/* 1. Hero Section with 4-Column Live Dashboard */}
      <HeroSection onNavigate={onNavigate} />

      {/* 2. Core Pillars (RAG, Citations, Knock-Outs) */}
      <FeaturesSection />

      {/* 3. Workflow (Ingest -> Chunk -> Screen -> Dossier) */}
      <HowItWorks />

      {/* 4. Heldout Evaluation Benchmark Metrics */}
      <MetricsSection />

      {/* 5. Frequently Asked Questions */}
      <FaqSection />

      {/* 6. Conversion Call To Action */}
      <CallToAction onNavigate={onNavigate} />
    </div>
  );
};
