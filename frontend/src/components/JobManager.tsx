import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import apiService, { JobDescription } from '../services/api'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Textarea } from './ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select'

const JobManager: React.FC = () => {
  const [jobs, setJobs] = useState<JobDescription[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showAddForm, setShowAddForm] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    company: '',
    description: '',
    requirements: '',
    location: '',
    salary_range: '',
    employment_type: '',
    experience_level: ''
  })

  // Load jobs on component mount
  useEffect(() => {
    fetchJobs()
  }, [])

  const fetchJobs = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await apiService.getJobs({ limit: 50 })
      setJobs(response.items)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch jobs')
      console.error('Error fetching jobs:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddJob = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await apiService.createJob({
        ...formData,
        source: 'manual'
      })
      setShowAddForm(false)
      setFormData({
        title: '',
        company: '',
        description: '',
        requirements: '',
        location: '',
        salary_range: '',
        employment_type: '',
        experience_level: ''
      })
      await fetchJobs()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add job')
    }
  }


  const handleDeleteJob = async (jobId: number, e?: React.MouseEvent) => {
    e?.stopPropagation()
    if (!confirm('Are you sure you want to delete this job?')) return
    
    try {
      console.log('Deleting job:', jobId)
      await apiService.deleteJob(jobId)
      console.log('Job deleted successfully')
      await fetchJobs()
    } catch (err: any) {
      console.error('Delete error:', err)
      setError(err.response?.data?.detail || 'Failed to delete job')
    }
  }

  const getEmploymentTypeColor = (type: string) => {
    const colors = {
      'full-time': 'bg-green-100 text-green-800',
      'part-time': 'bg-blue-100 text-blue-800',
      'contract': 'bg-purple-100 text-purple-800',
      'internship': 'bg-orange-100 text-orange-800',
      'remote': 'bg-indigo-100 text-indigo-800'
    }
    return colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">Job Manager</h1>
        <p className="text-gray-600 mb-4">
          Manage job descriptions through manual entry.
        </p>
        
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
				<Button onClick={() => setError(null)} variant="destructive" size="sm" >
					Dismiss
				</Button>
          </div>
        )}
        
        <div className="flex">
			<Button onClick={() => setShowAddForm(!showAddForm)} variant="info">
				Add Job
			</Button>
        </div>
      </div>

      {/* Add Job Form */}
      {showAddForm && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Add New Job</h2>
          <form onSubmit={handleAddJob} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
				<Label className="mb-1">Job Title *</Label>
				<Input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                />
              </div>
              <div>
				<Label className="mb-1">Company *</Label>
				<Input
                  type="text"
                  required
                  value={formData.company}
                  onChange={(e) => setFormData({...formData, company: e.target.value})}
                />
              </div>
              <div>
				<Label className="mb-1">Location</Label>
				<Input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({...formData, location: e.target.value})}
                />
              </div>
              <div>
				<Label className="mb-1">Salary Range</Label>
				<Input
                  type="text"
                  value={formData.salary_range}
                  onChange={(e) => setFormData({...formData, salary_range: e.target.value})}
                  placeholder="e.g., $60,000 - $80,000"
                />
              </div>
              <div>
				<Label className="mb-1">Employment Type</Label>
				<Select
					value={formData.employment_type || undefined}
          onValueChange={(value) => setFormData({ ...formData, employment_type: value ?? '' })}
				>
					<SelectTrigger className="w-full">
						<SelectValue placeholder="Select type" />
					</SelectTrigger>
					<SelectContent>
						<SelectItem value="full-time">Full-time</SelectItem>
						<SelectItem value="part-time">Part-time</SelectItem>
						<SelectItem value="contract">Contract</SelectItem>
						<SelectItem value="internship">Internship</SelectItem>
						<SelectItem value="remote">Remote</SelectItem>
					</SelectContent>
				</Select>
              </div>
              <div>
				<Label className="mb-1">Experience Level</Label>
				<Select
					value={formData.experience_level || undefined}
          onValueChange={(value) => setFormData({ ...formData, experience_level: value ?? '' })}
				>
					<SelectTrigger className="w-full">
						<SelectValue placeholder="Select level" />
					</SelectTrigger>
					<SelectContent>
						<SelectItem value="entry">Entry Level</SelectItem>
						<SelectItem value="mid">Mid Level</SelectItem>
						<SelectItem value="senior">Senior Level</SelectItem>
						<SelectItem value="lead">Lead/Principal</SelectItem>
						<SelectItem value="executive">Executive</SelectItem>
					</SelectContent>
				</Select>
              </div>
            </div>
            
            <div>
				<Label className="mb-1">Job Description *</Label>
				<Textarea
                required
                rows={4}
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="Enter the job description..."
              />
            </div>
            
            <div>
				<Label className="mb-1">Requirements</Label>
				<Textarea
                rows={3}
                value={formData.requirements}
                onChange={(e) => setFormData({...formData, requirements: e.target.value})}
                placeholder="Enter job requirements and qualifications..."
              />
            </div>
            
            <div className="flex space-x-4">
				<Button type="submit" variant="info">Add Job</Button>
				<Button type="button" variant="secondary" onClick={() => setShowAddForm(false)}>
					Cancel
				</Button>
            </div>
          </form>
        </div>
      )}


      {/* Jobs List */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-800">Job Descriptions</h2>
			<Button onClick={fetchJobs} disabled={loading} variant="secondary">
				{loading ? 'Loading...' : 'Refresh'}
			</Button>
        </div>
        
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading jobs...</p>
          </div>
        ) : jobs.length === 0 ? (
          <div className="text-gray-500 text-center py-8">
            <p>No job descriptions available. Add your first job description to get started!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {jobs.map((job) => (
              <div key={job.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="font-semibold text-gray-800">{job.title}</h3>
                      <span className="text-sm text-gray-600">at {job.company}</span>
                      {job.employment_type && (
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getEmploymentTypeColor(job.employment_type)}`}>
                          {job.employment_type}
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-600 mb-2">
                      {job.location && <span className="mr-4">📍 {job.location}</span>}
                      {job.salary_range && <span className="mr-4">💰 {job.salary_range}</span>}
                      {job.experience_level && <span>📊 {job.experience_level}</span>}
                    </div>
                    <p className="text-sm text-gray-700 line-clamp-2">{job.description}</p>
                    <div className="mt-2 text-xs text-gray-500">
                      Added: {new Date(job.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
					<Button
						onClick={(e) => handleDeleteJob(job.id, e)}
						variant="destructive"
						
					>
						Delete
					</Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  )
}

export default JobManager
