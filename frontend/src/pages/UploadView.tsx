import React, { useState } from 'react';
import { HirifyAPI } from '../services/api';

interface UploadViewProps {
  onNavigate: (page: string) => void;
}

interface ReqItem {
  id: string;
  category: string;
  weight: number;
  text: string;
  isKnockout: boolean;
}

interface UploadedFile {
  id: string;
  name: string;
  size: string;
  status: 'parsing' | 'chunked' | 'embedded' | 'ready';
  chunks: number;
  tokens: number;
}

export const UploadView: React.FC<UploadViewProps> = ({ onNavigate }) => {
  const [jobTitle, setJobTitle] = useState('Senior Backend AI / Systems Engineer');
  const [department, setDepartment] = useState('Core Agent Infrastructure');
  const [location, setLocation] = useState('Remote (US/EU)');
  const [requirements, setRequirements] = useState<ReqItem[]>([
    { id: 'REQ-1', category: 'Skills', weight: 35, text: '5+ years Python / FastAPI / AsyncIO production services', isKnockout: true },
    { id: 'REQ-2', category: 'Experience', weight: 30, text: 'PostgreSQL + pgvector or vector DB at scale, index tuning', isKnockout: false },
    { id: 'REQ-3', category: 'Project Impact', weight: 20, text: 'Production LLM evaluation, RAG pipelines, or autonomous agent tool loops', isKnockout: false },
    { id: 'REQ-4', category: 'Education & Certs', weight: 5, text: 'B.S./M.S. in Computer Science or demonstrated equivalent', isKnockout: false },
    { id: 'REQ-5', category: 'CV Clarity & Compliance', weight: 10, text: 'Verifiable US/EU work authorization (ADR-0005: Missing = Hard KO capped ≤40)', isKnockout: true }
  ]);

  const [files, setFiles] = useState<UploadedFile[]>([
    { id: 'f-1', name: 'marcus_vance_staff_swe.pdf', size: '248 KB', status: 'ready', chunks: 14, tokens: 4920 },
    { id: 'f-2', name: 'elena_rostova_senior_ai.pdf', size: '312 KB', status: 'ready', chunks: 16, tokens: 5680 },
    { id: 'f-3', name: 'david_chen_mlops_lead.pdf', size: '198 KB', status: 'ready', chunks: 12, tokens: 4210 },
    { id: 'f-4', name: 'chloe_dubois_backend_fr.pdf', size: '275 KB', status: 'ready', chunks: 15, tokens: 5120 },
    { id: 'f-5', name: 'tariq_almansoor_junior_dev.pdf', size: '164 KB', status: 'ready', chunks: 8, tokens: 2840 }
  ]);

  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStage, setProcessingStage] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const newFiles: UploadedFile[] = Array.from(e.target.files).map((f, i) => ({
      id: `f-${Date.now()}-${i}`,
      name: f.name,
      size: `${Math.round(f.size / 1024)} KB`,
      status: 'ready',
      chunks: Math.floor(10 + Math.random() * 8),
      tokens: Math.floor(3000 + Math.random() * 3000)
    }));
    setFiles(prev => [...prev, ...newFiles]);
  };

  const handleRunScreening = async () => {
    setIsProcessing(true);
    setProcessingStage('Chunking documents into ~350-token windows with 50-token overlap...');
    await new Promise(r => setTimeout(r, 600));

    setProcessingStage('Generating 384-dimensional embeddings (sentence-transformers MiniLM-L6-v2)...');
    await new Promise(r => setTimeout(r, 700));

    setProcessingStage('Executing RAG similarity retrieval & Qwen 3.8-Max scoring loop...');
    await new Promise(r => setTimeout(r, 800));

    setProcessingStage('Verifying verbatim resume citations & applying KO score caps (≤40)...');
    await new Promise(r => setTimeout(r, 600));

    await HirifyAPI.triggerScreening('job-1');
    setIsProcessing(false);
    onNavigate('ranking');
  };

  return (
    <div className="oatmeal-page" style={{ padding: '40px 24px', maxWidth: '1180px', margin: '0 auto' }}>
      {/* Top Banner */}
      <div style={{ marginBottom: '32px' }}>
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
            Step 1 of 3: Requisition & Ingest
          </span>
          <span style={{ fontSize: '12px', color: 'var(--color-olive-600, #5c624b)' }}>• ADR-0004 Compliant</span>
        </div>
        <h1 style={{
          fontFamily: "'Familjen Grotesk', sans-serif",
          fontSize: '36px',
          fontWeight: 700,
          letterSpacing: '-0.02em',
          color: 'var(--color-olive-950, #1b1d16)',
          margin: 0
        }}>
          Upload Job Requisition & Resumes
        </h1>
        <p style={{
          fontSize: '15px',
          color: 'var(--color-olive-700, #404434)',
          maxWidth: '740px',
          marginTop: '8px',
          lineHeight: '1.5'
        }}>
          Define weighted evaluation criteria (<code style={{ background: 'var(--color-olive-200, #e9ece0)', padding: '2px 6px', borderRadius: '4px', fontSize: '13px' }}>REQ-1..5</code>) and batch-upload candidate resumes for local MiniLM chunking and autonomous LLM screening.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '28px' }}>
        {/* Left Column: Job Description & Criteria */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Requisition Card */}
          <div style={{
            background: 'var(--color-olive-50, #ffffff)',
            border: '1px solid var(--color-olive-200, #e9ece0)',
            borderRadius: '16px',
            padding: '24px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.03)'
          }}>
            <h2 style={{
              fontFamily: "'Familjen Grotesk', sans-serif",
              fontSize: '18px',
              fontWeight: 700,
              color: 'var(--color-olive-950, #1b1d16)',
              marginTop: 0,
              marginBottom: '16px'
            }}>
              Role Specification
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--color-olive-700, #404434)', marginBottom: '4px' }}>
                  Job Title
                </label>
                <input
                  type="text"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    border: '1px solid var(--color-olive-300, #d5dac9)',
                    background: 'var(--color-olive-100, #fafbf8)',
                    fontSize: '14px',
                    color: 'var(--color-olive-950, #1b1d16)',
                    outline: 'none',
                    boxSizing: 'border-box'
                  }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--color-olive-700, #404434)', marginBottom: '4px' }}>
                    Department
                  </label>
                  <input
                    type="text"
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '10px 14px',
                      borderRadius: '8px',
                      border: '1px solid var(--color-olive-300, #d5dac9)',
                      background: 'var(--color-olive-100, #fafbf8)',
                      fontSize: '14px',
                      color: 'var(--color-olive-950, #1b1d16)',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--color-olive-700, #404434)', marginBottom: '4px' }}>
                    Location
                  </label>
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '10px 14px',
                      borderRadius: '8px',
                      border: '1px solid var(--color-olive-300, #d5dac9)',
                      background: 'var(--color-olive-100, #fafbf8)',
                      fontSize: '14px',
                      color: 'var(--color-olive-950, #1b1d16)',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Rubric Criteria Breakdown */}
          <div style={{
            background: 'var(--color-olive-50, #ffffff)',
            border: '1px solid var(--color-olive-200, #e9ece0)',
            borderRadius: '16px',
            padding: '24px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.03)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <h2 style={{
                fontFamily: "'Familjen Grotesk', sans-serif",
                fontSize: '18px',
                fontWeight: 700,
                color: 'var(--color-olive-950, #1b1d16)',
                margin: 0
              }}>
                Weighted Rubric Facets (<code style={{ fontSize: '13px' }}>config/rubric.yaml</code>)
              </h2>
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#15803d', background: '#dcfce7', padding: '2px 8px', borderRadius: '9999px' }}>
                Total 100%
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {requirements.map((req) => (
                <div key={req.id} style={{
                  padding: '12px 14px',
                  borderRadius: '10px',
                  border: '1px solid var(--color-olive-200, #e9ece0)',
                  background: 'var(--color-olive-100, #fafbf8)',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '12px'
                }}>
                  <div style={{
                    padding: '4px 8px',
                    borderRadius: '6px',
                    background: 'var(--color-olive-900, #2b2e21)',
                    color: '#fff',
                    fontFamily: 'monospace',
                    fontSize: '11px',
                    fontWeight: 700,
                    whiteSpace: 'nowrap'
                  }}>
                    {req.id}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2px' }}>
                      <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-olive-900, #2b2e21)' }}>
                        {req.category}
                      </span>
                      <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                        {req.isKnockout && (
                          <span style={{ fontSize: '10px', background: '#fee2e2', color: '#b91c1c', padding: '1px 6px', borderRadius: '4px', fontWeight: 600 }}>
                            KO Rule
                          </span>
                        )}
                        <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-olive-700, #404434)' }}>
                          {req.weight}%
                        </span>
                      </div>
                    </div>
                    <div style={{ fontSize: '13px', color: 'var(--color-olive-800, #343729)', lineHeight: '1.4' }}>
                      {req.text}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Resumes & Screening Ingest */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* File Upload Zone */}
          <div style={{
            background: 'var(--color-olive-50, #ffffff)',
            border: '1px solid var(--color-olive-200, #e9ece0)',
            borderRadius: '16px',
            padding: '24px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.03)'
          }}>
            <h2 style={{
              fontFamily: "'Familjen Grotesk', sans-serif",
              fontSize: '18px',
              fontWeight: 700,
              color: 'var(--color-olive-950, #1b1d16)',
              marginTop: 0,
              marginBottom: '14px'
            }}>
              Batch Resume Ingestion
            </h2>

            {/* Dropzone */}
            <label
              onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
              onDragLeave={() => setIsDragOver(false)}
              onDrop={(e) => {
                e.preventDefault();
                setIsDragOver(false);
                if (e.dataTransfer.files) {
                  const newFiles: UploadedFile[] = Array.from(e.dataTransfer.files).map((f, i) => ({
                    id: `f-${Date.now()}-${i}`,
                    name: f.name,
                    size: `${Math.round(f.size / 1024)} KB`,
                    status: 'ready',
                    chunks: Math.floor(10 + Math.random() * 8),
                    tokens: Math.floor(3000 + Math.random() * 3000)
                  }));
                  setFiles(prev => [...prev, ...newFiles]);
                }
              }}
              style={{
                display: 'block',
                border: isDragOver ? '2px dashed var(--color-olive-700, #404434)' : '2px dashed var(--color-olive-300, #d5dac9)',
                borderRadius: '12px',
                padding: '28px 16px',
                textAlign: 'center',
                background: isDragOver ? 'var(--color-olive-200, #e9ece0)' : 'var(--color-olive-100, #fafbf8)',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              <input type="file" multiple accept=".pdf,.docx,.txt" onChange={handleFileUpload} style={{ display: 'none' }} />
              <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '10px' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  background: 'var(--color-olive-200, #e9ece0)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--color-olive-900, #2b2e21)'
                }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                </div>
              </div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--color-olive-950, #1b1d16)' }}>
                Click to upload or drag resumes here
              </div>
              <div style={{ fontSize: '12px', color: 'var(--color-olive-600, #5c624b)', marginTop: '4px' }}>
                PDF, DOCX, TXT • Auto-chunked into ~350-token windows
              </div>
            </label>

            {/* Ingested List */}
            <div style={{ marginTop: '18px' }}>
              <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-olive-600, #5c624b)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>
                Resumes Queued ({files.length})
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '240px', overflowY: 'auto' }}>
                {files.map((file) => (
                  <div key={file.id} style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '8px 12px',
                    borderRadius: '8px',
                    background: 'var(--color-olive-100, #fafbf8)',
                    border: '1px solid var(--color-olive-200, #e9ece0)',
                    fontSize: '12.5px'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0 }}>
                      <span style={{ color: 'var(--color-olive-500, #737a5f)' }}>📄</span>
                      <span style={{ fontWeight: 600, color: 'var(--color-olive-900, #2b2e21)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '170px' }}>
                        {file.name}
                      </span>
                      <span style={{ color: 'var(--color-olive-500, #737a5f)', fontSize: '11px' }}>({file.size})</span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{
                        fontSize: '10.5px',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        background: '#dcfce7',
                        color: '#15803d',
                        fontWeight: 600
                      }}>
                        {file.chunks} Chunks
                      </span>
                      <span style={{
                        fontSize: '10.5px',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        background: 'var(--color-olive-200, #e9ece0)',
                        color: 'var(--color-olive-800, #343729)',
                        fontWeight: 600
                      }}>
                        MiniLM-384
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Screening Trigger Action */}
          <div style={{
            background: 'var(--color-olive-900, #2b2e21)',
            color: '#ffffff',
            borderRadius: '16px',
            padding: '24px',
            boxShadow: '0 8px 24px rgba(43,46,33,0.2)'
          }}>
            <h3 style={{
              fontFamily: "'Familjen Grotesk', sans-serif",
              fontSize: '18px',
              fontWeight: 700,
              marginTop: 0,
              marginBottom: '8px'
            }}>
              Autonomous Screening Agent
            </h3>
            <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.8)', lineHeight: '1.4', margin: '0 0 16px 0' }}>
              Qwen 3.8-Max will retrieve relevant chunks per requirement, verify quote citations, enforce knockout rules, and generate ranking.
            </p>

            {isProcessing ? (
              <div style={{
                padding: '14px',
                borderRadius: '8px',
                background: 'rgba(255,255,255,0.1)',
                border: '1px solid rgba(255,255,255,0.2)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <div style={{
                    width: '14px',
                    height: '14px',
                    border: '2px solid rgba(255,255,255,0.3)',
                    borderTopColor: '#fff',
                    borderRadius: '50%',
                    animation: 'spin 0.8s linear infinite'
                  }} />
                  <span style={{ fontSize: '13px', fontWeight: 600 }}>Screening in progress...</span>
                </div>
                <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.85)', fontFamily: 'monospace' }}>
                  {processingStage}
                </div>
              </div>
            ) : (
              <button
                type="button"
                onClick={handleRunScreening}
                style={{
                  width: '100%',
                  padding: '12px 18px',
                  borderRadius: '9999px',
                  background: 'var(--color-olive-100, #fafbf8)',
                  color: 'var(--color-olive-950, #1b1d16)',
                  border: 'none',
                  fontSize: '14px',
                  fontWeight: 700,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  transition: 'all 0.15s ease'
                }}
              >
                <span>⚡ Run Screening on {files.length} Candidates</span>
                <span>→</span>
              </button>
            )}

            <div style={{ marginTop: '12px', fontSize: '11px', color: 'rgba(255,255,255,0.6)', textAlign: 'center' }}>
              Target: NDCG@5 ≥ 0.75 • 100% Citation Faithfulness • KO Cap ≤40
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
