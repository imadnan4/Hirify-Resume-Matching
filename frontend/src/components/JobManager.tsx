import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { AlertCircle } from 'lucide-react'
import apiService, { JobDescription } from '../services/api'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Textarea } from './ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select'
import { Badge } from './ui/badge'
import { Alert, AlertDescription } from './ui/alert'
import { useToast } from './ui/toast'
import { useDeleteFlow } from '../hooks/use-delete-flow'
import ConfirmDialog from './ui/confirm-dialog'

const EMPLOYMENT_TYPE_VARIANTS: Record<string, 'default' | 'secondary' | 'destructive' | 'outline' | 'ghost'> = {
  'full-time': 'default',
  'part-time': 'secondary',
  contract: 'outline',
  internship: 'ghost',
  remote: 'secondary',
}

const JobManager: React.FC = () => {
  const [jobs, setJobs] = useState<JobDescription[]>([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showAddForm, setShowAddForm] = useState(false)
  const { addToast } = useToast()
  const {
    pendingDelete: jobPendingDelete,
    deleting: deletingJob,
    requestDelete: requestDeleteJob,
    cancelDelete: cancelDeleteJob,
    handleDelete: handleDeleteJob,
  } = useDeleteFlow<JobDescription>({
    deleteFn: (id) => apiService.deleteJob(id),
    itemLabel: 'Job',
    onDeleted: (id) => setJobs((prev) => prev.filter((job) => job.id !== id)),
    getDescription: (item) => `${item.title} at ${item.company}`,
  })
  const [formData, setFormData] = useState({
    title: '',
    company: '',
    description: '',
    requirements: '',
    location: '',
    salary_range: '',
    employment_type: '',
    experience_level: '',
  })

  useEffect(() => {
    fetchJobs()
  }, [])

  const fetchJobs = async (withLoader = true) => {
    try {
      if (withLoader) setLoading(true)
      setError(null)
      const response = await apiService.getJobs({ limit: 50 })
      setJobs(response.items)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch jobs')
      console.error('Error fetching jobs:', err)
    } finally {
      if (withLoader) setLoading(false)
    }
  }

  const handleAddJob = async (e: React.FormEvent) => {
    e.preventDefault()
    if (submitting) return

    const payload: Record<string, any> = {
      title: formData.title,
      company: formData.company,
      description: formData.description,
      requirements: formData.requirements,
      source: 'manual',
    }
    if (formData.location) payload.location = formData.location
    if (formData.salary_range) payload.salary_range = formData.salary_range
    if (formData.employment_type) payload.employment_type = formData.employment_type
    if (formData.experience_level) payload.experience_level = formData.experience_level

    try {
      setSubmitting(true)
      await apiService.createJob(payload)
      setShowAddForm(false)
      setFormData({
        title: '',
        company: '',
        description: '',
        requirements: '',
        location: '',
        salary_range: '',
        employment_type: '',
        experience_level: '',
      })
      addToast({
        type: 'success',
        title: 'Job created',
        description: `${formData.title} has been added.`,
      })
      await fetchJobs(false)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add job')
    } finally {
      setSubmitting(false)
    }
  }



  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-4 md:space-y-6"
    >
      {/* Header */}
      <div className="rounded-lg border border-border/60 bg-card/95 p-5 shadow-sm md:p-6">
        <h1 className="mb-4 text-2xl font-bold">Job Manager</h1>
        <p className="mb-4 text-muted-foreground">
          Manage job descriptions through manual entry.
        </p>

        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertCircle className="h-3.5 w-3.5" />
            <AlertDescription className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <span>{error}</span>
              <Button onClick={() => setError(null)} variant="destructive" size="sm" className="w-full sm:w-auto">
                Dismiss
              </Button>
            </AlertDescription>
          </Alert>
        )}

        <div className="flex flex-col sm:flex-row">
          <Button onClick={() => setShowAddForm(!showAddForm)} variant="info" className="w-full sm:w-auto">
            {showAddForm ? 'Cancel' : 'Add Job'}
          </Button>
        </div>
      </div>

      {/* Add Job Form */}
      {showAddForm && (
        <div className="rounded-lg border border-border/60 bg-card/95 p-5 shadow-sm md:p-6">
          <h2 className="mb-4 text-xl font-semibold">Add New Job</h2>
          <form onSubmit={handleAddJob} className="space-y-4">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <Label className="mb-1 block">Job Title *</Label>
                <Input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                />
              </div>
              <div>
                <Label className="mb-1 block">Company *</Label>
                <Input
                  type="text"
                  required
                  value={formData.company}
                  onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                />
              </div>
              <div>
                <Label className="mb-1 block">Location</Label>
                <Input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                />
              </div>
              <div>
                <Label className="mb-1 block">Salary Range</Label>
                <Input
                  type="text"
                  value={formData.salary_range}
                  onChange={(e) => setFormData({ ...formData, salary_range: e.target.value })}
                  placeholder="e.g., $60,000 - $80,000"
                />
              </div>
              <div>
                <Label className="mb-1 block">Employment Type</Label>
                <Select
                  value={formData.employment_type || undefined}
                  onValueChange={(value) =>
                    setFormData({ ...formData, employment_type: (value as string) ?? '' })
                  }
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
                  onValueChange={(value) =>
                    setFormData({ ...formData, experience_level: (value as string) ?? '' })
                  }
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
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Enter the job description..."
              />
            </div>

            <div>
              <Label className="mb-1 block">Requirements</Label>
              <Textarea
                rows={3}
                value={formData.requirements}
                onChange={(e) =>
                  setFormData({ ...formData, requirements: e.target.value })
                }
                placeholder="Enter job requirements and qualifications..."
              />
            </div>

            <div className="flex flex-col gap-2 sm:flex-row">
              <Button type="submit" variant="info" disabled={submitting} className="w-full sm:w-auto">
                {submitting ? 'Adding...' : 'Add Job'}
              </Button>
              <Button
                type="button"
                variant="secondary"
                onClick={() => setShowAddForm(false)}
                className="w-full sm:w-auto"
              >
                Cancel
              </Button>
            </div>
          </form>
        </div>
      )}

      {/* Jobs List */}
      <div className="rounded-lg border border-border/60 bg-card/95 p-5 shadow-sm md:p-6">
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="text-xl font-semibold">Job Descriptions</h2>
          <Button onClick={() => fetchJobs()} disabled={loading} variant="secondary" className="w-full sm:w-auto">
            {loading ? 'Loading...' : 'Refresh'}
          </Button>
        </div>

        {loading ? (
          <div className="py-8 text-center">
            <div className="mx-auto h-8 w-8 animate-spin rounded-full border-b-2 border-primary" />
            <p className="mt-2 text-muted-foreground">Loading jobs...</p>
          </div>
        ) : jobs.length === 0 ? (
          <div className="py-8 text-center text-muted-foreground">
            <p>No job descriptions available. Add your first job description to get started!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {jobs.map((job) => (
              <div
                key={job.id}
                className="overflow-hidden rounded-lg border border-border/60 p-4 transition-colors hover:bg-muted/30"
              >
                <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div className="flex-1">
                    <div className="mb-2 flex flex-wrap items-center gap-2.5">
                      <h3 className="font-semibold">{job.title}</h3>
                      <span className="text-sm text-muted-foreground">at {job.company}</span>
                      {job.employment_type && (
                        <Badge variant={EMPLOYMENT_TYPE_VARIANTS[job.employment_type] || 'outline'}>
                          {job.employment_type}
                        </Badge>
                      )}
                    </div>
                    <div className="mb-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted-foreground">
                      {job.location && <span>📍 {job.location}</span>}
                      {job.salary_range && <span>💰 {job.salary_range}</span>}
                      {job.experience_level && <span>📊 {job.experience_level}</span>}
                    </div>
                    <p className="line-clamp-2 text-sm">{job.description}</p>
                    <div className="mt-2 text-xs text-muted-foreground">
                      Added: {new Date(job.created_at).toLocaleDateString()}
                    </div>
                  </div>

                  <div className="flex w-full items-center gap-2 lg:w-auto lg:justify-end">
                    <Button
                      onClick={(e) => requestDeleteJob(job, e)}
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

      <ConfirmDialog
        open={Boolean(jobPendingDelete)}
        onOpenChange={(open) => {
          if (!open) cancelDeleteJob()
        }}
        title="Delete this job?"
        description={
          jobPendingDelete
            ? `${jobPendingDelete.title} at ${jobPendingDelete.company} will be permanently deleted.`
            : 'This action cannot be undone.'
        }
        confirmLabel="Delete Job"
        confirming={deletingJob}
        onConfirm={handleDeleteJob}
      />
    </motion.div>
  )
}

export default JobManager
