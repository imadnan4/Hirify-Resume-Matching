import React, { useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import apiService from '../services/api'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { AnimatedBarChart, AnimatedLineChart, AnimatedPieChart } from './ui/animated-chart'

interface DashboardStats {
  totalResumes: number
  totalJobs: number
  averageMatchScore: number
  resumeData: any[]
  jobData: any[]
  matchData: any[]
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalResumes: 0,
    totalJobs: 0,
    averageMatchScore: 0,
    resumeData: [],
    jobData: [],
    matchData: []
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDashboardStats()
  }, [])

  const fetchDashboardStats = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const [resumeResponse, jobResponse, matchResponse] = await Promise.all([
        apiService.getResumes({ limit: 1000 }),
        apiService.getJobs({ limit: 1000 }),
        apiService.getMatches({ limit: 1000 })
      ])
      
      const totalResumes = resumeResponse.total
      const totalJobs = jobResponse.total
      const matches = matchResponse.items
      
      // Calculate average match score
      const averageMatchScore = matches.length > 0 
        ? matches.reduce((sum, match) => sum + match.overall_score, 0) / matches.length
        : 0
      
      setStats((prev) => ({
        ...prev,
        totalResumes,
        totalJobs,
        averageMatchScore,
        resumeData: resumeResponse.items,
        jobData: jobResponse.items,
        matchData: matches
      }))
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch dashboard data')
      console.error('Error fetching dashboard stats:', err)
    } finally {
      setLoading(false)
    }
  }

  const processTimeSeriesData = (data: any[]) => {
    if (!data || data.length === 0) return []

    const groupedData = data.reduce((acc: Record<string, number>, item) => {
      const rawDate = item.created_at || item.posted_at
      if (!rawDate) {
        return acc
      }

      const day = new Date(rawDate)
      const dayKey = day.toISOString().slice(0, 10)
      acc[dayKey] = (acc[dayKey] || 0) + 1
      return acc
    }, {})

    return Object.entries(groupedData)
      .sort(([a], [b]) => a.localeCompare(b))
      .slice(-7)
      .map(([dayKey, count]) => ({
        date: new Date(dayKey).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        count,
      }))
  }

  const processScoreDistribution = () => {
    if (!stats.matchData || stats.matchData.length === 0) {
      return [
        { name: 'No Data', value: 100, color: '#94A3B8' }
      ]
    }
    
    const distribution = {
      excellent: 0,
      good: 0,
      fair: 0,
      poor: 0
    }
    
    stats.matchData.forEach(match => {
      const score = match.overall_score * 100
      if (score >= 80) distribution.excellent++
      else if (score >= 60) distribution.good++
      else if (score >= 40) distribution.fair++
      else distribution.poor++
    })
    
    return [
      { name: 'Excellent (80-100%)', value: distribution.excellent, color: '#22C55E' },
      { name: 'Good (60-79%)', value: distribution.good, color: '#0EA5E9' },
      { name: 'Fair (40-59%)', value: distribution.fair, color: '#F59E0B' },
      { name: 'Poor (0-39%)', value: distribution.poor, color: '#F43F5E' }
    ].filter(item => item.value > 0)
  }

  const resumeTrendData = useMemo(() => processTimeSeriesData(stats.resumeData), [stats.resumeData])
  const jobTrendData = useMemo(() => processTimeSeriesData(stats.jobData), [stats.jobData])
  const scoreDistribution = useMemo(() => processScoreDistribution(), [stats.matchData])

  const StatCard: React.FC<{ title: string; value: string; color: string; loading?: boolean }> = ({ title, value, color, loading }) => {
    return (
      <Card className="border-border/60 bg-card/95 shadow-sm">
        <CardHeader className="pb-2">
          <CardDescription>{title}</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="animate-pulse">
              <div className="h-8 w-20 rounded bg-muted"></div>
            </div>
          ) : (
            <p className={`text-3xl font-semibold tracking-tight ${color}`}>{value}</p>
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
      <Card className="border-border/60 bg-card/95 shadow-sm">
        <CardHeader className="gap-4">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <CardTitle className="text-2xl">Dashboard</CardTitle>
              <CardDescription>Operational summary of resumes, jobs, and match quality.</CardDescription>
            </div>
            <Button onClick={fetchDashboardStats} disabled={loading} variant="secondary" size="lg" className="w-full sm:w-auto">
              {loading ? 'Loading...' : 'Refresh Data'}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50/90 p-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm font-medium text-red-700">{error}</p>
              <Button onClick={() => setError(null)} variant="destructive" size="sm" className="w-full sm:w-auto">
                Dismiss
              </Button>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          <StatCard 
            title="Total Resumes" 
            value={stats.totalResumes.toString()} 
            color="text-sky-600" 
            loading={loading}
          />
          <StatCard 
            title="Available Jobs" 
            value={stats.totalJobs.toString()} 
            color="text-emerald-600" 
            loading={loading}
          />
          <StatCard 
            title="Average Match Score" 
            value={`${(stats.averageMatchScore * 100).toFixed(1)}%`} 
            color="text-indigo-600" 
            loading={loading}
          />
        </div>
        </CardContent>
      </Card>

      <Card className="border-border/60 bg-card/95 shadow-sm">
        <CardHeader>
          <CardTitle>Analytics</CardTitle>
          <CardDescription>EvilCharts-inspired motion styling with readable tooltips and compact axes.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 md:space-y-6">
          <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
            <AnimatedLineChart
              data={resumeTrendData}
              title="Resume Upload Trend"
              height={260}
              colors={['#22D3EE']}
            />
            <AnimatedBarChart
              data={jobTrendData}
              title="Job Posting Trend"
              height={260}
              colors={['#38BDF8']}
            />
          </div>

          <AnimatedPieChart
            data={scoreDistribution}
            title="Match Score Distribution"
            height={300}
            colors={scoreDistribution.map((entry) => entry.color)}
          />
        </CardContent>
      </Card>
            
    </motion.div>
  )
}

export default Dashboard
