import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { AlertCircle } from 'lucide-react'
import apiService from '../services/api'
import { Button } from './ui/button'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Alert, AlertDescription } from './ui/alert'

interface AnalyticsData {
  matchScoreDistribution: { score: string; count: number }[]
  topSkills: { skill: string; count: number }[]
  processingStats: { status: string; count: number }[]
  companyDemand: { company: string; jobCount: number }[]
  monthlyTrends: { month: string; resumes: number; jobs: number; matches: number }[]
}

const Analytics: React.FC = () => {
  const [data, setData] = useState<AnalyticsData>({
    matchScoreDistribution: [],
    topSkills: [],
    processingStats: [],
    companyDemand: [],
    monthlyTrends: [],
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAnalyticsData()
  }, [])

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true)
      setError(null)

      const [resumeResponse, jobResponse, matchResponse] = await Promise.all([
        apiService.getResumes({ limit: 1000 }),
        apiService.getJobs({ limit: 1000 }),
        apiService.getMatches({ limit: 1000 }),
      ])

      const resumes = resumeResponse.items
      const jobs = jobResponse.items
      const matches = matchResponse.items

      const scoreRanges: Record<string, number> = {
        '90-100%': 0,
        '80-89%': 0,
        '70-79%': 0,
        '60-69%': 0,
        '50-59%': 0,
        'Below 50%': 0,
      }

      matches.forEach((match) => {
        const score = match.overall_score * 100
        if (score >= 90) scoreRanges['90-100%']++
        else if (score >= 80) scoreRanges['80-89%']++
        else if (score >= 70) scoreRanges['70-79%']++
        else if (score >= 60) scoreRanges['60-69%']++
        else if (score >= 50) scoreRanges['50-59%']++
        else scoreRanges['Below 50%']++
      })

      const matchScoreDistribution = Object.entries(scoreRanges).map(
        ([score, count]) => ({ score, count }),
      )

      const skillCount: Record<string, number> = {}
      jobs.forEach((job) => {
        if (job.extracted_skills) {
          const skills = Array.isArray(job.extracted_skills)
            ? job.extracted_skills
            : []
          skills.forEach((skill) => {
            if (typeof skill === 'string') {
              skillCount[skill] = (skillCount[skill] || 0) + 1
            }
          })
        }
      })

      const topSkills = Object.entries(skillCount)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 10)
        .map(([skill, count]) => ({ skill, count }))

      const statusCount: Record<string, number> = {}
      resumes.forEach((resume) => {
        statusCount[resume.status] = (statusCount[resume.status] || 0) + 1
      })

      const processingStats = Object.entries(statusCount).map(
        ([status, count]) => ({ status, count }),
      )

      const companyCount: Record<string, number> = {}
      jobs.forEach((job) => {
        companyCount[job.company] = (companyCount[job.company] || 0) + 1
      })

      const companyDemand = Object.entries(companyCount)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 10)
        .map(([company, jobCount]) => ({ company, jobCount }))

      // TODO: Replace with real monthly aggregation from created_at/upload_date
      // once date-based grouping is available on the backend.
      const monthlyTrends: { month: string; resumes: number; jobs: number; matches: number }[] = []

      setData({
        matchScoreDistribution,
        topSkills,
        processingStats,
        companyDemand,
        monthlyTrends,
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch analytics data')
      console.error('Error fetching analytics data:', err)
    } finally {
      setLoading(false)
    }
  }

  const BarChart: React.FC<{
    data: { label: string; value: number; color?: string }[]
    title: string
  }> = ({ data, title }) => {
    const maxValue = Math.max(...data.map((d) => d.value), 1)

    return (
      <Card className="border-border/60 bg-card/95 shadow-sm">
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          {data.length === 0 ? (
            <div className="py-8 text-center text-muted-foreground">
              <p>No data available.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {data.map((item, index) => (
                <div key={index} className="flex items-center">
                  <div className="w-20 truncate text-sm text-muted-foreground">
                    {item.label}
                  </div>
                  <div className="mx-3 flex-1">
                    <div className="h-3 rounded-full bg-muted">
                      <div
                        className={`h-3 rounded-full ${item.color || 'bg-primary'}`}
                        style={{
                          width: `${(item.value / maxValue) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                  <div className="w-10 text-right text-sm text-muted-foreground">
                    {item.value}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  const PieChart: React.FC<{
    data: { label: string; value: number; color: string }[]
    title: string
  }> = ({ data, title }) => {
    const total = data.reduce((sum, item) => sum + item.value, 0)

    return (
      <Card className="border-border/60 bg-card/95 shadow-sm">
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          {data.length === 0 || total === 0 ? (
            <div className="py-8 text-center text-muted-foreground">
              <p>No data available.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {data.map((item, index) => {
                const percentage = ((item.value / total) * 100).toFixed(1)
                return (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className={`h-4 w-4 rounded-full ${item.color}`} />
                      <span className="text-sm">{item.label}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-muted-foreground">
                        {item.value}
                      </span>
                      <span className="text-sm text-muted-foreground">
                        ({percentage}%)
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-4 md:space-y-6"
    >
      {/* Header */}
      <Card className="border-border/60 bg-card/95 shadow-sm">
        <CardHeader>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <CardTitle className="text-2xl">Analytics Dashboard</CardTitle>
              <p className="mt-2 text-sm text-muted-foreground">
                View and analyze match scores, demand trends, and performance metrics.
              </p>
            </div>
            <Button
              onClick={fetchAnalyticsData}
              disabled={loading}
              variant="secondary"
              className="w-full sm:w-auto"
            >
              {loading ? 'Loading...' : 'Refresh Data'}
            </Button>
          </div>
        </CardHeader>
      </Card>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-3.5 w-3.5" />
          <AlertDescription className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <span>{error}</span>
            <Button
              onClick={() => setError(null)}
              variant="destructive"
              size="sm"
              className="w-full sm:w-auto"
            >
              Dismiss
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {loading ? (
        <div className="py-8 text-center">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-b-2 border-primary" />
          <p className="mt-4 text-muted-foreground">Loading analytics data...</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            <BarChart
              data={data.matchScoreDistribution.map((item) => ({
                label: item.score,
                value: item.count,
                color: 'bg-purple-500',
              }))}
              title="Match Score Distribution"
            />

            <PieChart
              data={data.processingStats.map((item, index) => ({
                label:
                  item.status.charAt(0).toUpperCase() + item.status.slice(1),
                value: item.count,
                color: ['bg-green-500', 'bg-yellow-500', 'bg-blue-500', 'bg-red-500'][
                  index % 4
                ],
              }))}
              title="Resume Processing Status"
            />

            <BarChart
              data={data.topSkills.slice(0, 5).map((item) => ({
                label: item.skill,
                value: item.count,
                color: 'bg-indigo-500',
              }))}
              title="Top Skills in Demand"
            />
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <BarChart
              data={data.companyDemand.map((item) => ({
                label: item.company,
                value: item.jobCount,
                color: 'bg-green-500',
              }))}
              title="Company Hiring Demand"
            />

            <Card className="border-border/60 bg-card/95 shadow-sm">
              <CardHeader>
                <CardTitle>Monthly Trends</CardTitle>
              </CardHeader>
              <CardContent>
                {data.monthlyTrends.length === 0 ? (
                  <div className="py-8 text-center text-muted-foreground">
                    <p>Trend data not available yet.</p>
                    <p className="text-sm">Monthly aggregation will appear once enough historical data is collected.</p>
                  </div>
                ) : (
                <div className="space-y-4">
                  {data.monthlyTrends.map((trend, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between"
                    >
                      <div className="font-medium">{trend.month}</div>
                      <div className="flex items-center space-x-4 text-sm">
                        <div className="flex items-center space-x-1">
                          <div className="h-3 w-3 rounded-full bg-blue-500" />
                          <span className="text-muted-foreground">
                            Resumes: {trend.resumes}
                          </span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <div className="h-3 w-3 rounded-full bg-green-500" />
                          <span className="text-muted-foreground">
                            Jobs: {trend.jobs}
                          </span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <div className="h-3 w-3 rounded-full bg-purple-500" />
                          <span className="text-muted-foreground">
                            Matches: {trend.matches}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                )}
              </CardContent>
            </Card>
          </div>

          <Card className="border-border/60 bg-card/95 shadow-sm">
            <CardHeader>
              <CardTitle>Key Insights</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                <div className="rounded-lg bg-blue-50 p-4">
                  <h4 className="font-semibold text-blue-800">
                    Top Performing Skill
                  </h4>
                  <p className="mt-1 text-blue-600">
                    {data.topSkills.length > 0 ? data.topSkills[0].skill : 'N/A'}
                  </p>
                  <p className="mt-1 text-sm text-blue-500">
                    {data.topSkills.length > 0
                      ? `${data.topSkills[0].count} job postings`
                      : 'No data'}
                  </p>
                </div>

                <div className="rounded-lg bg-green-50 p-4">
                  <h4 className="font-semibold text-green-800">
                    Most Active Company
                  </h4>
                  <p className="mt-1 text-green-600">
                    {data.companyDemand.length > 0
                      ? data.companyDemand[0].company
                      : 'N/A'}
                  </p>
                  <p className="mt-1 text-sm text-green-500">
                    {data.companyDemand.length > 0
                      ? `${data.companyDemand[0].jobCount} job postings`
                      : 'No data'}
                  </p>
                </div>

                <div className="rounded-lg bg-purple-50 p-4">
                  <h4 className="font-semibold text-purple-800">
                    Best Match Rate
                  </h4>
                  <p className="mt-1 text-purple-600">
                    {data.matchScoreDistribution.length > 0
                      ? `${data.matchScoreDistribution.filter((s) => s.score === '90-100%').reduce((sum, s) => sum + s.count, 0)} excellent matches`
                      : 'N/A'}
                  </p>
                  <p className="mt-1 text-sm text-purple-500">
                    High-quality candidate-job pairs
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </motion.div>
  )
}

export default Analytics
