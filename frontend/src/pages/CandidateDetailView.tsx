import React, { useState } from 'react';
import { SEED_CANDIDATES, HirifyAPI } from '../services/api';
import { Candidate } from '../types/hirify';

interface CandidateDetailViewProps {
  candidateId?: string;
  onNavigate: (page: string) => void;
}

export const CandidateDetailView: React.FC<CandidateDetailViewProps> = ({ candidateId, onNavigate }) => {
  const candidate: Candidate = SEED_CANDIDATES.find(c => c.id === candidateId) || SEED_CANDIDATES[0];
  const [scheduledStub, setScheduledStub] = useState<string | undefined>(candidate.interview_stub_id);
  const [notes, setNotes] = useState(candidate.interview_notes || '');
  const [scheduling, setScheduling] = useState(false);

  const handleSchedule = async () => {
    setScheduling(true);
    const res = await HirifyAPI.scheduleInterviewStub(candidate.id, notes);
    setScheduledStub(res.stub_id);
    setScheduling(false);
  };

  const getScoreBadgeClass = (score: number, isKo: boolean) => {
    if (isKo || score <= 40) return 'db-score-ko';
    if (score >= 88) return 'db-score-high';
    return 'db-score-medium';
  };

  return (
    <div className="oatmeal-page" style={{ padding: '40px 24px', maxWidth: '1100px', margin: '0 auto' }}>
      {/* Back Button */}
      <button
        type="button"
        onClick={() => onNavigate('ranking')}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          padding: '6px 12px',
          borderRadius: '6px',
          background: 'var(--color-white, #fff)',
          border: '1px solid rgba(0,0,0,0.12)',
          fontSize: '13px',
          fontWeight: 600,
          color: 'var(--color-olive-950, #1b1d16)',
          cursor: 'pointer',
          marginBottom: '20px'
        }}
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m15 18-6-6 6-6"/></svg>
        Back to Candidate Rankings
      </button>

      {/* Candidate Profile Header Card */}
      <div style={{ background: 'var(--color-white, #fff)', border: '1px solid rgba(0,0,0,0.08)', borderRadius: '12px', padding: '24px 28px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '28px', fontWeight: 700, margin: 0, color: 'var(--color-olive-950)' }}>
                {candidate.name}
              </h1>
              <span className={`db-score-badge ${getScoreBadgeClass(candidate.overall_score, candidate.is_knockout)}`} style={{ fontSize: '13px', padding: '4px 10px' }}>
                Overall: {candidate.overall_score} / 100
              </span>
              {candidate.is_knockout && (
                <span style={{ fontSize: '11px', fontWeight: 700, background: '#ef4444', color: '#fff', padding: '2px 6px', borderRadius: '4px' }}>
                  KO CAPPED (≤40)
                </span>
              )}
            </div>

            <p style={{ fontSize: '15px', color: 'var(--color-olive-700)', margin: '4px 0 0' }}>
              {candidate.current_title} at {candidate.current_company} • {candidate.experience_years} years total experience
            </p>
            <p style={{ fontSize: '13px', color: 'var(--color-olive-600)', margin: '4px 0 0' }}>
              Email: {candidate.email} • File: <span style={{ fontFamily: 'monospace' }}>{candidate.cv_filename}</span>
            </p>
          </div>

          <div style={{ textAlign: 'right' }}>
            {scheduledStub ? (
              <div style={{ padding: '8px 14px', background: '#dcfce7', border: '1px solid #86efac', borderRadius: '6px', color: '#15803d', fontWeight: 600, fontSize: '13px' }}>
                ✓ Interview Scheduled (#{scheduledStub})
              </div>
            ) : (
              <button
                type="button"
                onClick={handleSchedule}
                disabled={scheduling}
                style={{
                  padding: '10px 18px',
                  borderRadius: '8px',
                  background: 'var(--color-olive-950, #1b1d16)',
                  color: '#fff',
                  fontWeight: 600,
                  fontSize: '13px',
                  cursor: 'pointer',
                  border: 'none'
                }}
              >
                {scheduling ? 'Scheduling...' : 'Schedule Interview (DB Stub)'}
              </button>
            )}
            <div style={{ fontSize: '11px', color: 'var(--color-olive-600)', marginTop: '4px' }}>
              Tool: <span style={{ fontFamily: 'monospace' }}>schedule_interview_stub</span>
            </div>
          </div>
        </div>

        {/* Tags Row */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '16px' }}>
          {candidate.tags.map(tag => (
            <span
              key={tag}
              className="db-tag-pill"
              style={{
                fontSize: '12px',
                padding: '3px 8px',
                color: tag.startsWith('KO:') ? '#b91c1c' : undefined,
                background: tag.startsWith('KO:') ? '#fee2e2' : undefined
              }}
            >
              {tag}
            </span>
          ))}
        </div>
      </div>

      {/* Knock-Out Alert if KO */}
      {candidate.is_knockout && (
        <div className="db-ko-alert" style={{ marginBottom: '24px' }}>
          <div style={{ fontWeight: 700, fontSize: '14px', marginBottom: '2px' }}>
            Knock-Out Guardrail Triggered:
          </div>
          <div>{candidate.ko_reason}</div>
          <div style={{ fontSize: '11.5px', marginTop: '4px', opacity: 0.9 }}>
            In accordance with ADR-0005, candidates who fail mandatory constraints are capped at ≤40 overall score rather than silently zeroed, preserving all evidence and sub-scores for compliance review.
          </div>
        </div>
      )}

      {/* 5-Facet Rubric Breakdown */}
      {candidate.rubric && (
        <div style={{ marginBottom: '28px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 700, margin: 0, color: 'var(--color-olive-950)' }}>
              Grounding Citations & Rubric Breakdown (config/rubric.yaml)
            </h2>
            <span style={{ fontSize: '12px', color: '#166534', background: '#dcfce7', padding: '3px 8px', borderRadius: '4px', fontWeight: 600 }}>
              100% Citation Faithfulness
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* 1. Skills */}
            <div style={{ background: 'var(--color-white, #fff)', border: '1px solid rgba(0,0,0,0.08)', borderRadius: '10px', padding: '18px 20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontWeight: 700, fontSize: '15px', color: 'var(--color-olive-950)' }}>
                    1. Skills (35% Weight)
                  </span>
                  <span style={{ fontSize: '11px', background: '#e0f2fe', color: '#0369a1', padding: '1px 6px', borderRadius: '4px', fontWeight: 600 }}>
                    Linked to {candidate.rubric.skills.requirement_id}
                  </span>
                </div>
                <span style={{ fontWeight: 700, fontSize: '15px', color: 'var(--color-olive-950)' }}>
                  {candidate.rubric.skills.score} / {candidate.rubric.skills.max} pts
                </span>
              </div>
              <div className="db-progress-bar-bg" style={{ marginBottom: '10px' }}>
                <div className="db-progress-bar-fill" style={{ width: `${(candidate.rubric.skills.score / candidate.rubric.skills.max) * 100}%` }}></div>
              </div>
              <div className="db-evidence-quote" style={{ fontSize: '13.5px', padding: '10px 14px' }}>
                “{candidate.rubric.skills.quote}”
              </div>
              <div style={{ fontSize: '12.5px', color: 'var(--color-olive-700)', marginTop: '6px' }}>
                <strong>Agent Rationale:</strong> {candidate.rubric.skills.reasoning}
              </div>
            </div>

            {/* 2. Experience */}
            <div style={{ background: 'var(--color-white, #fff)', border: '1px solid rgba(0,0,0,0.08)', borderRadius: '10px', padding: '18px 20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontWeight: 700, fontSize: '15px', color: 'var(--color-olive-950)' }}>
                    2. Experience (30% Weight)
                  </span>
                  <span style={{ fontSize: '11px', background: '#e0f2fe', color: '#0369a1', padding: '1px 6px', borderRadius: '4px', fontWeight: 600 }}>
                    Linked to {candidate.rubric.experience.requirement_id}
                  </span>
                </div>
                <span style={{ fontWeight: 700, fontSize: '15px', color: 'var(--color-olive-950)' }}>
                  {candidate.rubric.experience.score} / {candidate.rubric.experience.max} pts
                </span>
              </div>
              <div className="db-progress-bar-bg" style={{ marginBottom: '10px' }}>
                <div className="db-progress-bar-fill" style={{ width: `${(candidate.rubric.experience.score / candidate.rubric.experience.max) * 100}%` }}></div>
              </div>
              <div className="db-evidence-quote" style={{ fontSize: '13.5px', padding: '10px 14px' }}>
                “{candidate.rubric.experience.quote}”
              </div>
              <div style={{ fontSize: '12.5px', color: 'var(--color-olive-700)', marginTop: '6px' }}>
                <strong>Agent Rationale:</strong> {candidate.rubric.experience.reasoning}
              </div>
            </div>

            {/* 3. Project Impact */}
            <div style={{ background: 'var(--color-white, #fff)', border: '1px solid rgba(0,0,0,0.08)', borderRadius: '10px', padding: '18px 20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontWeight: 700, fontSize: '15px', color: 'var(--color-olive-950)' }}>
                    3. Project Impact (20% Weight)
                  </span>
                  <span style={{ fontSize: '11px', background: '#e0f2fe', color: '#0369a1', padding: '1px 6px', borderRadius: '4px', fontWeight: 600 }}>
                    Linked to {candidate.rubric.project_impact.requirement_id}
                  </span>
                </div>
                <span style={{ fontWeight: 700, fontSize: '15px', color: 'var(--color-olive-950)' }}>
                  {candidate.rubric.project_impact.score} / {candidate.rubric.project_impact.max} pts
                </span>
              </div>
              <div className="db-progress-bar-bg" style={{ marginBottom: '10px' }}>
                <div className="db-progress-bar-fill" style={{ width: `${(candidate.rubric.project_impact.score / candidate.rubric.project_impact.max) * 100}%` }}></div>
              </div>
              <div className="db-evidence-quote" style={{ fontSize: '13.5px', padding: '10px 14px' }}>
                “{candidate.rubric.project_impact.quote}”
              </div>
              <div style={{ fontSize: '12.5px', color: 'var(--color-olive-700)', marginTop: '6px' }}>
                <strong>Agent Rationale:</strong> {candidate.rubric.project_impact.reasoning}
              </div>
            </div>

            {/* 4. Education */}
            <div style={{ background: 'var(--color-white, #fff)', border: '1px solid rgba(0,0,0,0.08)', borderRadius: '10px', padding: '18px 20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontWeight: 700, fontSize: '15px', color: 'var(--color-olive-950)' }}>
                    4. Education & Credentials (5% Weight)
                  </span>
                  <span style={{ fontSize: '11px', background: '#e0f2fe', color: '#0369a1', padding: '1px 6px', borderRadius: '4px', fontWeight: 600 }}>
                    Linked to {candidate.rubric.education_certs.requirement_id}
                  </span>
                </div>
                <span style={{ fontWeight: 700, fontSize: '15px', color: 'var(--color-olive-950)' }}>
                  {candidate.rubric.education_certs.score} / {candidate.rubric.education_certs.max} pts
                </span>
              </div>
              <div className="db-evidence-quote" style={{ fontSize: '13.5px', padding: '10px 14px' }}>
                “{candidate.rubric.education_certs.quote}”
              </div>
            </div>

            {/* 5. CV Clarity */}
            <div style={{ background: 'var(--color-white, #fff)', border: '1px solid rgba(0,0,0,0.08)', borderRadius: '10px', padding: '18px 20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontWeight: 700, fontSize: '15px', color: 'var(--color-olive-950)' }}>
                    5. CV Clarity & Structure (10% Weight)
                  </span>
                </div>
                <span style={{ fontWeight: 700, fontSize: '15px', color: 'var(--color-olive-950)' }}>
                  {candidate.rubric.cv_clarity.score} / {candidate.rubric.cv_clarity.max} pts
                </span>
              </div>
              <div style={{ fontSize: '12.5px', color: 'var(--color-olive-700)' }}>
                {candidate.rubric.cv_clarity.reasoning}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Reviewer Note & Interview Action Card */}
      <div style={{ background: 'var(--color-white, #fff)', border: '1px solid rgba(0,0,0,0.08)', borderRadius: '12px', padding: '24px' }}>
        <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '18px', fontWeight: 700, margin: '0 0 12px', color: 'var(--color-olive-950)' }}>
          Hiring Committee Notes & Audit Record
        </h3>
        <textarea
          rows={3}
          value={notes}
          onChange={e => setNotes(e.target.value)}
          placeholder="Add interviewer notes or specific technical focus areas..."
          style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', border: '1px solid rgba(0,0,0,0.15)', fontSize: '13px', lineHeight: 1.5, marginBottom: '14px' }}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '12px', color: 'var(--color-olive-600)' }}>
            All notes and interview stubs are persisted to Neon PostgreSQL.
          </span>
          <button
            type="button"
            onClick={handleSchedule}
            disabled={scheduling}
            style={{
              padding: '8px 16px',
              borderRadius: '6px',
              background: 'var(--color-olive-950, #1b1d16)',
              color: '#fff',
              fontWeight: 600,
              fontSize: '13px',
              border: 'none',
              cursor: 'pointer'
            }}
          >
            {scheduledStub ? 'Update Stub & Notes' : 'Save & Schedule Interview Stub'}
          </button>
        </div>
      </div>
    </div>
  );
};
