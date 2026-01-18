import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Play, Users, FileText, Briefcase, TrendingUp, Target, ChevronDown, Filter, Download, RefreshCw } from 'lucide-react'
import apiService, { Resume, JobDescription, Match } from '../services/api'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select'
import { Progress } from './ui/progress'
import { AnimatedBarChart, AnimatedPieChart } from './ui/animated-chart'

interface MatchingStats {
  totalMatches: number
  averageScore: number
  highScoreMatches: number
  lowScoreMatches: number
}

const MatchingInterface: React.FC = () => {
  const [resumes, setResumes] = useState<Resume[]>([])
  const [jobs, setJobs] = useState<JobDescription[]>([])
  const [matches, setMatches] = useState<Match[]>([])
  const [selectedResumes, setSelectedResumes] = useState<number[]>([])
  const [selectedJobs, setSelectedJobs] = useState<number[]>([])
  const [loading, setLoading] = useState(false)
  const [matching, setMatching] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [minScoreThreshold, setMinScoreThreshold] = useState(0.5)
  const [matchingType, setMatchingType] = useState<'single' | 'bulk'>('single')
  const [selectedSingleResume, setSelectedSingleResume] = useState<number | null>(null)
  const [selectedSingleJob, setSelectedSingleJob] = useState<number | null>(null)
  const [stats, setStats] = useState<MatchingStats>({ totalMatches: 0, averageScore: 0, highScoreMatches: 0, lowScoreMatches: 0 })

  // Load data on component mount
  useEffect(() => {
    fetchData()
  }, [])

  // Calculate statistics
  useEffect(() => {
    if (matches.length > 0) {
      const totalMatches = matches.length
      const averageScore = matches.reduce((sum, match) => sum + match.overall_score, 0) / totalMatches
      const highScoreMatches = matches.filter(match => match.overall_score >= 0.8).length
      const lowScoreMatches = matches.filter(match => match.overall_score < 0.4).length
      
      setStats({ totalMatches, averageScore, highScoreMatches, lowScoreMatches })
    }
  }, [matches])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const [resumeResponse, jobResponse, matchResponse] = await Promise.all([
        apiService.getResumes({ limit: 100 }),
        apiService.getJobs({ limit: 100 }),
        apiService.getMatches({ limit: 100 })
      ])
      
      setResumes(resumeResponse.items.filter(r => r.status === 'completed'))
      setJobs(jobResponse.items)
      setMatches(matchResponse.items)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch data')
      console.error('Error fetching data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleResumeToggle = (resumeId: number) => {
    setSelectedResumes(prev => 
      prev.includes(resumeId) 
        ? prev.filter(id => id !== resumeId)
        : [...prev, resumeId]
    )
  }

  const handleJobToggle = (jobId: number) => {
    setSelectedJobs(prev => 
      prev.includes(jobId) 
        ? prev.filter(id => id !== jobId)
        : [...prev, jobId]
    )
  }

  const handleStartMatching = async () => {
    if (matchingType === 'single') {
      if (!selectedSingleResume || !selectedSingleJob) {
        setError('Please select both a resume and a job for single matching')
        return
      }
      await handleSingleMatch(selectedSingleResume, selectedSingleJob)
    } else {
      await handleBulkMatch()
    }
  }

  const handleSingleMatch = async (resumeId: number, jobId: number) => {
    try {
      setMatching(true)
      await apiService.createMatch(resumeId, jobId)
      await fetchData()
      setSelectedSingleResume(null)
      setSelectedSingleJob(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create match')
    } finally {
      setMatching(false)
    }
  }

  const handleBulkMatch = async () => {
    if (selectedResumes.length === 0 || selectedJobs.length === 0) {
      setError('Please select at least one resume and one job')
      return
    }

    try {
      setMatching(true)
      await apiService.bulkMatch({
        resume_ids: selectedResumes,
        job_ids: selectedJobs,
        min_score_threshold: minScoreThreshold,
        include_explanations: true
      })
      
      setSelectedResumes([])
      setSelectedJobs([])
      await fetchData()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to perform bulk matching')
    } finally {
      setMatching(false)
    }
  }

  const handleDeleteMatch = async (matchId: number, e?: React.MouseEvent) => {
    e?.stopPropagation()
    if (!confirm('Are you sure you want to delete this match?')) return
    
    try {
      console.log('Deleting match:', matchId)
      await apiService.deleteMatch(matchId)
      console.log('Match deleted successfully')
      await fetchData()
    } catch (err: any) {
      console.error('Delete error:', err)
      setError(err.response?.data?.detail || 'Failed to delete match')
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-100'
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-100'
    if (score >= 0.4) return 'text-orange-600 bg-orange-100'
    return 'text-red-600 bg-red-100'
  }

  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'high': return 'text-green-600 bg-green-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      case 'low': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  // Generate chart data for a specific match
  const getMatchChartData = (match: Match) => {
    if (!match) return []
    
    const chartData = [
      {
        name: 'Skills',
        userScore: match.skills_score ? (match.skills_score * 100) : 0,
        targetScore: 100, // Target is always 100% for comparison
        weight: 40,
        color: '#8884d8'
      },
      {
        name: 'Experience',
        userScore: match.experience_score ? (match.experience_score * 100) : 0,
        targetScore: 100,
        weight: 30,
        color: '#82ca9d'
      },
      {
        name: 'Education',
        userScore: match.education_score ? (match.education_score * 100) : 0,
        targetScore: 100,
        weight: 20,
        color: '#ffc658'
      },
      {
        name: 'Overall',
        userScore: match.overall_score ? (match.overall_score * 100) : 0,
        targetScore: 100,
        weight: 100,
        color: '#ff7c7c'
      }
    ]
    return chartData.filter(item => item.userScore >= 0 || item.targetScore > 0)
  }

  // Generate pie chart data for match breakdown
  const getMatchPieData = (match: Match) => {
    if (!match) return []
    
    const pieData = []
    
    if (match.skills_score) {
      pieData.push({
        name: 'Skills Match',
        value: match.skills_score * 40, // Weight: 40%
        color: '#8884d8'
      })
    }
    
    if (match.experience_score) {
      pieData.push({
        name: 'Experience Match',
        value: match.experience_score * 30, // Weight: 30%
        color: '#82ca9d'
      })
    }
    
    if (match.education_score) {
      pieData.push({
        name: 'Education Match',
        value: match.education_score * 20, // Weight: 20%
        color: '#ffc658'
      })
    }
    
    // Add remaining factors
    const remainingScore = match.overall_score ? (match.overall_score * 100) - (pieData.reduce((sum, item) => sum + item.value, 0)) : 0
    if (remainingScore > 0) {
      pieData.push({
        name: 'Other Factors',
        value: remainingScore,
        color: '#ff7c7c'
      })
    }
    
    return pieData.length > 0 ? pieData : [{ name: 'No Data', value: 1, color: '#gray' }]
  }

  return (
    <motion.div className="space-y-6">
      {/* Main Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">Resume Matching</h1>
        <p className="text-gray-600 mb-4">
          Intelligently match resumes with job descriptions using AI-powered analysis.
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Matches</CardTitle>
            <Target className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalMatches}</div>
            <p className="text-xs text-gray-500">Active matching results</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(stats.averageScore * 100).toFixed(1)}%</div>
            <p className="text-xs text-gray-500">Overall performance</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">High Score Matches</CardTitle>
            <Users className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-emerald-600">{stats.highScoreMatches}</div>
            <p className="text-xs text-gray-500">≥80% match rate</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Available Data</CardTitle>
            <FileText className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{resumes.length}/{jobs.length}</div>
            <p className="text-xs text-gray-500">Resumes / Jobs</p>
          </CardContent>
        </Card>
      </div>

      {/* Matching Interface */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            AI-Powered Resume Matching
          </CardTitle>
          <CardDescription>
            Intelligently match resumes with job descriptions.
          </CardDescription>
          <div className="flex items-center space-x-4">
            <Select onValueChange={(value) => setMatchingType(value as 'single' | 'bulk')} value={matchingType}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select Match Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="single">Single Match</SelectItem>
                <SelectItem value="bulk">Bulk Match</SelectItem>
              </SelectContent>
            </Select>
            <Button
              onClick={handleStartMatching}
              disabled={resumes.length === 0 || jobs.length === 0 || matching}
              className="bg-blue-500 text-white rounded-lg"
            >
              {matching ? 'Matching...' : 'Start Matching'}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700">{error}</p>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setError(null)}
                className="mt-2 text-red-600 hover:text-red-800"
              >
                Dismiss
              </Button>
            </div>
          )}
        
        {/* Selection UI - Different for Single vs Bulk */}
        {matchingType === 'single' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Single Match - Dropdown Selection */}
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Select Resume</h3>
              {loading ? (
                <div className="text-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto"></div>
                </div>
              ) : resumes.length === 0 ? (
                <div className="text-gray-500 text-center py-8">
                  <p>No processed resumes available for matching</p>
                </div>
              ) : (
                <Select onValueChange={(value) => setSelectedSingleResume(parseInt(value))} value={selectedSingleResume?.toString()}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Choose a resume..." />
                  </SelectTrigger>
                  <SelectContent>
                    {resumes.map((resume) => (
                      <SelectItem key={resume.id} value={resume.id.toString()}>
                        {resume.filename}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            </div>
            
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Select Job Description</h3>
              {loading ? (
                <div className="text-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto"></div>
                </div>
              ) : jobs.length === 0 ? (
                <div className="text-gray-500 text-center py-8">
                  <p>No job descriptions available for matching</p>
                </div>
              ) : (
                <Select onValueChange={(value) => setSelectedSingleJob(parseInt(value))} value={selectedSingleJob?.toString()}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Choose a job..." />
                  </SelectTrigger>
                  <SelectContent>
                    {jobs.map((job) => (
                      <SelectItem key={job.id} value={job.id.toString()}>
                        {job.title} - {job.company}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Bulk Match - Checklist Selection */}
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Select Resumes</h3>
              {loading ? (
                <div className="text-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto"></div>
                </div>
              ) : resumes.length === 0 ? (
                <div className="text-gray-500 text-center py-8">
                  <p>No processed resumes available for matching</p>
                </div>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {resumes.map((resume) => (
                    <label key={resume.id} className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 p-2 rounded">
                      <input
                        type="checkbox"
                        checked={selectedResumes.includes(resume.id)}
                        onChange={() => handleResumeToggle(resume.id)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700">{resume.filename}</span>
                    </label>
                  ))}
                </div>
              )}
              <div className="mt-2 text-sm text-gray-600">
                {selectedResumes.length} resume(s) selected
              </div>
            </div>
            
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Select Job Descriptions</h3>
              {loading ? (
                <div className="text-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto"></div>
                </div>
              ) : jobs.length === 0 ? (
                <div className="text-gray-500 text-center py-8">
                  <p>No job descriptions available for matching</p>
                </div>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {jobs.map((job) => (
                    <label key={job.id} className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 p-2 rounded">
                      <input
                        type="checkbox"
                        checked={selectedJobs.includes(job.id)}
                        onChange={() => handleJobToggle(job.id)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <div className="flex-1 text-sm">
                        <div className="text-gray-700 font-medium">{job.title}</div>
                        <div className="text-gray-500">{job.company}</div>
                      </div>
                    </label>
                  ))}
                </div>
              )}
              <div className="mt-2 text-sm text-gray-600">
                {selectedJobs.length} job(s) selected
              </div>
            </div>
          </div>
        )}
        
        {/* Matching Controls */}
        {matchingType === 'bulk' && (
          <div className="mt-6 space-y-4">
            <div className="flex items-center space-x-4">
              <label className="text-sm font-medium text-gray-700">
                Minimum Score Threshold:
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={minScoreThreshold}
                onChange={(e) => setMinScoreThreshold(parseFloat(e.target.value))}
                className="flex-1 max-w-xs"
              />
              <span className="text-sm text-gray-600">{minScoreThreshold.toFixed(1)}</span>
            </div>
          </div>
        )}

        </CardContent>
      </Card>

      {/* Matching Criteria */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">
            Matching Criteria
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm text-gray-700">
          <p>Our matching process considers the following criteria:</p>
          <ul className="list-disc list-inside space-y-1">
            <li><strong>Skills:</strong> 40% weight - Matches candidate skills with job requirements.</li>
            <li><strong>Experience:</strong> 30% weight - Considers relevant years of experience and domain experience.</li>
            <li><strong>Education:</strong> 20% weight - Evaluates education level and field of study matching.</li>
            <li><strong>Other Factors:</strong> 10% weight - Includes certifications, keywords, and location.</li>
          </ul>
        </CardContent>
      </Card>

      {/* Match Results */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Match Results</h2>
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading matches...</p>
          </div>
        ) : matches.length === 0 ? (
          <div className="text-gray-500 text-center py-8">
            <p>No matches found. Upload resumes and job descriptions to start matching!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {matches.map((match) => {
              const resume = resumes.find(r => r.id === match.resume_id)
              const job = jobs.find(j => j.id === match.job_id)
              return (
                <div key={match.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-2">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-800">
                            {resume?.filename || 'Unknown Resume'}
                          </h3>
                          <p className="text-sm text-gray-600">
                            {job?.title || 'Unknown Job'} at {job?.company || 'Unknown Company'}
                          </p>
                        </div>

                        {/* Overall Score */}
                        <div className="flex items-center space-x-2">
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(match.overall_score)}`}>
                            {(match.overall_score * 100).toFixed(1)}%
                          </span>
                          {match.confidence_level && (
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(match.confidence_level)}`}>
                              {match.confidence_level}
                            </span>
                          )}
                        </div>
                      </div>


                      {/* Recommendations */}
                      {match.recommendation && (
                        <div className="mb-4 text-sm text-gray-700">
                          <strong>Recommendation:</strong> {match.recommendation}
                        </div>
                      )}

                      {/* Date Created */}
                      <div className="mb-2 text-xs text-gray-500">
                        Created: {new Date(match.created_at).toLocaleString()}
                      </div>
                    </div>

                    {/* Action Button */}
                    <div>
                      <button
                        onClick={(e) => handleDeleteMatch(match.id, e)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </div>

                  {/* Functional Chart for Matching Analysis */}
                  {match && (
                    <div className="mt-4 grid grid-cols-1 lg:grid-cols-2 gap-4">
                      <AnimatedBarChart
                        data={getMatchChartData(match)}
                        title="Matching Scores by Category"
                        height={200}
                        colors={['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c']}
                        className="col-span-1"
                      />
                      <AnimatedPieChart
                        data={getMatchPieData(match)}
                        title="Match Distribution"
                        height={200}
                        colors={['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c']}
                        className="col-span-1"
                      />
                    </div>
                  )}
                  
                  {/* Detailed Analysis */}
                  <div className="mt-4 bg-blue-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-blue-900 mb-2">Matching Analysis</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-blue-800">
                          <strong>Strengths:</strong> 
                          {match.skills_score && match.skills_score >= 0.7 ? ' Strong skills match' : ''}
                          {match.experience_score && match.experience_score >= 0.7 ? ', Good experience level' : ''}
                          {match.education_score && match.education_score >= 0.7 ? ', Education requirement met' : ''}
                        </p>
                        {match.skill_overlap_count !== undefined && (
                          <p className="text-blue-800 mt-1">
                            <strong>Skills Overlap:</strong> {match.skill_overlap_count} out of {match.total_required_skills} required skills
                          </p>
                        )}
                      </div>
                      <div>
                        <p className="text-blue-800">
                          <strong>Areas for Improvement:</strong> 
                          {match.skills_score && match.skills_score < 0.5 ? ' Skills development needed' : ''}
                          {match.experience_score && match.experience_score < 0.5 ? ', More experience required' : ''}
                          {match.education_score && match.education_score < 0.5 ? ', Education gap identified' : ''}
                        </p>
                        {match.confidence_level && (
                          <p className="text-blue-800 mt-1">
                            <strong>Confidence Level:</strong> {match.confidence_level.charAt(0).toUpperCase() + match.confidence_level.slice(1)}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </motion.div>
  )
}

export default MatchingInterface
