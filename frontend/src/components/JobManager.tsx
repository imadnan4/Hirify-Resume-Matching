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
      className="space-y-4 md:space-y-6"
    >
      <div className="rounded-lg border border-border/60 bg-card/95 p-5 shadow-sm md:p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">Job Manager</h1>
        <p className="text-gray-600 mb-4">
          Manage job descriptions through manual entry.
        </p>
        
        {error && (
          <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm font-medium text-red-700">{error}</p>
				<Button onClick={() => setError(null)} variant="destructive" size="sm" className="w-full sm:w-auto" >
					Dismiss
				</Button>
            </div>
          </div>
        )}
        
        <div className="flex flex-col sm:flex-row">
			<Button onClick={() => setShowAddForm(!showAddForm)} variant="info" className="w-full sm:w-auto">
				Add Job
			</Button>
        </div>
      </div>

      {/* Add Job Form */}
      {showAddForm && (
        <div className="rounded-lg border border-border/60 bg-card/95 p-5 shadow-sm md:p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Add New Job</h2>
          <form onSubmit={handleAddJob} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
				<Label className="mb-1 block">Job Title *</Label>
				<Input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                />
              </div>
              <div>
				<Label className="mb-1 block">Company *</Label>
				<Input
                  type="text"
                  required
                  value={formData.company}
                  onChange={(e) => setFormData({...formData, company: e.target.value})}
                />
              </div>
              <div>
				<Label className="mb-1 block">Location</Label>
				<Input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({...formData, location: e.target.value})}
                />
              </div>
              <div>
				<Label className="mb-1 block">Salary Range</Label>
				<Input
                  type="text"
                  value={formData.salary_range}
                  onChange={(e) => setFormData({...formData, salary_range: e.target.value})}
                  placeholder="e.g., $60,000 - $80,000"
                />
              </div>
              <div>
				<Label className="mb-1 block">Employment Type</Label>
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
        <Label className="mb-1 block">Experience Level</Label>
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
				<Label className="mb-1 block">Job Description *</Label>
				<Textarea
                required
                rows={4}
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="Enter the job description..."
              />
            </div>
            
            <div>
				<Label className="mb-1 block">Requirements</Label>
				<Textarea
                rows={3}
                value={formData.requirements}
                onChange={(e) => setFormData({...formData, requirements: e.target.value})}
                placeholder="Enter job requirements and qualifications..."
              />
            </div>
            
            <div className="flex flex-col gap-2 sm:flex-row">
				<Button type="submit" variant="info" className="w-full sm:w-auto">Add Job</Button>
				<Button type="button" variant="secondary" onClick={() => setShowAddForm(false)} className="w-full sm:w-auto">
					Cancel
				</Button>
            </div>
          </form>
        </div>
      )}


      {/* Jobs List */}
      <div className="rounded-lg border border-border/60 bg-card/95 p-5 shadow-sm md:p-6">
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="text-xl font-semibold text-gray-800">Job Descriptions</h2>
			<Button onClick={fetchJobs} disabled={loading} variant="secondary" className="w-full sm:w-auto">
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
              <div key={job.id} className="overflow-hidden rounded-lg border p-4 transition-colors hover:bg-muted/30">
                <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div className="flex-1">
                    <div className="mb-2 flex flex-wrap items-center gap-2.5">
                      <h3 className="font-semibold text-gray-800">{job.title}</h3>
                      <span className="text-sm text-gray-600">at {job.company}</span>
                      {job.employment_type && (
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getEmploymentTypeColor(job.employment_type)}`}>
                          {job.employment_type}
                        </span>
                      )}
                    </div>
                    <div className="mb-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-gray-600">
                      {job.location && <span>📍 {job.location}</span>}
                      {job.salary_range && <span>💰 {job.salary_range}</span>}
                      {job.experience_level && <span>📊 {job.experience_level}</span>}
                    </div>
                    <p className="text-sm text-gray-700 line-clamp-2">{job.description}</p>
                    <div className="mt-2 text-xs text-gray-500">
                      Added: {new Date(job.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  
                  <div className="flex w-full items-center gap-2 lg:w-auto lg:justify-end">
					<Button
						onClick={(e) => handleDeleteJob(job.id, e)}
						variant="destructive"
						className="w-full sm:w-auto"
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
