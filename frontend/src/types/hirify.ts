export interface JobRequirement {
  id: string; // e.g., 'REQ-1'
  title: string;
  weight: number; // percentage in rubric
  description: string;
}

export interface Job {
  id: string;
  title: string;
  department: string;
  location: string;
  status: 'active' | 'draft' | 'closed';
  description: string;
  requirements: JobRequirement[];
  candidate_count: number;
  created_at: string;
}

export interface RubricItemScore {
  score: number;
  max: number;
  weight_percent: number;
  requirement_id: string;
  quote: string;
  reasoning: string;
}

export interface CandidateRubric {
  skills: RubricItemScore;
  experience: RubricItemScore;
  project_impact: RubricItemScore;
  education_certs: RubricItemScore;
  cv_clarity: RubricItemScore;
}

export interface Candidate {
  id: string;
  job_id: string;
  name: string;
  email: string;
  phone?: string;
  current_title: string;
  current_company: string;
  experience_years: number;
  overall_score: number; // 0-100
  is_knockout: boolean;
  ko_reason?: string;
  tags: string[];
  status: 'screened' | 'interview_scheduled' | 'shortlisted' | 'rejected' | 'pending';
  cv_filename: string;
  screened_at: string;
  interview_stub_id?: string;
  interview_notes?: string;
  rubric?: CandidateRubric;
  chunks_retrieved?: number;
}

export interface EvalBenchmarkResult {
  p_at_3: number;
  ndcg_at_5: number;
  spearman_rho: number;
  citation_faithfulness: number; // percentage, target 100%
  target_met: boolean;
  total_candidates: number;
  comparisons: Array<{
    candidate_id: string;
    candidate_name: string;
    ground_truth_rank: number;
    agent_rank: number;
    score: number;
    ko_status: boolean;
    citation_valid: boolean;
  }>;
  ai_usage: {
    model: string;
    prompt_hash: string;
    tool_schema_version: string;
    retrieval_top_k: number;
    rubric_weights: string;
    avg_latency_sec: number;
    est_cost: string;
  };
}
