import React, { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import apiService, { Resume } from '../services/api'
import { Button } from './ui/button'
import { Progress } from './ui/progress'
import { useToast } from './ui/toast'
import ConfirmDialog from './ui/confirm-dialog'

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

  // Load resumes on component mount
  useEffect(() => {
    fetchResumes()
  }, [])

  const fetchResumes = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await apiService.getResumes({ limit: 50 })
      setResumes(response.items)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch resumes')
      console.error('Error fetching resumes:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = (files: FileList | null) => {
    if (!files) return
    
    console.log('Files selected:', files) // Debug log
    
    const fileArray = Array.from(files)
    const validFiles: File[] = []
    let hasErrors = false
    
    fileArray.forEach(file => {
      console.log(`Checking file: ${file.name}, type: ${file.type}, size: ${file.size}`) // Debug log
      
      // Check file extension (more reliable than MIME type)
      const fileName = file.name.toLowerCase()
      const validExtensions = ['.pdf', '.doc', '.docx']
      const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext))
      
      // Also check MIME types as backup
      const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
      const maxSize = 10 * 1024 * 1024 // 10MB
      
      // Accept file if either extension OR MIME type is valid
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
    
    console.log('Valid files:', validFiles) // Debug log
    
    // Add valid files to the selection (append, don't replace)
    setSelectedFiles(prev => [...prev, ...validFiles])
    
    // Only clear error if no errors occurred
    if (!hasErrors) {
      setError(null)
    }
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
      
      // Reset state
      setSelectedFiles([])
      setUploadProgress({})
      
      // Refresh resumes list
      await fetchResumes()
      
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
      await apiService.deleteResume(resumePendingDelete.id)
      console.log('Resume deleted successfully')
      await fetchResumes()
      addToast({
        type: 'success',
        title: 'Resume deleted',
        description: `${resumePendingDelete.filename} has been removed.`
      })
      setResumePendingDelete(null)
    } catch (err: any) {
      console.error('Delete error:', err)
      setError(err.response?.data?.detail || 'Failed to delete resume')
      addToast({
        type: 'error',
        title: 'Delete failed',
        description: err.response?.data?.detail || 'Failed to delete resume'
      })
    } finally {
      setDeletingResume(false)
    }
  }

  const handleReprocessResume = async (resumeId: number) => {
    try {
      await apiService.reprocessResume(resumeId)
      await fetchResumes()
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

  const getStatusBadge = (status: string) => {
    const statusColors = {
      'pending': 'bg-yellow-100 text-yellow-800',
      'processing': 'bg-blue-100 text-blue-800',
      'completed': 'bg-green-100 text-green-800',
      'failed': 'bg-red-100 text-red-800'
    }
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[status as keyof typeof statusColors] || 'bg-gray-100 text-gray-800'}`}>
        {status}
      </span>
    )
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
        <h1 className="text-2xl font-bold text-gray-800 mb-4">Resume Manager</h1>
        <p className="text-gray-600 mb-4">
          Upload, manage, and process resume documents with AI-powered extraction.
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
        
        <div 
          className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors sm:p-8 ${
            dragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="text-gray-500">
            <svg className="mx-auto h-12 w-12 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
          
      <Button variant="info" onClick={() => fileInputRef.current?.click()} disabled={uploading} className="mt-4 w-full sm:w-auto">
				{uploading ? 'Uploading...' : 'Select Files'}
			</Button>
        </div>
        
        {/* Selected Files */}
        {selectedFiles.length > 0 && (
          <div className="mt-4">
            <h3 className="text-lg font-medium mb-2">Selected Files:</h3>
            <div className="space-y-2">
              {selectedFiles.map((file, index) => (
                <div key={index} className="flex flex-col gap-2 rounded-lg bg-gray-50 p-3 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-sm font-medium text-gray-700">{file.name}</span>
                    <span className="text-sm text-gray-500">({formatFileSize(file.size)})</span>
                  </div>
                  {uploadProgress[file.name] && (
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
          <h2 className="text-xl font-semibold text-gray-800">Uploaded Resumes</h2>
			<Button onClick={fetchResumes} disabled={loading} variant="secondary" className="w-full sm:w-auto">
				{loading ? 'Loading...' : 'Refresh'}
			</Button>
        </div>
        
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading resumes...</p>
          </div>
        ) : resumes.length === 0 ? (
          <div className="text-gray-500 text-center py-8">
            <p>No resumes uploaded yet. Upload your first resume to get started!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {resumes.map((resume) => (
              <div key={resume.id} className="overflow-hidden rounded-lg border p-4 transition-colors hover:bg-muted/30">
                <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-2.5">
                      <h3 className="font-medium text-gray-800">{resume.filename}</h3>
                      {getStatusBadge(resume.status)}
                    </div>
                    <div className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-gray-600">
                      <span>Size: {formatFileSize(resume.file_size)}</span>
                      <span>Type: {resume.file_type}</span>
                      <span>Uploaded: {new Date(resume.upload_date).toLocaleString()}</span>
                    </div>
                    {resume.processing_errors && (
                      <div className="mt-2 text-sm text-red-600">
                        Error: {JSON.stringify(resume.processing_errors)}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex w-full flex-wrap items-center gap-2 lg:w-auto lg:justify-end">
					<Button
						onClick={() => handleReprocessResume(resume.id)}
						variant="link"
            className="text-blue-600"
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

      {isPreviewOpen && previewData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-3 sm:p-6">
          <div className="max-h-[92vh] w-full max-w-4xl overflow-y-auto rounded-lg bg-white p-4 shadow-xl sm:p-6 md:p-8">
            <div className="flex justify-between items-center mb-6">
			  <h2 className="text-xl font-bold text-gray-800 sm:text-2xl">Extracted Resume Data</h2>
				<Button
					onClick={() => setIsPreviewOpen(false)}
					variant="ghost"
					size="icon"
					className="text-gray-500"
				>
					×
				</Button>
            </div>
            
            <div className="space-y-6">
              {/* Contact Information */}
              {previewData.contact_info && (
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-blue-800 mb-3">Contact Information</h3>
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
                <div className="bg-green-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-green-800 mb-3">Summary</h3>
                  <p className="text-gray-700">{previewData.summary}</p>
                </div>
              )}
              
              {/* Work Experience */}
              {previewData.work_experience && previewData.work_experience.length > 0 && (
                <div className="bg-purple-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-purple-800 mb-3">Work Experience</h3>
                  <div className="space-y-3">
                    {previewData.work_experience.map((exp: any, index: number) => (
                      <div key={index} className="border-l-4 border-purple-400 pl-4">
                        <div className="font-medium">{exp.job_title || 'N/A'} at {exp.company || 'N/A'}</div>
                        <div className="text-sm text-gray-600">{exp.start_date || ''} - {exp.end_date || 'Present'}</div>
                        {exp.description && <div className="text-sm mt-1">{exp.description}</div>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Education */}
              {previewData.education && previewData.education.length > 0 && (
                <div className="bg-orange-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-orange-800 mb-3">Education</h3>
                  <div className="space-y-3">
                    {previewData.education.map((edu: any, index: number) => (
                      <div key={index} className="border-l-4 border-orange-400 pl-4">
                        <div className="font-medium">{edu.degree || 'N/A'} in {edu.field_of_study || 'N/A'}</div>
                        <div className="text-sm text-gray-600">{edu.institution || 'N/A'}</div>
                        <div className="text-sm text-gray-600">Graduated: {edu.graduation_year || 'N/A'}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Skills */}
              {previewData.skills && previewData.skills.length > 0 && (
                <div className="bg-indigo-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-indigo-800 mb-3">Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {previewData.skills.map((skill: string, index: number) => (
                      <span key={index} className="bg-indigo-200 text-indigo-800 px-2 py-1 rounded-full text-sm">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Certifications */}
              {previewData.certifications && previewData.certifications.length > 0 && (
                <div className="bg-red-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-red-800 mb-3">Certifications</h3>
                  <div className="space-y-2">
                    {previewData.certifications.map((cert: string, index: number) => (
                      <div key={index} className="flex items-center">
                        <div className="w-2 h-2 bg-red-400 rounded-full mr-2"></div>
                        <span>{cert}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Raw JSON Toggle */}
              <div className="mt-8">
                <details className="bg-gray-50 p-4 rounded-lg">
                  <summary className="cursor-pointer font-medium text-gray-700 hover:text-gray-900">
                    View Raw JSON Data
                  </summary>
                  <pre className="mt-4 bg-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
                    {JSON.stringify(previewData, null, 2)}
                  </pre>
                </details>
              </div>
            </div>
            
            <div className="mt-8 flex justify-end">
    				<Button onClick={() => setIsPreviewOpen(false)} className="w-full sm:w-auto">
					Close
				</Button>
            </div>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={Boolean(resumePendingDelete)}
        onOpenChange={(open) => {
          if (!open) {
            setResumePendingDelete(null)
          }
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
