import React, { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { AlertCircle } from 'lucide-react'
import apiService, { Resume } from '../services/api'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Progress } from './ui/progress'
import { Alert, AlertDescription } from './ui/alert'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog'
import { useToast } from './ui/toast'
import ConfirmDialog from './ui/confirm-dialog'

const STATUS_VARIANT_MAP: Record<string, 'default' | 'secondary' | 'destructive' | 'outline' | 'ghost'> = {
  pending: 'secondary',
  processing: 'secondary',
  completed: 'default',
  failed: 'destructive',
}

const ResumeManager: React.FC = () => {
  const [resumes, setResumes] = useState<Resume[]>([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [uploadProgress, setUploadProgress] = useState<{ [key: string]: number }>({})
  const [previewData, setPreviewData] = useState<any>(null)
  const [isPreviewOpen, setIsPreviewOpen] = useState(false)
  const [resumePendingDelete, setResumePendingDelete] = useState<Resume | null>(null)
  const [deletingResume, setDeletingResume] = useState(false)
  const { addToast } = useToast()

  useEffect(() => {
    fetchResumes()
  }, [])

  const fetchResumes = async (withLoader = true) => {
    try {
      if (withLoader) setLoading(true)
      setError(null)
      const response = await apiService.getResumes({ limit: 50 })
      setResumes(response.items)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch resumes')
      console.error('Error fetching resumes:', err)
    } finally {
      if (withLoader) setLoading(false)
    }
  }

  const handleFileSelect = (files: FileList | null) => {
    if (!files) return

    const fileArray = Array.from(files)
    const validFiles: File[] = []
    let hasErrors = false

    fileArray.forEach(file => {
      const fileName = file.name.toLowerCase()
      const validExtensions = ['.pdf', '.doc', '.docx']
      const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext))
      const validTypes = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      ]
      const maxSize = 10 * 1024 * 1024

      if (!hasValidExtension && !validTypes.includes(file.type)) {
        setError(`Invalid file type: ${file.name}. Only PDF, DOC, and DOCX files are allowed.`)
        hasErrors = true
        return
      }

      if (file.size > maxSize) {
        setError(`File too large: ${file.name}. Maximum size is 10MB.`)
        hasErrors = true
        return
      }

      validFiles.push(file)
    })

    setSelectedFiles(prev => [...prev, ...validFiles])
    if (!hasErrors) setError(null)
  }

  const uploadFiles = async () => {
    if (selectedFiles.length === 0) return

    setUploading(true)
    setError(null)

    try {
      const uploadPromises = selectedFiles.map(async (file) => {
        try {
          const result = await apiService.uploadResume(file)
          setUploadProgress(prev => ({ ...prev, [file.name]: 100 }))
          return result
        } catch (err: any) {
          setError(`Failed to upload ${file.name}: ${err.response?.data?.detail || err.message}`)
          throw err
        }
      })

      await Promise.all(uploadPromises)
      setSelectedFiles([])
      setUploadProgress({})
      await fetchResumes(false)
    } catch (err) {
      console.error('Upload error:', err)
    } finally {
      setUploading(false)
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files)
    }
  }

  const requestDeleteResume = (resume: Resume, e?: React.MouseEvent) => {
    e?.stopPropagation()
    setResumePendingDelete(resume)
  }

  const handleDeleteResume = async () => {
    if (!resumePendingDelete) return

    try {
      setDeletingResume(true)
      const deletedResumeId = resumePendingDelete.id
      const deletedResumeName = resumePendingDelete.filename

      await apiService.deleteResume(deletedResumeId)
      setResumes((prev) => prev.filter((r) => r.id !== deletedResumeId))
      addToast({
        type: 'success',
        title: 'Resume deleted',
        description: `${deletedResumeName} has been removed.`,
      })
      setResumePendingDelete(null)
    } catch (err: any) {
      console.error('Delete error:', err)
      setError(err.response?.data?.detail || 'Failed to delete resume')
      addToast({
        type: 'error',
        title: 'Delete failed',
        description: err.response?.data?.detail || 'Failed to delete resume',
      })
    } finally {
      setDeletingResume(false)
    }
  }

  const handleReprocessResume = async (resumeId: number) => {
    try {
      await apiService.reprocessResume(resumeId)
      await fetchResumes(false)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reprocess resume')
    }
  }

  const handlePreviewData = async (resumeId: number) => {
    try {
      const data = await apiService.previewResumeData(resumeId)
      setPreviewData(data)
      setIsPreviewOpen(true)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch preview data')
    }
  }

  const formatFileSize = (bytes: number) => {
    const units = ['B', 'KB', 'MB', 'GB']
    let size = bytes
    let unitIndex = 0
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024
      unitIndex++
    }
    return `${size.toFixed(1)} ${units[unitIndex]}`
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-4 md:space-y-6"
    >
      {/* Upload Section */}
      <div className="rounded-lg border border-border/60 bg-card/95 p-5 shadow-sm md:p-6">
        <h1 className="mb-4 text-2xl font-bold">Resume Manager</h1>
        <p className="mb-4 text-muted-foreground">
          Upload, manage, and process resume documents with AI-powered extraction.
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

        <div
          className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors sm:p-8 ${
            dragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/30 hover:border-muted-foreground/50'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="text-muted-foreground">
            <svg className="mx-auto mb-4 h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p className="text-lg font-medium">Drop files here or click to upload</p>
            <p className="text-sm">Supports PDF, DOC, DOCX files up to 10MB</p>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.doc,.docx"
            onChange={(e) => handleFileSelect(e.target.files)}
            className="hidden"
          />

          <Button
            variant="info"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="mt-4 w-full sm:w-auto"
          >
            {uploading ? 'Uploading...' : 'Select Files'}
          </Button>
        </div>

        {/* Selected Files */}
        {selectedFiles.length > 0 && (
          <div className="mt-4">
            <h3 className="mb-2 text-lg font-medium">Selected Files:</h3>
            <div className="space-y-2">
              {selectedFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex flex-col gap-2 rounded-lg bg-muted/50 p-3 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-sm font-medium">{file.name}</span>
                    <span className="text-sm text-muted-foreground">
                      ({formatFileSize(file.size)})
                    </span>
                  </div>
                  {uploadProgress[file.name] != null && (
                    <div className="w-full sm:w-32">
                      <Progress value={uploadProgress[file.name]} />
                    </div>
                  )}
                </div>
              ))}
            </div>
            <div className="mt-4 flex flex-col gap-2 sm:flex-row">
              <Button onClick={uploadFiles} disabled={uploading} variant="success" className="w-full sm:w-auto">
                {uploading ? 'Uploading...' : 'Upload Files'}
              </Button>
              <Button
                onClick={() => {
                  setSelectedFiles([])
                  setUploadProgress({})
                }}
                variant="secondary"
                className="w-full sm:w-auto"
              >
                Clear
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Resumes List */}
      <div className="rounded-lg border border-border/60 bg-card/95 p-5 shadow-sm md:p-6">
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="text-xl font-semibold">Uploaded Resumes</h2>
          <Button onClick={() => fetchResumes()} disabled={loading} variant="secondary" className="w-full sm:w-auto">
            {loading ? 'Loading...' : 'Refresh'}
          </Button>
        </div>

        {loading ? (
          <div className="py-8 text-center">
            <div className="mx-auto h-8 w-8 animate-spin rounded-full border-b-2 border-primary" />
            <p className="mt-2 text-muted-foreground">Loading resumes...</p>
          </div>
        ) : resumes.length === 0 ? (
          <div className="py-8 text-center text-muted-foreground">
            <p>No resumes uploaded yet. Upload your first resume to get started!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {resumes.map((resume) => (
              <div
                key={resume.id}
                className="overflow-hidden rounded-lg border border-border/60 p-4 transition-colors hover:bg-muted/30"
              >
                <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div className="flex-1">
                    <div className="mb-1 flex flex-wrap items-center gap-2.5">
                      <h3 className="font-medium">{resume.filename}</h3>
                      <Badge variant={STATUS_VARIANT_MAP[resume.status] || 'outline'}>
                        {resume.status}
                      </Badge>
                    </div>
                    <div className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-muted-foreground">
                      <span>Size: {formatFileSize(resume.file_size)}</span>
                      <span>Type: {resume.file_type}</span>
                      <span>Uploaded: {new Date(resume.upload_date).toLocaleString()}</span>
                    </div>
                    {resume.processing_errors && (
                      <div className="mt-2 text-sm text-destructive">
                        Error: {JSON.stringify(resume.processing_errors)}
                      </div>
                    )}
                  </div>

                  <div className="flex w-full flex-wrap items-center gap-2 lg:w-auto lg:justify-end">
                    <Button
                      onClick={() => handleReprocessResume(resume.id)}
                      variant="link"
                      className="text-primary"
                    >
                      Reprocess
                    </Button>
                    <Button
                      onClick={() => handlePreviewData(resume.id)}
                      variant="link"
                      className="text-emerald-600"
                    >
                      Preview
                    </Button>
                    <Button
                      onClick={(e) => requestDeleteResume(resume, e)}
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

      {/* Preview Dialog */}
      <Dialog open={isPreviewOpen} onOpenChange={setIsPreviewOpen}>
        <DialogContent showCloseButton className="max-h-[92vh] sm:max-w-4xl">
          <DialogHeader>
            <DialogTitle>Extracted Resume Data</DialogTitle>
            <DialogDescription>
              AI-extracted information from the uploaded document.
            </DialogDescription>
          </DialogHeader>

          {previewData && (
            <div className="space-y-6 overflow-y-auto">
              {/* Contact Information */}
              {previewData.contact_info && (
                <div className="rounded-lg bg-blue-50 p-4">
                  <h3 className="mb-3 text-lg font-semibold text-blue-800">Contact Information</h3>
                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-4">
                    {previewData.contact_info.full_name && (
                      <div><span className="font-medium">Name:</span> {previewData.contact_info.full_name}</div>
                    )}
                    {previewData.contact_info.email && (
                      <div><span className="font-medium">Email:</span> {previewData.contact_info.email}</div>
                    )}
                    {previewData.contact_info.phone && (
                      <div><span className="font-medium">Phone:</span> {previewData.contact_info.phone}</div>
                    )}
                    {previewData.contact_info.location && (
                      <div><span className="font-medium">Location:</span> {previewData.contact_info.location}</div>
                    )}
                  </div>
                </div>
              )}

              {/* Summary */}
              {previewData.summary && (
                <div className="rounded-lg bg-green-50 p-4">
                  <h3 className="mb-3 text-lg font-semibold text-green-800">Summary</h3>
                  <p className="text-foreground">{previewData.summary}</p>
                </div>
              )}

              {/* Work Experience */}
              {previewData.work_experience && previewData.work_experience.length > 0 && (
                <div className="rounded-lg bg-purple-50 p-4">
                  <h3 className="mb-3 text-lg font-semibold text-purple-800">Work Experience</h3>
                  <div className="space-y-3">
                    {previewData.work_experience.map((exp: any, index: number) => (
                      <div key={index} className="border-l-4 border-purple-400 pl-4">
                        <div className="font-medium">
                          {exp.job_title || 'N/A'} at {exp.company || 'N/A'}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {exp.start_date || ''} - {exp.end_date || 'Present'}
                        </div>
                        {exp.description && <div className="mt-1 text-sm">{exp.description}</div>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Education */}
              {previewData.education && previewData.education.length > 0 && (
                <div className="rounded-lg bg-orange-50 p-4">
                  <h3 className="mb-3 text-lg font-semibold text-orange-800">Education</h3>
                  <div className="space-y-3">
                    {previewData.education.map((edu: any, index: number) => (
                      <div key={index} className="border-l-4 border-orange-400 pl-4">
                        <div className="font-medium">
                          {edu.degree || 'N/A'} in {edu.field_of_study || 'N/A'}
                        </div>
                        <div className="text-sm text-muted-foreground">{edu.institution || 'N/A'}</div>
                        <div className="text-sm text-muted-foreground">
                          Graduated: {edu.graduation_year || 'N/A'}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Skills */}
              {previewData.skills && previewData.skills.length > 0 && (
                <div className="rounded-lg bg-indigo-50 p-4">
                  <h3 className="mb-3 text-lg font-semibold text-indigo-800">Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {previewData.skills.map((skill: string, index: number) => (
                      <span
                        key={index}
                        className="rounded-full bg-indigo-200 px-2 py-1 text-sm text-indigo-800"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Certifications */}
              {previewData.certifications && previewData.certifications.length > 0 && (
                <div className="rounded-lg bg-red-50 p-4">
                  <h3 className="mb-3 text-lg font-semibold text-red-800">Certifications</h3>
                  <div className="space-y-2">
                    {previewData.certifications.map((cert: string, index: number) => (
                      <div key={index} className="flex items-center">
                        <div className="mr-2 h-2 w-2 rounded-full bg-red-400" />
                        <span>{cert}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Raw JSON Toggle */}
              <div className="mt-8">
                <details className="rounded-lg bg-muted/50 p-4">
                  <summary className="cursor-pointer font-medium hover:text-foreground">
                    View Raw JSON Data
                  </summary>
                  <pre className="mt-4 overflow-x-auto rounded-lg bg-muted p-4 text-sm">
                    {JSON.stringify(previewData, null, 2)}
                  </pre>
                </details>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button onClick={() => setIsPreviewOpen(false)} variant="secondary" className="w-full sm:w-auto">
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={Boolean(resumePendingDelete)}
        onOpenChange={(open) => {
          if (!open) setResumePendingDelete(null)
        }}
        title="Delete this resume?"
        description={
          resumePendingDelete
            ? `${resumePendingDelete.filename} will be permanently deleted.`
            : 'This action cannot be undone.'
        }
        confirmLabel="Delete Resume"
        confirming={deletingResume}
        onConfirm={handleDeleteResume}
      />
    </motion.div>
  )
}

export default ResumeManager
