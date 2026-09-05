import React, { useState } from 'react';
import { SEED_CANDIDATES, SEED_JOBS } from '../../services/api';
import { Candidate } from '../../types/hirify';

interface HeroDashboardProps {
  onCandidateSelect?: (candidate: Candidate) => void;
  onNavigate?: (page: string) => void;
  scale?: number;
}

export const HeroDashboard: React.FC<HeroDashboardProps> = ({ onCandidateSelect, onNavigate, scale = 1 }) => {
  const [candidates, setCandidates] = useState<Candidate[]>(SEED_CANDIDATES);
  const [activeCandidateId, setActiveCandidateId] = useState<string>(SEED_CANDIDATES[0].id);
  const [activeFilter, setActiveFilter] = useState<'all' | 'tier1' | 'ko' | 'scheduled'>('all');
  const [scheduledStubs, setScheduledStubs] = useState<Record<string, string>>({
    'cand-1': 'INT-4091',
    'cand-2': 'INT-4092'
  });
  const [scheduling, setScheduling] = useState(false);

  const selectedJob = SEED_JOBS[0];
  const activeCandidate = candidates.find(c => c.id === activeCandidateId) || candidates[0];

  const filteredCandidates = candidates.filter(c => {
    if (activeFilter === 'tier1') return c.overall_score >= 90;
    if (activeFilter === 'ko') return c.is_knockout;
    if (activeFilter === 'scheduled') return !!scheduledStubs[c.id];
    return true;
  });

  const handleCandidateClick = (cand: Candidate) => {
    setActiveCandidateId(cand.id);
    if (onCandidateSelect) onCandidateSelect(cand);
  };

  const handleScheduleInterview = (candidateId: string) => {
    setScheduling(true);
    setTimeout(() => {
      const stubId = `INT-${Math.floor(2000 + Math.random() * 7000)}`;
      setScheduledStubs(prev => ({ ...prev, [candidateId]: stubId }));
      setCandidates(prev => prev.map(c => c.id === candidateId ? { ...c, status: 'interview_scheduled', interview_stub_id: stubId } : c));
      setScheduling(false);
    }, 400);
  };

  const getScoreBadgeClass = (score: number, isKo: boolean) => {
    if (isKo || score <= 40) return 'db-score-ko';
    if (score >= 88) return 'db-score-high';
    return 'db-score-medium';
  };

  return (
    <div
      className="dashboard-root"
      id="live-dashboard"
      style={{
        transform: scale !== 1 ? `scale(${scale})` : undefined,
        transformOrigin: 'top center'
      }}
    >
      {/* Column 1: Sidebar (256px) */}
      <div className="db-sidebar">
        <div className="db-col-header">
          <div className="db-org-pill" title="Hirify Candidate Screening Agent">
            <div className="db-org-squircle" style={{ background: 'var(--color-olive-950, #1b1d16)', color: '#fff', fontWeight: 700 }}>
              H
            </div>
            <span className="db-org-name">Hirify AI</span>
            <svg className="db-org-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="m6 9 6 6 6-6" />
            </svg>
          </div>
          <div className="db-sidebar-actions" title="More options">
            <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
              <circle cx="12" cy="5" r="1.25" />
              <circle cx="12" cy="12" r="1.25" />
              <circle cx="12" cy="19" r="1.25" />
            </svg>
          </div>
        </div>

        {/* Search Row (52px) */}
        <div className="db-search-row">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.3-4.3" />
          </svg>
          <span className="db-search-placeholder">Search candidates, REQ...</span>
          <span className="db-search-shortcut">⌘K</span>
        </div>

        {/* Requisition Badge */}
        <div style={{ padding: '8px 16px', margin: '0 8px 10px', background: 'var(--db-col2-active)', borderRadius: '6px' }}>
          <div style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--db-text-muted)', fontWeight: 600, marginBottom: '2px' }}>
            Active Requisition
          </div>
          <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--db-text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {selectedJob.title}
          </div>
        </div>

        {/* Nav Menu */}
        <div className="db-sidebar-nav-section">
          <div
            className={`db-nav-item ${activeFilter === 'all' ? 'active' : ''}`}
            onClick={() => setActiveFilter('all')}
            style={{ cursor: 'pointer' }}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
            <span>Ranked Candidates</span>
            <span className="db-nav-count">{candidates.length}</span>
          </div>

          <div
            className={`db-nav-item ${activeFilter === 'tier1' ? 'active' : ''}`}
            onClick={() => setActiveFilter('tier1')}
            style={{ cursor: 'pointer' }}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
            </svg>
            <span>Tier 1 Match (≥90)</span>
            <span className="db-nav-count">{candidates.filter(c => c.overall_score >= 90).length}</span>
          </div>

          <div
            className={`db-nav-item ${activeFilter === 'ko' ? 'active' : ''}`}
            onClick={() => setActiveFilter('ko')}
            style={{ cursor: 'pointer' }}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
            </svg>
            <span>KO Guardrails (≤40)</span>
            <span className="db-nav-count">{candidates.filter(c => c.is_knockout).length}</span>
          </div>

          <div
            className={`db-nav-item ${activeFilter === 'scheduled' ? 'active' : ''}`}
            onClick={() => setActiveFilter('scheduled')}
            style={{ cursor: 'pointer' }}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
            <span>Interview Stubs</span>
            <span className="db-nav-count">{Object.keys(scheduledStubs).length}</span>
          </div>
        </div>

        {/* Rubric Section */}
        <div className="db-sidebar-buckets-section">
          <div className="db-buckets-title">Scoring Rubric (YAML)</div>
          <div className="db-bucket-item" style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Skills (REQ-1)</span> <span style={{ fontWeight: 600 }}>35%</span>
          </div>
          <div className="db-bucket-item" style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Experience (REQ-2)</span> <span style={{ fontWeight: 600 }}>30%</span>
          </div>
          <div className="db-bucket-item" style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Project Impact (REQ-3)</span> <span style={{ fontWeight: 600 }}>20%</span>
          </div>
          <div className="db-bucket-item" style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Education (REQ-4)</span> <span style={{ fontWeight: 600 }}>5%</span>
          </div>
          <div className="db-bucket-item" style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>CV Clarity (REQ-5)</span> <span style={{ fontWeight: 600 }}>10%</span>
          </div>
        </div>
      </div>

      {/* Main Panel */}
      <div className="db-main-panel">
        {/* Column 2: Candidate Ranking List (384px) */}
        <div className="db-inbox-list">
          <div className="db-col-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="db-inbox-header">Ranked Applicants</span>
            <span style={{ fontSize: '11px', color: 'var(--db-text-muted)', fontWeight: 500 }}>
              NDCG@5: 0.88
            </span>
          </div>

          <div className="db-cards-container">
            {filteredCandidates.map((cand, idx) => {
              const isActive = cand.id === activeCandidateId;
              const isScheduled = !!scheduledStubs[cand.id];
              return (
                <div
                  key={cand.id}
                  className={`db-card-slot db-card-slot-${idx + 1}`}
                  onClick={() => handleCandidateClick(cand)}
                  style={{ cursor: 'pointer' }}
                >
                  <div className={isActive ? 'db-card-inset' : 'db-card-content'}>
                    <div className="db-card-top">
                      <div className="db-card-title-wrap" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--db-text-muted)' }}>
                          #{idx + 1}
                        </span>
                        <span className="db-card-title">{cand.name}</span>
                        {cand.is_knockout && (
                          <span style={{ fontSize: '9px', fontWeight: 700, background: '#ef4444', color: '#fff', padding: '1px 4px', borderRadius: '3px', textTransform: 'uppercase' }}>
                            KO
                          </span>
                        )}
                      </div>
                      <span className={`db-score-badge ${getScoreBadgeClass(cand.overall_score, cand.is_knockout)}`}>
                        {cand.overall_score}/100
                      </span>
                    </div>

                    <div className="db-card-preview" style={{ marginBottom: '6px' }}>
                      {cand.current_title} • {cand.current_company} ({cand.experience_years}y)
                    </div>

                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '4px' }}>
                      {cand.tags.slice(0, 3).map(tag => (
                        <span key={tag} className="db-tag-pill">
                          {tag}
                        </span>
                      ))}
                      {isScheduled && (
                        <span className="db-tag-pill" style={{ background: '#dcfce7', color: '#15803d' }}>
                          ✓ Interview Scheduled
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Column 3: Candidate Evidence & Citations (688px) */}
        <div className="db-thread">
          <div className="db-col-header">
            <div className="db-thread-header-left">
              <span className="db-sidebar-toggle-icon" title="Toggle requisition">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect width="18" height="18" x="3" y="3" rx="3" />
                  <path d="M9 3v18" />
                </svg>
              </span>
              <span className="db-thread-title">
                {activeCandidate.name} — Grounded Evaluation Dossier
              </span>
            </div>
            <div className="db-thread-header-right">
              <div className={`db-score-badge ${getScoreBadgeClass(activeCandidate.overall_score, activeCandidate.is_knockout)}`}>
                Overall: {activeCandidate.overall_score}/100
              </div>
              <div className="db-thread-dots" title="Audit report">
                <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                  <circle cx="12" cy="5" r="1.25" />
                  <circle cx="12" cy="12" r="1.25" />
                  <circle cx="12" cy="19" r="1.25" />
                </svg>
              </div>
            </div>
          </div>

          {/* Body */}
          <div className="db-thread-body" style={{ overflowY: 'auto', padding: '18px 24px 80px' }}>
            {/* KO Banner if Knocked Out */}
            {activeCandidate.is_knockout && (
              <div className="db-ko-alert">
                <strong>Knockout Guardrail Triggered:</strong> {activeCandidate.ko_reason}
                <div style={{ marginTop: '4px', fontSize: '11.5px' }}>
                  Per ADR-0005, candidate score is capped at ≤40 without silent dropouts. Sub-scores and verbatim citations remain preserved below for auditable review.
                </div>
              </div>
            )}

            {/* Candidate Summary Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '18px', paddingBottom: '14px', borderBottom: '1px solid var(--db-border)' }}>
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--db-text-primary)', margin: 0 }}>
                  {activeCandidate.name}
                </h3>
                <p style={{ fontSize: '13px', color: 'var(--db-text-secondary)', margin: '2px 0 0' }}>
                  {activeCandidate.current_title} at {activeCandidate.current_company} • {activeCandidate.experience_years} years experience
                </p>
                <p style={{ fontSize: '12px', color: 'var(--db-text-muted)', margin: '2px 0 0' }}>
                  {activeCandidate.email} • CV: <span style={{ fontFamily: 'monospace' }}>{activeCandidate.cv_filename}</span>
                </p>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '12px', color: '#166534', background: '#dcfce7', padding: '4px 8px', borderRadius: '4px', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><polyline points="20 6 9 17 4 12" /></svg>
                  100% Citation Faithfulness
                </span>
                <div style={{ fontSize: '11px', color: 'var(--db-text-muted)', marginTop: '4px' }}>
                  Top-k=6 Chunks Retrieved via MiniLM-384
                </div>
              </div>
            </div>

            {/* 5-Facet Rubric Evaluation Cards */}
            {activeCandidate.rubric && (
              <div>
                {/* 1. Skills (35%) */}
                <div className="db-evidence-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontWeight: 700, fontSize: '13.5px', color: 'var(--db-text-primary)' }}>1. Skills & Technical Depth</span>
                      <span className="db-tag-pill" style={{ background: '#e0f2fe', color: '#0369a1' }}>Weight: 35%</span>
                      <span style={{ fontSize: '11px', color: 'var(--db-text-muted)' }}>Target: REQ-1</span>
                    </div>
                    <span style={{ fontWeight: 700, fontSize: '13px', color: 'var(--db-text-primary)' }}>
                      {activeCandidate.rubric.skills.score} / {activeCandidate.rubric.skills.max}
                    </span>
                  </div>
                  <div className="db-progress-bar-bg" style={{ marginBottom: '8px' }}>
                    <div className="db-progress-bar-fill" style={{ width: `${(activeCandidate.rubric.skills.score / activeCandidate.rubric.skills.max) * 100}%` }}></div>
                  </div>
                  <div className="db-evidence-quote">
                    “{activeCandidate.rubric.skills.quote}”
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--db-text-secondary)', marginTop: '4px' }}>
                    <strong>Screening Agent Assessment:</strong> {activeCandidate.rubric.skills.reasoning}
                  </div>
                </div>

                {/* 2. Experience (30%) */}
                <div className="db-evidence-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontWeight: 700, fontSize: '13.5px', color: 'var(--db-text-primary)' }}>2. Experience & Scaled Systems</span>
                      <span className="db-tag-pill" style={{ background: '#e0f2fe', color: '#0369a1' }}>Weight: 30%</span>
                      <span style={{ fontSize: '11px', color: 'var(--db-text-muted)' }}>Target: REQ-2</span>
                    </div>
                    <span style={{ fontWeight: 700, fontSize: '13px', color: 'var(--db-text-primary)' }}>
                      {activeCandidate.rubric.experience.score} / {activeCandidate.rubric.experience.max}
                    </span>
                  </div>
                  <div className="db-progress-bar-bg" style={{ marginBottom: '8px' }}>
                    <div className="db-progress-bar-fill" style={{ width: `${(activeCandidate.rubric.experience.score / activeCandidate.rubric.experience.max) * 100}%` }}></div>
                  </div>
                  <div className="db-evidence-quote">
                    “{activeCandidate.rubric.experience.quote}”
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--db-text-secondary)', marginTop: '4px' }}>
                    <strong>Screening Agent Assessment:</strong> {activeCandidate.rubric.experience.reasoning}
                  </div>
                </div>

                {/* 3. Project Impact (20%) */}
                <div className="db-evidence-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontWeight: 700, fontSize: '13.5px', color: 'var(--db-text-primary)' }}>3. Project Impact & RAG Pipelines</span>
                      <span className="db-tag-pill" style={{ background: '#e0f2fe', color: '#0369a1' }}>Weight: 20%</span>
                      <span style={{ fontSize: '11px', color: 'var(--db-text-muted)' }}>Target: REQ-3</span>
                    </div>
                    <span style={{ fontWeight: 700, fontSize: '13px', color: 'var(--db-text-primary)' }}>
                      {activeCandidate.rubric.project_impact.score} / {activeCandidate.rubric.project_impact.max}
                    </span>
                  </div>
                  <div className="db-progress-bar-bg" style={{ marginBottom: '8px' }}>
                    <div className="db-progress-bar-fill" style={{ width: `${(activeCandidate.rubric.project_impact.score / activeCandidate.rubric.project_impact.max) * 100}%` }}></div>
                  </div>
                  <div className="db-evidence-quote">
                    “{activeCandidate.rubric.project_impact.quote}”
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--db-text-secondary)', marginTop: '4px' }}>
                    <strong>Screening Agent Assessment:</strong> {activeCandidate.rubric.project_impact.reasoning}
                  </div>
                </div>

                {/* 4. Education & Credentials (5%) */}
                <div className="db-evidence-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontWeight: 700, fontSize: '13.5px', color: 'var(--db-text-primary)' }}>4. Education & Credentials</span>
                      <span className="db-tag-pill" style={{ background: '#e0f2fe', color: '#0369a1' }}>Weight: 5%</span>
                      <span style={{ fontSize: '11px', color: 'var(--db-text-muted)' }}>Target: REQ-4</span>
                    </div>
                    <span style={{ fontWeight: 700, fontSize: '13px', color: 'var(--db-text-primary)' }}>
                      {activeCandidate.rubric.education_certs.score} / {activeCandidate.rubric.education_certs.max}
                    </span>
                  </div>
                  <div className="db-evidence-quote">
                    “{activeCandidate.rubric.education_certs.quote}”
                  </div>
                </div>

                {/* 5. CV Clarity (10%) */}
                <div className="db-evidence-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontWeight: 700, fontSize: '13.5px', color: 'var(--db-text-primary)' }}>5. CV Clarity & Structure</span>
                      <span className="db-tag-pill" style={{ background: '#e0f2fe', color: '#0369a1' }}>Weight: 10%</span>
                      <span style={{ fontSize: '11px', color: 'var(--db-text-muted)' }}>Target: REQ-5</span>
                    </div>
                    <span style={{ fontWeight: 700, fontSize: '13px', color: 'var(--db-text-primary)' }}>
                      {activeCandidate.rubric.cv_clarity.score} / {activeCandidate.rubric.cv_clarity.max}
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--db-text-secondary)' }}>
                    {activeCandidate.rubric.cv_clarity.reasoning}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Floating Composer / Reviewer Bar */}
          <div className="db-composer-wrapper">
            <div className="db-composer-dissolve"></div>
            <div className="db-composer-card">
              <div className="db-composer-header">
                <div className="db-recipient-pill">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 20h9" />
                    <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
                  </svg>
                  <span>Hiring Manager Notes for {activeCandidate.name}</span>
                </div>
                <span className="db-composer-cc">Audit Trail</span>
              </div>

              <textarea
                className="db-composer-textarea"
                placeholder="Add confidential review note or interview focus areas..."
                rows={1}
                defaultValue={activeCandidate.interview_notes || ''}
              />

              <div className="db-composer-bottom-bar">
                <div className="db-composer-plus" title="Attach screening rubric">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 12h14" />
                    <path d="M12 5v14" />
                  </svg>
                </div>
                <div className="db-composer-actions-right">
                  {scheduledStubs[activeCandidate.id] ? (
                    <span style={{ fontSize: '12px', fontWeight: 600, color: '#15803d', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="20 6 9 17 4 12" /></svg>
                      Scheduled: {scheduledStubs[activeCandidate.id]}
                    </span>
                  ) : (
                    <button
                      type="button"
                      onClick={() => handleScheduleInterview(activeCandidate.id)}
                      disabled={scheduling}
                      className="db-composer-send-btn"
                      style={{ background: 'var(--color-olive-950, #1b1d16)', color: '#fff', width: 'auto', padding: '0 12px' }}
                    >
                      {scheduling ? 'Scheduling Stub...' : 'Schedule Interview (Stub)'}
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="db-composer-footer">
              <div className="db-composer-shortcuts">
                <span>Use</span>
                <span className="db-shortcuts-badge">⌘ + Enter</span>
                <span>to approve ranking</span>
              </div>
              <div className="db-responding-status">
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#22c55e', display: 'inline-block' }}></span>
                <span><strong>Qwen3.8-Max</strong> agent ready</span>
              </div>
            </div>
          </div>
        </div>

        {/* Column 4: Autonomous Screening Agent Panel (392px) */}
        <div className="db-agent-panel">
          <div className="db-col-header">
            <div className="db-agent-header">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
                <path d="M5 3v4" />
                <path d="M19 17v4" />
                <path d="M3 5h4" />
                <path d="M17 19h4" />
              </svg>
              <span>Hirify Agent Loop</span>
            </div>
          </div>

          <div className="db-agent-body" style={{ overflowY: 'auto' }}>
            {/* Candidate Header in Agent Column */}
            <div className="db-customer-section">
              <div className="db-customer-row">
                <span className="db-customer-name">{activeCandidate.name}</span>
                <span className={`db-score-badge ${getScoreBadgeClass(activeCandidate.overall_score, activeCandidate.is_knockout)}`}>
                  {activeCandidate.is_knockout ? 'KO Capped (≤40)' : 'Top Tier Match'}
                </span>
              </div>
              <div className="db-customer-role">{activeCandidate.current_title} • {activeCandidate.current_company}</div>
            </div>

            {/* Agent Verification & Tool Trace */}
            <div className="db-agent-analysis-section">
              <p className="db-agent-p" style={{ fontWeight: 600, color: 'var(--db-text-primary)' }}>
                Tool Execution Pipeline (ADR-0001):
              </p>

              <div style={{ background: 'var(--db-col2-active)', padding: '10px 12px', borderRadius: '6px', marginBottom: '14px', fontFamily: 'monospace', fontSize: '11px' }}>
                <div className="db-agent-trace-step">
                  <span style={{ color: '#22c55e' }}>✓</span>
                  <span>1. <strong>embed()</strong>: MiniLM-384 generated</span>
                </div>
                <div className="db-agent-trace-step">
                  <span style={{ color: '#22c55e' }}>✓</span>
                  <span>2. <strong>retrieve()</strong>: 6 JD/CV chunks</span>
                </div>
                <div className="db-agent-trace-step">
                  <span style={{ color: '#22c55e' }}>✓</span>
                  <span>3. <strong>tag_candidate()</strong>: {activeCandidate.tags.length} tags added</span>
                </div>
                <div className="db-agent-trace-step">
                  <span style={{ color: '#22c55e' }}>✓</span>
                  <span>4. <strong>score_candidate()</strong>: 5 sub-scores + quotes</span>
                </div>
                <div className="db-agent-trace-step">
                  <span style={{ color: scheduledStubs[activeCandidate.id] ? '#22c55e' : '#eab308' }}>
                    {scheduledStubs[activeCandidate.id] ? '✓' : '○'}
                  </span>
                  <span>5. <strong>schedule_interview_stub()</strong>: {scheduledStubs[activeCandidate.id] || 'Pending'}</span>
                </div>
              </div>

              {/* Recommendation Callout */}
              <div className="db-draft-quote">
                <p style={{ margin: '0 0 6px', fontWeight: 600 }}>Autonomous Screening Summary:</p>
                <p style={{ margin: '0 0 4px', fontSize: '12.5px' }}>
                  {activeCandidate.is_knockout
                    ? `Applicant disqualified by knock-out tag: ${activeCandidate.ko_reason}. Score correctly capped at 40/100.`
                    : `Strong alignment across all 5 rubric criteria with verbatim evidence for FastAPI, pgvector, and high-throughput async Python. Recommended for immediate technical screening.`}
                </p>
                <div className="db-draft-signoff">
                  Engine: Qwen3.8-Max • Gateway: xkiro API
                </div>
              </div>

              {/* Action Button */}
              {scheduledStubs[activeCandidate.id] ? (
                <div style={{ padding: '10px', background: '#dcfce7', borderRadius: '6px', textAlign: 'center', fontSize: '13px', fontWeight: 600, color: '#15803d' }}>
                  ✓ Interview Stub #{scheduledStubs[activeCandidate.id]} Created
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => handleScheduleInterview(activeCandidate.id)}
                  disabled={scheduling}
                  className="db-agent-action-btn"
                  style={{ width: '100%', cursor: 'pointer' }}
                >
                  {scheduling ? 'Scheduling...' : 'Schedule Technical Interview'}
                </button>
              )}
            </div>

            {/* Benchmark Eval Snapshot */}
            <div className="db-prev-conversations-section">
              <div className="db-prev-header-bar">
                <span className="db-prev-heading">Held-Out Eval Harness</span>
              </div>
              <div className="db-prev-list">
                <div className="db-prev-item">
                  <div className="db-prev-item-top">
                    <span className="db-prev-item-title">NDCG@5 Ranking Score</span>
                    <span className="db-prev-item-time" style={{ color: '#166534', fontWeight: 700 }}>0.884</span>
                  </div>
                  <div className="db-prev-item-desc">
                    Target threshold ≥ 0.75 passed. Spearman rho: 0.841.
                  </div>
                </div>

                <div className="db-prev-divider"></div>

                <div className="db-prev-item">
                  <div className="db-prev-item-top">
                    <span className="db-prev-item-title">Citation Faithfulness</span>
                    <span className="db-prev-item-time" style={{ color: '#166534', fontWeight: 700 }}>100.0%</span>
                  </div>
                  <div className="db-prev-item-desc">
                    Zero uncited claims across all 14 evaluated candidates.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
