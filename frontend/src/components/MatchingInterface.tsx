import React, { useMemo, useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Users, FileText, TrendingUp, Target, AlertCircle } from 'lucide-react'
import apiService, { Resume, JobDescription, Match } from '../services/api'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select'
import { Alert, AlertDescription } from './ui/alert'
import { AnimatedBarChart, AnimatedPieChart } from './ui/animated-chart'
import { useToast } from './ui/toast'
import { useDeleteFlow } from '../hooks/use-delete-flow'
import ConfirmDialog from './ui/confirm-dialog'

interface MatchingStats {
  totalMatches: number
  averageScore: number
  highScoreMatches: number
  lowScoreMatches: number
}

const SCORE_VARIANT_MAP: Record<string, 'default' | 'secondary' | 'destructive' | 'outline' | 'ghost'> = {
  high: 'default',
  medium: 'secondary',
  low: 'outline',
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
  const { addToast } = useToast()
  const {
    pendingDelete: matchPendingDelete,
    deleting: deletingMatch,
    requestDelete: requestDeleteMatch,
    cancelDelete: cancelDeleteMatch,
    handleDelete: handleDeleteMatch,
  } = useDeleteFlow<Match>({
    deleteFn: (id) => apiService.deleteMatch(id),
    itemLabel: 'Match',
    onDeleted: (id) => setMatches((prev) => prev.filter((m) => m.id !== id)),
    getDescription: (item) => `Match #${item.id}`,
  })

  useEffect(() => {
    fetchData()
  }, [])

  const stats = useMemo<MatchingStats>(() => {
    if (matches.length === 0) {
      return { totalMatches: 0, averageScore: 0, highScoreMatches: 0, lowScoreMatches: 0 }
    }

    const totalMatches = matches.length
    const averageScore =
      matches.reduce((sum, match) => sum + match.overall_score, 0) / totalMatches
    const highScoreMatches = matches.filter((match) => match.overall_score >= 0.8).length
    const lowScoreMatches = matches.filter((match) => match.overall_score < 0.4).length

    return { totalMatches, averageScore, highScoreMatches, lowScoreMatches }
  }, [matches])

  const fetchData = async (withLoader = true) => {
    try {
      if (withLoader) setLoading(true)
      setError(null)

      const [resumeResponse, jobResponse, matchResponse] = await Promise.all([
        apiService.getResumes({ limit: 100 }),
        apiService.getJobs({ limit: 100 }),
        apiService.getMatches({ limit: 100 }),
      ])

      setResumes(resumeResponse.items.filter((r) => r.status === 'completed'))
      setJobs(jobResponse.items)
      setMatches(matchResponse.items)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch data')
      console.error('Error fetching data:', err)
    } finally {
      if (withLoader) setLoading(false)
    }
  }

  const handleResumeToggle = (resumeId: number) => {
    setSelectedResumes((prev) =>
      prev.includes(resumeId) ? prev.filter((id) => id !== resumeId) : [...prev, resumeId],
    )
  }

  const handleJobToggle = (jobId: number) => {
    setSelectedJobs((prev) =>
      prev.includes(jobId) ? prev.filter((id) => id !== jobId) : [...prev, jobId],
    )
  }

  const handleStartMatching = async () => {
    if (matchingType === 'single') {
      if (selectedSingleResume === null || selectedSingleJob === null) {
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
      await fetchData(false)
      setSelectedSingleResume(null)
      setSelectedSingleJob(null)
      addToast({
        type: 'success',
        title: 'Match created',
        description: 'The new match has been added to your results.',
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create match')
      addToast({
        type: 'error',
        title: 'Match failed',
        description: err.response?.data?.detail || 'Failed to create match',
      })
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
        include_explanations: true,
      })

      setSelectedResumes([])
      setSelectedJobs([])
      await fetchData(false)
      addToast({
        type: 'success',
        title: 'Bulk matching complete',
        description: 'Match results were refreshed successfully.',
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to perform bulk matching')
      addToast({
        type: 'error',
        title: 'Bulk matching failed',
        description: err.response?.data?.detail || 'Failed to perform bulk matching',
      })
    } finally {
      setMatching(false)
    }
  }



  const getScoreColorClass = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-100'
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-100'
    if (score >= 0.4) return 'text-orange-600 bg-orange-100'
    return 'text-red-600 bg-red-100'
  }

  const getMatchChartData = (match: Match) => {
    if (!match) return []

    return [
      {
        name: 'Skills',
        userScore: match.skills_score ? match.skills_score * 100 : 0,
        targetScore: 100,
        color: '#8884d8',
      },
      {
        name: 'Experience',
        userScore: match.experience_score ? match.experience_score * 100 : 0,
        targetScore: 100,
        color: '#82ca9d',
      },
      {
        name: 'Education',
        userScore: match.education_score ? match.education_score * 100 : 0,
        targetScore: 100,
        color: '#ffc658',
      },
      {
        name: 'Overall',
        userScore: match.overall_score ? match.overall_score * 100 : 0,
        targetScore: 100,
        color: '#ff7c7c',
      },
    ]
  }

  const getMatchPieData = (match: Match) => {
    if (!match) return []

    const pieData = []
    if (match.skills_score) {
      pieData.push({ name: 'Skills Match', value: match.skills_score * 40, color: '#8884d8' })
    }
    if (match.experience_score) {
      pieData.push({
        name: 'Experience Match',
        value: match.experience_score * 30,
        color: '#82ca9d',
      })
    }
    if (match.education_score) {
      pieData.push({
        name: 'Education Match',
        value: match.education_score * 20,
        color: '#ffc658',
      })
    }
    const remainingScore = match.overall_score
      ? match.overall_score * 100 - pieData.reduce((sum, item) => sum + item.value, 0)
      : 0
    if (remainingScore > 0) {
      pieData.push({ name: 'Other Factors', value: remainingScore, color: '#ff7c7c' })
    }

    return pieData.length > 0 ? pieData : [{ name: 'No Data', value: 1, color: '#94A3B8' }]
  }

  const selectedResumeOption = selectedSingleResume
    ? resumes.find((r) => r.id === selectedSingleResume)
    : null
  const selectedJobOption = selectedSingleJob
    ? jobs.find((j) => j.id === selectedSingleJob)
    : null

  const selectedResumeValue = selectedResumeOption
    ? selectedResumeOption.id.toString()
    : undefined
  const selectedJobValue = selectedJobOption ? selectedJobOption.id.toString() : undefined

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-4 md:space-y-6"
    >
      {/* Header */}
      <div className="rounded-lg border border-border/60 bg-card/95 p-5 shadow-sm md:p-6">
        <h1 className="mb-4 text-2xl font-bold">Resume Matching</h1>
        <p className="text-muted-foreground">
          Intelligently match resumes with job descriptions using AI-powered analysis.
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Card className="border-border/60 bg-card/95 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Matches</CardTitle>
            <Target className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalMatches}</div>
            <p className="text-xs text-muted-foreground">Active matching results</p>
          </CardContent>
        </Card>

        <Card className="border-border/60 bg-card/95 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(stats.averageScore * 100).toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">Overall performance</p>
          </CardContent>
        </Card>

        <Card className="border-border/60 bg-card/95 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">High Score Matches</CardTitle>
            <Users className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-emerald-600">
              {stats.highScoreMatches}
            </div>
            <p className="text-xs text-muted-foreground">≥80% match rate</p>
          </CardContent>
        </Card>

        <Card className="border-border/60 bg-card/95 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Available Data</CardTitle>
            <FileText className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {resumes.length}/{jobs.length}
            </div>
            <p className="text-xs text-muted-foreground">Resumes / Jobs</p>
          </CardContent>
        </Card>
      </div>

      {/* Matching Interface */}
      <Card className="border-border/60 bg-card/95 shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            AI-Powered Resume Matching
          </CardTitle>
          <CardDescription>
            Intelligently match resumes with job descriptions.
          </CardDescription>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <Select
              onValueChange={(value) => setMatchingType(value as 'single' | 'bulk')}
              value={matchingType}
            >
              <SelectTrigger className="w-full sm:w-56">
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
              variant="info"
              className="w-full sm:w-auto"
            >
              {matching ? 'Matching...' : 'Start Matching'}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-3.5 w-3.5" />
              <AlertDescription className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <span>{error}</span>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => setError(null)}
                  className="w-full sm:w-auto"
                >
                  Dismiss
                </Button>
              </AlertDescription>
            </Alert>
          )}

          {/* Selection UI */}
          {matchingType === 'single' ? (
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <div className="rounded-lg border border-border/60 p-4">
                <h3 className="mb-2 text-lg font-semibold">Select Resume</h3>
                {loading ? (
                  <div className="py-4 text-center">
                    <div className="mx-auto h-6 w-6 animate-spin rounded-full border-b-2 border-primary" />
                  </div>
                ) : resumes.length === 0 ? (
                  <div className="py-8 text-center text-muted-foreground">
                    <p>No processed resumes available for matching</p>
                  </div>
                ) : (
                  <Select
                    onValueChange={(value) =>
                      setSelectedSingleResume(value ? parseInt(value as string, 10) : null)
                    }
                    value={selectedResumeValue}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Choose a resume...">
                        {selectedResumeOption?.filename}
                      </SelectValue>
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

              <div className="rounded-lg border border-border/60 p-4">
                <h3 className="mb-2 text-lg font-semibold">Select Job Description</h3>
                {loading ? (
                  <div className="py-4 text-center">
                    <div className="mx-auto h-6 w-6 animate-spin rounded-full border-b-2 border-primary" />
                  </div>
                ) : jobs.length === 0 ? (
                  <div className="py-8 text-center text-muted-foreground">
                    <p>No job descriptions available for matching</p>
                  </div>
                ) : (
                  <Select
                    onValueChange={(value) =>
                      setSelectedSingleJob(value ? parseInt(value as string, 10) : null)
                    }
                    value={selectedJobValue}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Choose a job...">
                        {selectedJobOption
                          ? `${selectedJobOption.title} - ${selectedJobOption.company}`
                          : undefined}
                      </SelectValue>
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
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <div className="rounded-lg border border-border/60 p-4">
                <h3 className="mb-2 text-lg font-semibold">Select Resumes</h3>
                {loading ? (
                  <div className="py-4 text-center">
                    <div className="mx-auto h-6 w-6 animate-spin rounded-full border-b-2 border-primary" />
                  </div>
                ) : resumes.length === 0 ? (
                  <div className="py-8 text-center text-muted-foreground">
                    <p>No processed resumes available for matching</p>
                  </div>
                ) : (
                  <div className="max-h-64 space-y-2 overflow-y-auto">
                    {resumes.map((resume) => (
                      <label
                        key={resume.id}
                        className="flex cursor-pointer items-center gap-2 rounded p-2 hover:bg-muted/50"
                      >
                        <input
                          type="checkbox"
                          checked={selectedResumes.includes(resume.id)}
                          onChange={() => handleResumeToggle(resume.id)}
                          className="rounded border-border text-primary focus:ring-ring"
                        />
                        <span className="text-sm">{resume.filename}</span>
                      </label>
                    ))}
                  </div>
                )}
                <div className="mt-2 text-sm text-muted-foreground">
                  {selectedResumes.length} resume(s) selected
                </div>
              </div>

              <div className="rounded-lg border border-border/60 p-4">
                <h3 className="mb-2 text-lg font-semibold">Select Job Descriptions</h3>
                {loading ? (
                  <div className="py-4 text-center">
                    <div className="mx-auto h-6 w-6 animate-spin rounded-full border-b-2 border-primary" />
                  </div>
                ) : jobs.length === 0 ? (
                  <div className="py-8 text-center text-muted-foreground">
                    <p>No job descriptions available for matching</p>
                  </div>
                ) : (
                  <div className="max-h-64 space-y-2 overflow-y-auto">
                    {jobs.map((job) => (
                      <label
                        key={job.id}
                        className="flex cursor-pointer items-center gap-2 rounded p-2 hover:bg-muted/50"
                      >
                        <input
                          type="checkbox"
                          checked={selectedJobs.includes(job.id)}
                          onChange={() => handleJobToggle(job.id)}
                          className="rounded border-border text-primary focus:ring-ring"
                        />
                        <div className="flex-1 text-sm">
                          <div className="font-medium">{job.title}</div>
                          <div className="text-muted-foreground">{job.company}</div>
                        </div>
                      </label>
                    ))}
                  </div>
                )}
                <div className="mt-2 text-sm text-muted-foreground">
                  {selectedJobs.length} job(s) selected
                </div>
              </div>
            </div>
          )}

          {/* Bulk Matching Controls */}
          {matchingType === 'bulk' && (
            <div className="mt-6 space-y-4">
              <div className="flex flex-col items-start gap-3 sm:flex-row sm:items-center">
                <label className="text-sm font-medium">
                  Minimum Score Threshold:
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={minScoreThreshold}
                  onChange={(e) =>
                    setMinScoreThreshold(parseFloat(e.target.value))
                  }
                  className="w-full sm:max-w-xs"
                />
                <span className="text-sm text-muted-foreground">
                  {minScoreThreshold.toFixed(1)}
                </span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Matching Criteria */}
      <Card className="border-border/60 bg-card/95 shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">Matching Criteria</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <p>Our matching process considers the following criteria:</p>
          <ul className="list-inside list-disc space-y-1">
            <li>
              <strong>Skills:</strong> 40% weight - Matches candidate skills with job requirements.
            </li>
            <li>
              <strong>Experience:</strong> 30% weight - Considers relevant years of experience.
            </li>
            <li>
              <strong>Education:</strong> 20% weight - Evaluates education level and field.
            </li>
            <li>
              <strong>Other Factors:</strong> 10% weight - Certifications, keywords, location.
            </li>
          </ul>
        </CardContent>
      </Card>

      {/* Match Results */}
      <div className="rounded-lg border border-border/60 bg-card/95 p-5 shadow-sm md:p-6">
        <h2 className="mb-4 text-xl font-semibold">Match Results</h2>
        {loading ? (
          <div className="py-8 text-center">
            <div className="mx-auto h-8 w-8 animate-spin rounded-full border-b-2 border-primary" />
            <p className="mt-2 text-muted-foreground">Loading matches...</p>
          </div>
        ) : matches.length === 0 ? (
          <div className="py-8 text-center text-muted-foreground">
            <p>No matches found. Upload resumes and job descriptions to start matching!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {matches.map((match) => {
              const resume = resumes.find((r) => r.id === match.resume_id)
              const job = jobs.find((j) => j.id === match.job_id)
              const barData = getMatchChartData(match)
              const pieData = getMatchPieData(match)

              return (
                <div
                  key={match.id}
                  className="rounded-lg border border-border/60 p-4 transition-colors hover:bg-muted/30"
                >
                  <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                    <div className="flex-1">
                      <div className="mb-2 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold">
                            {resume?.filename || 'Unknown Resume'}
                          </h3>
                          <p className="text-sm text-muted-foreground">
                            {job?.title || 'Unknown Job'} at{' '}
                            {job?.company || 'Unknown Company'}
                          </p>
                        </div>

                        <div className="flex flex-wrap items-center gap-2">
                          <span
                            className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${getScoreColorClass(match.overall_score)}`}
                          >
                            {(match.overall_score * 100).toFixed(1)}%
                          </span>
                          {match.confidence_level && (
                            <Badge
                              variant={
                                SCORE_VARIANT_MAP[match.confidence_level] || 'outline'
                              }
                            >
                              {match.confidence_level}
                            </Badge>
                          )}
                        </div>
                      </div>

                      {match.recommendation && (
                        <div className="mb-4 text-sm">
                          <strong>Recommendation:</strong> {match.recommendation}
                        </div>
                      )}

                      <div className="mb-2 text-xs text-muted-foreground">
                        Created: {new Date(match.created_at).toLocaleString()}
                      </div>
                    </div>

                    <div className="w-full lg:w-auto">
                      <Button
                        onClick={(e) => requestDeleteMatch(match, e)}
                        variant="destructive"
                        className="w-full sm:w-auto"
                      >
                        Delete
                      </Button>
                    </div>
                  </div>

                  {/* Charts */}
                  <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
                    <AnimatedBarChart
                      data={barData}
                      title="Matching Scores by Category"
                      height={220}
                      colors={['#22D3EE', '#60A5FA']}
                    />
                    <AnimatedPieChart
                      data={pieData}
                      title="Match Distribution"
                      height={220}
                      colors={pieData.map((segment) => segment.color)}
                    />
                  </div>

                  {/* Detailed Analysis */}
                  <div className="mt-4 rounded-lg bg-blue-50 p-4">
                    <h4 className="mb-2 font-semibold text-blue-900">
                      Matching Analysis
                    </h4>
                    <div className="grid grid-cols-1 gap-4 text-sm md:grid-cols-2">
                      <div>
                        <p className="text-blue-800">
                          <strong>Strengths:</strong>
                          {[
                            match.skills_score && match.skills_score >= 0.7 && 'Strong skills match',
                            match.experience_score && match.experience_score >= 0.7 && 'Good experience level',
                            match.education_score && match.education_score >= 0.7 && 'Education requirement met',
                          ].filter(Boolean).join(', ') || ' None identified'}
                        </p>
                        {match.skill_overlap_count !== undefined && match.total_required_skills !== undefined && (
                          <p className="mt-1 text-blue-800">
                            <strong>Skills Overlap:</strong>{' '}
                            {match.skill_overlap_count} out of{' '}
                            {match.total_required_skills} required skills
                          </p>
                        )}
                      </div>
                      <div>
                        <p className="text-blue-800">
                          <strong>Areas for Improvement:</strong>
                          {[
                            match.skills_score && match.skills_score < 0.5 && 'Skills development needed',
                            match.experience_score && match.experience_score < 0.5 && 'More experience required',
                            match.education_score && match.education_score < 0.5 && 'Education gap identified',
                          ].filter(Boolean).join(', ') || ' None identified'}
                        </p>
                        {match.confidence_level && (
                          <p className="mt-1 text-blue-800">
                            <strong>Confidence Level:</strong>{' '}
                            {match.confidence_level.charAt(0).toUpperCase() +
                              match.confidence_level.slice(1)}
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

      <ConfirmDialog
        open={Boolean(matchPendingDelete)}
        onOpenChange={(open) => {
          if (!open) cancelDeleteMatch()
        }}
        title="Delete this match record?"
        description="This will permanently remove the matching result and analysis details."
        confirmLabel="Delete Match"
        confirming={deletingMatch}
        onConfirm={handleDeleteMatch}
      />
    </motion.div>
  )
}

export default MatchingInterface
