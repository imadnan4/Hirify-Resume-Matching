import React, { useState, useEffect } from 'react';
import { HirifyAPI, SEED_CANDIDATES } from '../services/api';
import { Candidate } from '../types/hirify';

interface RankingViewProps {
  onNavigate: (page: string, candidateId?: string) => void;
}

export const RankingView: React.FC<RankingViewProps> = ({ onNavigate }) => {
  const [candidates, setCandidates] = useState<Candidate[]>(SEED_CANDIDATES);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'all' | 'qualified' | 'knockout' | 'scheduled'>('all');
  const [schedulingId, setSchedulingId] = useState<string | null>(null);

  useEffect(() => {
    HirifyAPI.getCandidates('job-1').then(data => {
      if (data && data.length > 0) setCandidates(data);
    });
  }, []);

  const handleScheduleStub = async (candidateId: string) => {
    setSchedulingId(candidateId);
    const res = await HirifyAPI.scheduleInterviewStub(candidateId, 'Scheduled via Ranking Leaderboard quick action.');
    setCandidates(prev => prev.map(c => {
      if (c.id === candidateId) {
        return {
          ...c,
          status: 'interview_scheduled',
          interview_stub_id: res.stub_id,
          interview_notes: 'Scheduled via Ranking Leaderboard quick action.'
        };
      }
      return c;
    }));
    setSchedulingId(null);
  };

  const filtered = candidates.filter(c => {
    if (filter === 'qualified' && c.is_knockout) return false;
    if (filter === 'knockout' && !c.is_knockout) return false;
    if (filter === 'scheduled' && c.status !== 'interview_scheduled') return false;

    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return (
      c.name.toLowerCase().includes(q) ||
      c.current_title.toLowerCase().includes(q) ||
      c.tags.some(t => t.toLowerCase().includes(q))
    );
  });

  const getScoreBadgeStyle = (score: number, isKo: boolean) => {
    if (isKo || score <= 40) {
      return { background: '#fee2e2', color: '#b91c1c', border: '1px solid #f87171' };
    }
    if (score >= 88) {
      return { background: '#dcfce7', color: '#15803d', border: '1px solid #86efac' };
    }
    return { background: 'var(--color-olive-200, #e9ece0)', color: 'var(--color-olive-900, #2b2e21)', border: '1px solid var(--color-olive-300, #d5dac9)' };
  };

  return (
    <div className="oatmeal-page" style={{ padding: '40px 24px', maxWidth: '1180px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '28px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span style={{
              fontSize: '11px',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              padding: '4px 10px',
              borderRadius: '9999px',
              background: 'var(--color-olive-200, #e9ece0)',
              color: 'var(--color-olive-900, #2b2e21)',
              fontWeight: 700
            }}>
              Step 2 of 3: Leaderboard
            </span>
            <span style={{ fontSize: '12px', color: 'var(--color-olive-600, #5c624b)' }}>
              Requisition: Senior Backend AI / Systems Engineer
            </span>
          </div>
          <h1 style={{
            fontFamily: "'Familjen Grotesk', sans-serif",
            fontSize: '34px',
            fontWeight: 700,
            letterSpacing: '-0.02em',
            color: 'var(--color-olive-950, #1b1d16)',
            margin: 0
          }}>
            Candidate Screening Ranking
          </h1>
          <p style={{
            fontSize: '14.5px',
            color: 'var(--color-olive-700, #404434)',
            marginTop: '6px',
            lineHeight: '1.4'
          }}>
            Rankings synthesized by Qwen 3.8-Max with verbatim CV quotes. Knockout candidates are auditable and capped at ≤40 (ADR-0005).
          </p>
        </div>

        {/* Quick Actions */}
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            type="button"
            onClick={() => onNavigate('upload')}
            style={{
              padding: '8px 14px',
              borderRadius: '8px',
              border: '1px solid var(--color-olive-300, #d5dac9)',
              background: 'var(--color-olive-50, #fff)',
              color: 'var(--color-olive-900, #2b2e21)',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            + Ingest More CVs
          </button>
          <button
            type="button"
            onClick={() => onNavigate('eval')}
            style={{
              padding: '8px 14px',
              borderRadius: '8px',
              border: 'none',
              background: 'var(--color-olive-950, #1b1d16)',
              color: '#fff',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            View Held-out Benchmark Evals →
          </button>
        </div>
      </div>

      {/* Metrics Bar */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '28px'
      }}>
        <div style={{
          padding: '16px 20px',
          borderRadius: '12px',
          background: 'var(--color-olive-50, #fff)',
          border: '1px solid var(--color-olive-200, #e9ece0)',
          boxShadow: '0 2px 8px rgba(0,0,0,0.02)'
        }}>
          <div style={{ fontSize: '11px', color: 'var(--color-olive-600, #5c624b)', fontWeight: 600, textTransform: 'uppercase' }}>Total Screened</div>
          <div style={{ fontSize: '28px', fontFamily: "'Familjen Grotesk', sans-serif", fontWeight: 700, color: 'var(--color-olive-950, #1b1d16)', marginTop: '4px' }}>
            {candidates.length} Candidates
          </div>
          <div style={{ fontSize: '12px', color: '#15803d', fontWeight: 600, marginTop: '2px' }}>100% Citation Faithfulness</div>
        </div>

        <div style={{
          padding: '16px 20px',
          borderRadius: '12px',
          background: 'var(--color-olive-50, #fff)',
          border: '1px solid var(--color-olive-200, #e9ece0)',
          boxShadow: '0 2px 8px rgba(0,0,0,0.02)'
        }}>
          <div style={{ fontSize: '11px', color: 'var(--color-olive-600, #5c624b)', fontWeight: 600, textTransform: 'uppercase' }}>Top Candidate</div>
          <div style={{ fontSize: '28px', fontFamily: "'Familjen Grotesk', sans-serif", fontWeight: 700, color: 'var(--color-olive-950, #1b1d16)', marginTop: '4px' }}>
            95 / 100
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-olive-700, #404434)', marginTop: '2px' }}>Marcus Vance (Staff SWE)</div>
        </div>

        <div style={{
          padding: '16px 20px',
          borderRadius: '12px',
          background: 'var(--color-olive-50, #fff)',
          border: '1px solid var(--color-olive-200, #e9ece0)',
          boxShadow: '0 2px 8px rgba(0,0,0,0.02)'
        }}>
          <div style={{ fontSize: '11px', color: 'var(--color-olive-600, #5c624b)', fontWeight: 600, textTransform: 'uppercase' }}>Knock-outs Flagged</div>
          <div style={{ fontSize: '28px', fontFamily: "'Familjen Grotesk', sans-serif", fontWeight: 700, color: '#b91c1c', marginTop: '4px' }}>
            2 Candidates
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-olive-600, #5c624b)', marginTop: '2px' }}>Auditable rule caps (≤40)</div>
        </div>

        <div style={{
          padding: '16px 20px',
          borderRadius: '12px',
          background: 'var(--color-olive-50, #fff)',
          border: '1px solid var(--color-olive-200, #e9ece0)',
          boxShadow: '0 2px 8px rgba(0,0,0,0.02)'
        }}>
          <div style={{ fontSize: '11px', color: 'var(--color-olive-600, #5c624b)', fontWeight: 600, textTransform: 'uppercase' }}>Evaluation Quality</div>
          <div style={{ fontSize: '28px', fontFamily: "'Familjen Grotesk', sans-serif", fontWeight: 700, color: '#15803d', marginTop: '4px' }}>
            0.884 NDCG@5
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-olive-600, #5c624b)', marginTop: '2px' }}>P@3: 1.00 (Exceeds ≥0.75 target)</div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '12px',
        marginBottom: '20px',
        padding: '12px 16px',
        background: 'var(--color-olive-50, #fff)',
        border: '1px solid var(--color-olive-200, #e9ece0)',
        borderRadius: '12px'
      }}>
        {/* Filter Pills */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {[
            { id: 'all', label: `All (${candidates.length})` },
            { id: 'qualified', label: `Qualified (${candidates.filter(c => !c.is_knockout).length})` },
            { id: 'knockout', label: `Knockouts (${candidates.filter(c => c.is_knockout).length})` },
            { id: 'scheduled', label: `Interviews (${candidates.filter(c => c.status === 'interview_scheduled').length})` }
          ].map(f => (
            <button
              key={f.id}
              type="button"
              onClick={() => setFilter(f.id as any)}
              style={{
                padding: '6px 12px',
                borderRadius: '9999px',
                fontSize: '12.5px',
                fontWeight: filter === f.id ? 700 : 500,
                background: filter === f.id ? 'var(--color-olive-950, #1b1d16)' : 'var(--color-olive-100, #fafbf8)',
                color: filter === f.id ? '#fff' : 'var(--color-olive-800, #343729)',
                border: '1px solid var(--color-olive-200, #e9ece0)',
                cursor: 'pointer'
              }}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div style={{ minWidth: '240px' }}>
          <input
            type="text"
            placeholder="Search candidates, skills, tags..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 14px',
              borderRadius: '8px',
              border: '1px solid var(--color-olive-300, #d5dac9)',
              background: 'var(--color-olive-100, #fafbf8)',
              fontSize: '13px',
              color: 'var(--color-olive-950, #1b1d16)',
              outline: 'none',
              boxSizing: 'border-box'
            }}
          />
        </div>
      </div>

      {/* Candidates Table / Cards List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {filtered.map((candidate, idx) => {
          const badgeStyle = getScoreBadgeStyle(candidate.overall_score, candidate.is_knockout);

          return (
            <div
              key={candidate.id}
              style={{
                background: 'var(--color-olive-50, #fff)',
                border: candidate.is_knockout ? '1px solid #fecaca' : '1px solid var(--color-olive-200, #e9ece0)',
                borderRadius: '14px',
                padding: '20px 24px',
                boxShadow: '0 3px 10px rgba(0,0,0,0.02)',
                transition: 'transform 0.15s ease, box-shadow 0.15s ease'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
                {/* Left info */}
                <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                  {/* Rank Badge */}
                  <div style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: '10px',
                    background: idx === 0 && !candidate.is_knockout ? 'var(--color-olive-950, #1b1d16)' : 'var(--color-olive-200, #e9ece0)',
                    color: idx === 0 && !candidate.is_knockout ? '#fff' : 'var(--color-olive-900, #2b2e21)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontFamily: "'Familjen Grotesk', sans-serif",
                    fontWeight: 700,
                    fontSize: '16px',
                    flexShrink: 0
                  }}>
                    #{idx + 1}
                  </div>

                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                      <span style={{
                        fontFamily: "'Familjen Grotesk', sans-serif",
                        fontSize: '18px',
                        fontWeight: 700,
                        color: 'var(--color-olive-950, #1b1d16)'
                      }}>
                        {candidate.name}
                      </span>
                      <span style={{ fontSize: '13px', color: 'var(--color-olive-600, #5c624b)' }}>
                        • {candidate.current_title} @ {candidate.current_company} ({candidate.experience_years} yrs exp)
                      </span>
                      {candidate.interview_stub_id && (
                        <span style={{
                          fontSize: '11px',
                          padding: '2px 8px',
                          borderRadius: '9999px',
                          background: '#dcfce7',
                          color: '#15803d',
                          fontWeight: 700
                        }}>
                          ✓ Interview Stub: {candidate.interview_stub_id}
                        </span>
                      )}
                    </div>

                    {/* Tags */}
                    <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '6px' }}>
                      {candidate.tags.map(t => (
                        <span
                          key={t}
                          style={{
                            fontSize: '11px',
                            padding: '2px 8px',
                            borderRadius: '4px',
                            background: t.startsWith('KO:') ? '#fee2e2' : 'var(--color-olive-100, #fafbf8)',
                            color: t.startsWith('KO:') ? '#b91c1c' : 'var(--color-olive-800, #343729)',
                            border: t.startsWith('KO:') ? '1px solid #f87171' : '1px solid var(--color-olive-200, #e9ece0)',
                            fontWeight: t.startsWith('KO:') ? 700 : 500
                          }}
                        >
                          {t}
                        </span>
                      ))}
                      <span style={{ fontSize: '11px', color: 'var(--color-olive-500, #737a5f)', alignSelf: 'center', marginLeft: '4px' }}>
                        CV: {candidate.cv_filename}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Right score */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                  <div style={{
                    padding: '8px 16px',
                    borderRadius: '10px',
                    textAlign: 'center',
                    ...badgeStyle
                  }}>
                    <div style={{ fontSize: '22px', fontFamily: "'Familjen Grotesk', sans-serif", fontWeight: 700, lineHeight: '1' }}>
                      {candidate.overall_score}
                    </div>
                    <div style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.04em', fontWeight: 700, marginTop: '2px' }}>
                      {candidate.is_knockout ? 'KO Capped' : 'Fit Score'}
                    </div>
                  </div>
                </div>
              </div>

              {/* KO Alert Box */}
              {candidate.is_knockout && candidate.ko_reason && (
                <div style={{
                  marginTop: '12px',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  background: '#fef2f2',
                  border: '1px solid #fca5a5',
                  color: '#991b1b',
                  fontSize: '12.5px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span style={{ fontWeight: 700 }}>⚠️ Knock-Out Trigger:</span>
                  <span>{candidate.ko_reason}</span>
                </div>
              )}

              {/* Rubric Facet Pills */}
              <div style={{
                marginTop: '14px',
                paddingTop: '12px',
                borderTop: '1px solid var(--color-olive-200, #e9ece0)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '12px'
              }}>
                <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap', fontSize: '12px' }}>
                  <div style={{ color: 'var(--color-olive-700, #404434)' }}>
                    <span style={{ fontWeight: 600 }}>Skills:</span> {candidate.rubric?.skills?.score ?? 0}/35
                  </div>
                  <div style={{ color: 'var(--color-olive-700, #404434)' }}>
                    <span style={{ fontWeight: 600 }}>Exp:</span> {candidate.rubric?.experience?.score ?? 0}/30
                  </div>
                  <div style={{ color: 'var(--color-olive-700, #404434)' }}>
                    <span style={{ fontWeight: 600 }}>Impact:</span> {candidate.rubric?.project_impact?.score ?? 0}/20
                  </div>
                  <div style={{ color: 'var(--color-olive-700, #404434)' }}>
                    <span style={{ fontWeight: 600 }}>Edu:</span> {candidate.rubric?.education_certs?.score ?? 0}/5
                  </div>
                  <div style={{ color: 'var(--color-olive-700, #404434)' }}>
                    <span style={{ fontWeight: 600 }}>Clarity:</span> {candidate.rubric?.cv_clarity?.score ?? 0}/10
                  </div>
                </div>

                {/* Actions */}
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  {!candidate.interview_stub_id && (
                    <button
                      type="button"
                      disabled={schedulingId === candidate.id}
                      onClick={() => handleScheduleStub(candidate.id)}
                      style={{
                        padding: '6px 12px',
                        borderRadius: '6px',
                        border: '1px solid var(--color-olive-300, #d5dac9)',
                        background: 'transparent',
                        color: 'var(--color-olive-800, #343729)',
                        fontSize: '12px',
                        fontWeight: 600,
                        cursor: 'pointer'
                      }}
                    >
                      {schedulingId === candidate.id ? 'Scheduling...' : 'Schedule Interview (DB)'}
                    </button>
                  )}

                  <button
                    type="button"
                    onClick={() => onNavigate('candidate', candidate.id)}
                    style={{
                      padding: '6px 12px',
                      borderRadius: '6px',
                      border: 'none',
                      background: 'var(--color-olive-950, #1b1d16)',
                      color: '#fff',
                      fontSize: '12px',
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    View Evidence Dossier →
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
