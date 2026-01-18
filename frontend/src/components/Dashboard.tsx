import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'
import apiService from '../services/api'

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
  const navigate = useNavigate()

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


  // Process real data for charts
  const processTimeSeriesData = (data: any[], type: 'resumes' | 'jobs') => {
    if (!data || data.length === 0) return []
    
    // Group data by date
    const groupedData = data.reduce((acc, item) => {
      const date = new Date(item.created_at || item.posted_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      acc[date] = (acc[date] || 0) + 1
      return acc
    }, {})
    
    // Convert to array and sort by date
    return Object.entries(groupedData)
      .map(([date, count]) => ({ date, count }))
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
      .slice(-7) // Get last 7 days
  }

  const processScoreDistribution = () => {
    if (!stats.matchData || stats.matchData.length === 0) {
      return [
        { name: 'No Data', value: 100, color: '#9CA3AF' }
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
      { name: 'Excellent (80-100%)', value: distribution.excellent, color: '#10B981' },
      { name: 'Good (60-79%)', value: distribution.good, color: '#3B82F6' },
      { name: 'Fair (40-59%)', value: distribution.fair, color: '#F59E0B' },
      { name: 'Poor (0-39%)', value: distribution.poor, color: '#EF4444' }
    ].filter(item => item.value > 0)
  }

  const StatCard: React.FC<{ title: string; value: string; color: string; loading?: boolean }> = ({ title, value, color, loading }) => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-700 mb-2">{title}</h3>
      {loading ? (
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-16"></div>
        </div>
      ) : (
        <p className={`text-3xl font-bold ${color}`}>{value}</p>
      )}
    </div>
  )

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">Overview</h1>
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
            <button 
              onClick={() => setError(null)}
              className="mt-2 text-sm text-red-600 hover:text-red-800"
            >
              Dismiss
            </button>
          </div>
        )}

        <div className="flex justify-end mb-4">
          <button
            onClick={fetchDashboardStats}
            disabled={loading}
            className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Refresh Data'}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <StatCard 
            title="Total Resumes" 
            value={stats.totalResumes.toString()} 
            color="text-blue-600" 
            loading={loading}
          />
          <StatCard 
            title="Available Jobs" 
            value={stats.totalJobs.toString()} 
            color="text-green-600" 
            loading={loading}
          />
          <StatCard 
            title="Average Match Score" 
            value={`${(stats.averageMatchScore * 100).toFixed(1)}%`} 
            color="text-purple-600" 
            loading={loading}
          />
        </div>
      </div>

      {/* Charts section */}
      <div className="bg-white rounded-lg shadow-md p-6 mt-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Analytics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Resume Upload Trend */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-medium text-gray-700 mb-3">Resume Upload Trend</h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={processTimeSeriesData(stats.resumeData, 'resumes')}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#3B82F6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          
          {/* Job Posting Trend */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-medium text-gray-700 mb-3">Job Posting Trend</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={processTimeSeriesData(stats.jobData, 'jobs')}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Match Score Distribution */}
        <div className="mt-6 bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-medium text-gray-700 mb-3">Match Score Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={processScoreDistribution()}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {processScoreDistribution().map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
            
    </motion.div>
  )
}

export default Dashboard
