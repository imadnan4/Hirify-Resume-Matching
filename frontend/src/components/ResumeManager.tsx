import React, { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import apiService, { Resume } from '../services/api'

const ResumeManager: React.FC = () => {
  const [resumes, setResumes] = useState<Resume[]>([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [uploadProgress, setUploadProgress] = useState<{ [key: string]: number }>({})

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
    
    const validFiles = Array.from(files).filter(file => {
      const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
      const maxSize = 10 * 1024 * 1024 // 10MB
      
      if (!validTypes.includes(file.type)) {
        setError(`Invalid file type: ${file.name}. Only PDF, DOC, and DOCX files are allowed.`)
        return false
      }
      
      if (file.size > maxSize) {
        setError(`File too large: ${file.name}. Maximum size is 10MB.`)
        return false
      }
      
      return true
    })
    
    setSelectedFiles(validFiles)
    setError(null)
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

  const handleDeleteResume = async (resumeId: number) => {
    if (!confirm('Are you sure you want to delete this resume?')) return
    
    try {
      await apiService.deleteResume(resumeId)
      await fetchResumes()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete resume')
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
      className="space-y-6"
    >
      {/* Upload Section */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">Resume Manager</h1>
        <p className="text-gray-600 mb-4">
          Upload, manage, and process resume documents with AI-powered extraction.
        </p>
        
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
        
        <div 
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
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
          
          <button 
            onClick={() => fileInputRef.current?.click()}
            className="mt-4 bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors"
            disabled={uploading}
          >
            {uploading ? 'Uploading...' : 'Select Files'}
          </button>
        </div>
        
        {/* Selected Files */}
        {selectedFiles.length > 0 && (
          <div className="mt-4">
            <h3 className="text-lg font-medium mb-2">Selected Files:</h3>
            <div className="space-y-2">
              {selectedFiles.map((file, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center">
                    <span className="text-sm font-medium text-gray-700">{file.name}</span>
                    <span className="ml-2 text-sm text-gray-500">({formatFileSize(file.size)})</span>
                  </div>
                  {uploadProgress[file.name] && (
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${uploadProgress[file.name]}%` }}
                      ></div>
                    </div>
                  )}
                </div>
              ))}
            </div>
            <div className="mt-4 flex space-x-2">
              <button
                onClick={uploadFiles}
                disabled={uploading}
                className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50"
              >
                {uploading ? 'Uploading...' : 'Upload Files'}
              </button>
              <button
                onClick={() => {
                  setSelectedFiles([])
                  setUploadProgress({})
                }}
                className="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition-colors"
              >
                Clear
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Resumes List */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-800">Uploaded Resumes</h2>
          <button
            onClick={fetchResumes}
            disabled={loading}
            className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
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
              <div key={resume.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h3 className="font-medium text-gray-800">{resume.filename}</h3>
                      {getStatusBadge(resume.status)}
                    </div>
                    <div className="mt-1 text-sm text-gray-600">
                      <span>Size: {formatFileSize(resume.file_size)}</span>
                      <span className="mx-2">•</span>
                      <span>Type: {resume.file_type}</span>
                      <span className="mx-2">•</span>
                      <span>Uploaded: {new Date(resume.upload_date).toLocaleString()}</span>
                    </div>
                    {resume.processing_errors && (
                      <div className="mt-2 text-sm text-red-600">
                        Error: {JSON.stringify(resume.processing_errors)}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleReprocessResume(resume.id)}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Reprocess
                    </button>
                    <button
                      onClick={() => handleDeleteResume(resume.id)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Delete
                    </button>
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

export default ResumeManager
