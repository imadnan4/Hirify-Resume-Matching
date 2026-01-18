import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import apiService from '../services/api'
import { Button } from './ui/button'

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
    monthlyTrends: []
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
        apiService.getMatches({ limit: 1000 })
      ])
      
      const resumes = resumeResponse.items
      const jobs = jobResponse.items
      const matches = matchResponse.items
      
      // Process match score distribution
      const scoreRanges = {
        '90-100%': 0,
        '80-89%': 0,
        '70-79%': 0,
        '60-69%': 0,
        '50-59%': 0,
        'Below 50%': 0
      }
      
      matches.forEach(match => {
        const score = match.overall_score * 100
        if (score >= 90) scoreRanges['90-100%']++
        else if (score >= 80) scoreRanges['80-89%']++
        else if (score >= 70) scoreRanges['70-79%']++
        else if (score >= 60) scoreRanges['60-69%']++
        else if (score >= 50) scoreRanges['50-59%']++
        else scoreRanges['Below 50%']++
      })
      
      const matchScoreDistribution = Object.entries(scoreRanges).map(([score, count]) => ({ score, count }))
      
      // Process top skills from job descriptions
      const skillCount: { [key: string]: number } = {}
      jobs.forEach(job => {
        if (job.extracted_skills) {
          const skills = Array.isArray(job.extracted_skills) ? job.extracted_skills : []
          skills.forEach(skill => {
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
      
      // Process resume processing stats
      const statusCount: { [key: string]: number } = {}
      resumes.forEach(resume => {
        statusCount[resume.status] = (statusCount[resume.status] || 0) + 1
      })
      
      const processingStats = Object.entries(statusCount).map(([status, count]) => ({ status, count }))
      
      // Process company demand
      const companyCount: { [key: string]: number } = {}
      jobs.forEach(job => {
        companyCount[job.company] = (companyCount[job.company] || 0) + 1
      })
      
      const companyDemand = Object.entries(companyCount)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 10)
        .map(([company, jobCount]) => ({ company, jobCount }))
      
      // Generate monthly trends (mock data for now)
      const monthlyTrends = [
        { month: 'Jan', resumes: Math.floor(resumes.length * 0.1), jobs: Math.floor(jobs.length * 0.1), matches: Math.floor(matches.length * 0.1) },
        { month: 'Feb', resumes: Math.floor(resumes.length * 0.15), jobs: Math.floor(jobs.length * 0.15), matches: Math.floor(matches.length * 0.15) },
        { month: 'Mar', resumes: Math.floor(resumes.length * 0.2), jobs: Math.floor(jobs.length * 0.2), matches: Math.floor(matches.length * 0.2) },
        { month: 'Apr', resumes: Math.floor(resumes.length * 0.25), jobs: Math.floor(jobs.length * 0.25), matches: Math.floor(matches.length * 0.25) },
        { month: 'May', resumes: Math.floor(resumes.length * 0.3), jobs: Math.floor(jobs.length * 0.3), matches: Math.floor(matches.length * 0.3) },
        { month: 'Jun', resumes: resumes.length, jobs: jobs.length, matches: matches.length }
      ]
      
      setData({
        matchScoreDistribution,
        topSkills,
        processingStats,
        companyDemand,
        monthlyTrends
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch analytics data')
      console.error('Error fetching analytics data:', err)
    } finally {
      setLoading(false)
    }
  }

  const BarChart: React.FC<{ data: { label: string; value: number; color?: string }[]; title: string }> = ({ data, title }) => {
    const maxValue = Math.max(...data.map(d => d.value))
    
    return (
      <div className='bg-white rounded-lg shadow-md p-6'>
        <h3 className='text-lg font-semibold text-gray-700 mb-4'>{title}</h3>
        {data.length === 0 ? (
          <div className='text-gray-500 text-center py-8'>
            <p>No data available.</p>
          </div>
        ) : (
          <div className='space-y-3'>
            {data.map((item, index) => (
              <div key={index} className='flex items-center'>
                <div className='w-20 text-sm text-gray-600 truncate'>{item.label}</div>
                <div className='flex-1 mx-3'>
                  <div className='bg-gray-200 rounded-full h-3'>
                    <div
                      className={`h-3 rounded-full ${item.color || 'bg-blue-500'}`}
                      style={{ width: `${maxValue > 0 ? (item.value / maxValue) * 100 : 0}%` }}
                    ></div>
                  </div>
                </div>
                <div className='w-10 text-sm text-gray-600 text-right'>{item.value}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    )
  }

  const PieChart: React.FC<{ data: { label: string; value: number; color: string }[]; title: string }> = ({ data, title }) => {
    const total = data.reduce((sum, item) => sum + item.value, 0)
    
    return (
      <div className='bg-white rounded-lg shadow-md p-6'>
        <h3 className='text-lg font-semibold text-gray-700 mb-4'>{title}</h3>
        {data.length === 0 || total === 0 ? (
          <div className='text-gray-500 text-center py-8'>
            <p>No data available.</p>
          </div>
        ) : (
          <div className='space-y-3'>
            {data.map((item, index) => {
              const percentage = ((item.value / total) * 100).toFixed(1)
              return (
                <div key={index} className='flex items-center justify-between'>
                  <div className='flex items-center space-x-2'>
                    <div className={`w-4 h-4 rounded-full ${item.color}`}></div>
                    <span className='text-sm text-gray-700'>{item.label}</span>
                  </div>
                  <div className='flex items-center space-x-2'>
                    <span className='text-sm text-gray-600'>{item.value}</span>
                    <span className='text-sm text-gray-500'>({percentage}%)</span>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className='space-y-6'
    >
      <div className='bg-white rounded-lg shadow-md p-6'>
        <h1 className='text-2xl font-bold text-gray-800 mb-4'>Analytics Dashboard</h1>
        <p className='text-gray-600 mb-4'>
          View and analyze match scores, demand trends, and performance metrics.
        </p>
        
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
			<Button onClick={() => setError(null)} variant="destructive" size="sm" >
				Dismiss
			</Button>
          </div>
        )}
        
        <div className="flex justify-end">
			<Button onClick={fetchAnalyticsData} disabled={loading} variant="secondary">
				{loading ? 'Loading...' : 'Refresh Data'}
			</Button>
        </div>
      </div>

      {loading ? (
        <div className='text-center py-8'>
          <div className='animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto'></div>
          <p className='mt-4 text-gray-600'>Loading analytics data...</p>
        </div>
      ) : (
        <>
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
            <BarChart 
              data={data.matchScoreDistribution.map(item => ({ label: item.score, value: item.count, color: 'bg-purple-500' }))}
              title="Match Score Distribution"
            />
            
            <PieChart 
              data={data.processingStats.map((item, index) => ({ 
                label: item.status.charAt(0).toUpperCase() + item.status.slice(1), 
                value: item.count, 
                color: ['bg-green-500', 'bg-yellow-500', 'bg-blue-500', 'bg-red-500'][index % 4]
              }))}
              title="Resume Processing Status"
            />
            
            <BarChart 
              data={data.topSkills.slice(0, 5).map(item => ({ label: item.skill, value: item.count, color: 'bg-indigo-500' }))}
              title="Top Skills in Demand"
            />
          </div>
          
          <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
            <BarChart 
              data={data.companyDemand.map(item => ({ label: item.company, value: item.jobCount, color: 'bg-green-500' }))}
              title="Company Hiring Demand"
            />
            
            <div className='bg-white rounded-lg shadow-md p-6'>
              <h3 className='text-lg font-semibold text-gray-700 mb-4'>Monthly Trends</h3>
              <div className='space-y-4'>
                {data.monthlyTrends.map((trend, index) => (
                  <div key={index} className='flex items-center justify-between'>
                    <div className='font-medium text-gray-700'>{trend.month}</div>
                    <div className='flex items-center space-x-4 text-sm'>
                      <div className='flex items-center space-x-1'>
                        <div className='w-3 h-3 bg-blue-500 rounded-full'></div>
                        <span>Resumes: {trend.resumes}</span>
                      </div>
                      <div className='flex items-center space-x-1'>
                        <div className='w-3 h-3 bg-green-500 rounded-full'></div>
                        <span>Jobs: {trend.jobs}</span>
                      </div>
                      <div className='flex items-center space-x-1'>
                        <div className='w-3 h-3 bg-purple-500 rounded-full'></div>
                        <span>Matches: {trend.matches}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          <div className='bg-white rounded-lg shadow-md p-6'>
            <h3 className='text-lg font-semibold text-gray-700 mb-4'>Key Insights</h3>
            <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
              <div className='p-4 bg-blue-50 rounded-lg'>
                <h4 className='font-semibold text-blue-800'>Top Performing Skill</h4>
                <p className='text-blue-600 mt-1'>
                  {data.topSkills.length > 0 ? data.topSkills[0].skill : 'N/A'}
                </p>
                <p className='text-sm text-blue-500 mt-1'>
                  {data.topSkills.length > 0 ? `${data.topSkills[0].count} job postings` : 'No data'}
                </p>
              </div>
              
              <div className='p-4 bg-green-50 rounded-lg'>
                <h4 className='font-semibold text-green-800'>Most Active Company</h4>
                <p className='text-green-600 mt-1'>
                  {data.companyDemand.length > 0 ? data.companyDemand[0].company : 'N/A'}
                </p>
                <p className='text-sm text-green-500 mt-1'>
                  {data.companyDemand.length > 0 ? `${data.companyDemand[0].jobCount} job postings` : 'No data'}
                </p>
              </div>
              
              <div className='p-4 bg-purple-50 rounded-lg'>
                <h4 className='font-semibold text-purple-800'>Best Match Rate</h4>
                <p className='text-purple-600 mt-1'>
                  {data.matchScoreDistribution.length > 0 ? 
                    `${data.matchScoreDistribution.filter(s => s.score.includes('90-100')).reduce((sum, s) => sum + s.count, 0)} excellent matches` : 
                    'N/A'
                  }
                </p>
                <p className='text-sm text-purple-500 mt-1'>
                  High-quality candidate-job pairs
                </p>
              </div>
            </div>
          </div>
        </>
      )}
    </motion.div>
  )
}

export default Analytics

