import axios from 'axios'

// API Base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types for API responses
export interface Resume {
  id: number
  filename: string
  file_type: string
  file_size: number
  file_path: string
  upload_date: string
  processed_date?: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  extracted_text?: string
  structured_data?: any
  processing_errors?: any
  created_at: string
  updated_at: string
}

export interface JobDescription {
  id: number
  title: string
  company: string
  description: string
  source: string
  location?: string
  salary_range?: string
  employment_type?: string
  experience_level?: string
  scraped_date?: string
  processed_date?: string
  requirements?: string
  source_url?: string
  structured_data?: any
  extracted_skills?: any
  processing_errors?: any
  status: string
  created_at: string
  updated_at: string
}

export interface Candidate {
  id: number
  resume_id: number
  full_name?: string
  email?: string
  phone?: string
  location?: string
  linkedin_url?: string
  portfolio_url?: string
  years_experience?: number
  education_level?: string
  field_of_study?: string
  university?: string
  graduation_year?: number
  current_position?: string
  current_company?: string
  skills?: any
  work_history?: any
  education_history?: any
  certifications?: any
  languages?: any
  projects?: any
  achievements?: any
  summary?: string
  created_at: string
  updated_at: string
}

export interface Match {
  id: number
  resume_id: number
  job_id: number
  overall_score: number
  skills_score?: number
  experience_score?: number
  education_score?: number
  additional_score?: number
  matched_skills?: any
  missing_skills?: any
  skill_overlap_count?: number
  total_required_skills?: number
  explanation?: any
  confidence_level?: string
  recommendation?: string
  created_at: string
  updated_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// API Service Class
class ApiService {
  // Health check
  async health() {
    const response = await api.get('/health')
    return response.data
  }

  // Resume endpoints
  async uploadResume(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/api/v1/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }

  async bulkUploadResumes(files: File[]) {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })
    
    const response = await api.post('/api/v1/resumes/bulk-upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }

  async getResumes(params?: {
    skip?: number
    limit?: number
    status?: string
  }): Promise<PaginatedResponse<Resume>> {
    const response = await api.get('/api/v1/resumes/', { params })
    return response.data
  }

  async getResume(id: number): Promise<Resume> {
    const response = await api.get(`/api/v1/resumes/${id}`)
    return response.data
  }

  async getResumeStatus(id: number) {
    const response = await api.get(`/api/v1/resumes/${id}/status`)
    return response.data
  }

  async updateResume(id: number, data: Partial<Resume>) {
    const response = await api.put(`/api/v1/resumes/${id}`, data)
    return response.data
  }

  async deleteResume(id: number) {
    const response = await api.delete(`/api/v1/resumes/${id}`)
    return response.data
  }

  async reprocessResume(id: number) {
    const response = await api.post(`/api/v1/resumes/${id}/reprocess`)
    return response.data
  }

  async previewResumeData(id: number) {
    const response = await api.get(`/api/v1/resumes/${id}/preview`)
    return response.data
  }

  // Job endpoints
  async createJob(data: Partial<JobDescription>) {
    const response = await api.post('/api/v1/jobs/', data)
    return response.data
  }

  async getJobs(params?: {
    skip?: number
    limit?: number
    company?: string
    location?: string
    employment_type?: string
    experience_level?: string
    status?: string
  }): Promise<PaginatedResponse<JobDescription>> {
    const response = await api.get('/api/v1/jobs/', { params })
    return response.data
  }

  async getJob(id: number): Promise<JobDescription> {
    const response = await api.get(`/api/v1/jobs/${id}`)
    return response.data
  }

  async updateJob(id: number, data: Partial<JobDescription>) {
    const response = await api.put(`/api/v1/jobs/${id}`, data)
    return response.data
  }

  async deleteJob(id: number) {
    const response = await api.delete(`/api/v1/jobs/${id}`)
    return response.data
  }

  async scrapeJobs(urls: string[]) {
    const response = await api.post('/api/v1/jobs/scrape', { urls })
    return response.data
  }

  async searchJobsBySkills(skills: string, minMatches: number = 1) {
    const response = await api.get('/api/v1/jobs/search/skills', {
      params: { skills, min_matches: minMatches }
    })
    return response.data
  }

  async getJobSkills(id: number) {
    const response = await api.get(`/api/v1/jobs/${id}/skills`)
    return response.data
  }

  // Candidate endpoints
  async getCandidates(params?: {
    skip?: number
    limit?: number
  }): Promise<PaginatedResponse<Candidate>> {
    const response = await api.get('/api/v1/candidates/', { params })
    return response.data
  }

  async getCandidate(id: number): Promise<Candidate> {
    const response = await api.get(`/api/v1/candidates/${id}`)
    return response.data
  }

  async getCandidateResume(id: number) {
    const response = await api.get(`/api/v1/candidates/${id}/resume`)
    return response.data
  }

  async updateCandidate(id: number, data: Partial<Candidate>) {
    const response = await api.put(`/api/v1/candidates/${id}`, data)
    return response.data
  }

  async deleteCandidate(id: number) {
    const response = await api.delete(`/api/v1/candidates/${id}`)
    return response.data
  }

  async searchCandidatesBySkills(skills: string, minMatches: number = 1) {
    const response = await api.get('/api/v1/candidates/search/by-skills', {
      params: { skills, min_matches: minMatches }
    })
    return response.data
  }

  // Matching endpoints
  async createMatch(resumeId: number, jobId: number) {
    const response = await api.post('/api/v1/matching/match', {
      resume_id: resumeId,
      job_id: jobId
    })
    return response.data
  }

  async bulkMatch(data: {
    resume_ids: number[]
    job_ids: number[]
    min_score_threshold?: number
    include_explanations?: boolean
  }) {
    const response = await api.post('/api/v1/matching/bulk-match', data)
    return response.data
  }

  async getMatches(params?: {
    skip?: number
    limit?: number
    resume_id?: number
    job_id?: number
    min_score?: number
    max_score?: number
  }): Promise<PaginatedResponse<Match>> {
    const response = await api.get('/api/v1/matching/', { params })
    return response.data
  }

  async getMatch(id: number): Promise<Match> {
    const response = await api.get(`/api/v1/matching/${id}`)
    return response.data
  }

  async updateMatch(id: number, data: Partial<Match>) {
    const response = await api.put(`/api/v1/matching/${id}`, data)
    return response.data
  }

  async deleteMatch(id: number) {
    const response = await api.delete(`/api/v1/matching/${id}`)
    return response.data
  }

  async getMatchExplanation(id: number) {
    const response = await api.get(`/api/v1/matching/${id}/explanation`)
    return response.data
  }

  async getMatchingStats() {
    const response = await api.get('/api/v1/matching/stats')
    return response.data
  }

  async getTopMatches(params?: {
    limit?: number
    job_id?: number
    resume_id?: number
  }) {
    const response = await api.get('/api/v1/matching/top-matches', { params })
    return response.data
  }
}

export const apiService = new ApiService()
export default apiService
