'use client'

import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { uploadDocument } from '@/lib/api'
import { DocumentMetadata } from '@/types'
import { Upload, File, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'

interface DocumentUploadProps {
  onUploadComplete: (documentId: string) => void
}

export default function DocumentUpload({ onUploadComplete }: DocumentUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [statusMessage, setStatusMessage] = useState('')
  const [metadata, setMetadata] = useState<Partial<DocumentMetadata>>({
    source: '',
    regulator: '',
    document_type: 'regulation'
  })

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    setUploading(true)
    setUploadStatus('idle')
    setStatusMessage(`Uploading ${file.name}...`)

    try {
      const result = await uploadDocument(file, {
        ...metadata,
        filename: file.name,
        file_size: file.size,
        upload_date: new Date().toISOString()
      })

      setUploadStatus('success')
      setStatusMessage(`Successfully uploaded ${file.name}`)
      onUploadComplete(result.document_id)

      // Reset form after 2 seconds
      setTimeout(() => {
        setUploadStatus('idle')
        setStatusMessage('')
      }, 2000)
    } catch (error: any) {
      setUploadStatus('error')
      setStatusMessage(error.response?.data?.detail || 'Failed to upload document')
    } finally {
      setUploading(false)
    }
  }, [metadata, onUploadComplete])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    },
    maxFiles: 1,
    disabled: uploading
  })

  return (
    <div className="card space-y-4">
      <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
        <Upload className="w-6 h-6" />
        Upload Document
      </h2>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`
          border-3 border-dashed rounded-xl p-8 text-center cursor-pointer
          transition-all duration-200
          ${isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400 bg-gray-50'
          }
          ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        <File className="w-12 h-12 mx-auto mb-3 text-gray-400" />
        {isDragActive ? (
          <p className="text-blue-600 font-semibold">Drop the file here...</p>
        ) : (
          <div>
            <p className="text-gray-700 font-semibold mb-1">
              Drag & drop a regulatory document here
            </p>
            <p className="text-gray-500 text-sm">
              or click to select a file
            </p>
            <p className="text-gray-400 text-xs mt-2">
              Supported formats: PDF, DOCX, TXT (max 10MB)
            </p>
          </div>
        )}
      </div>

      {/* Metadata Form */}
      <div className="space-y-3">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">
            Source Organization
          </label>
          <input
            type="text"
            value={metadata.source || ''}
            onChange={(e) => setMetadata({ ...metadata, source: e.target.value })}
            placeholder="e.g., European Commission, SEC, FINRA"
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
            disabled={uploading}
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">
            Regulator
          </label>
          <input
            type="text"
            value={metadata.regulator || ''}
            onChange={(e) => setMetadata({ ...metadata, regulator: e.target.value })}
            placeholder="e.g., ESMA, CFTC, FCA"
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
            disabled={uploading}
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">
            Document Type
          </label>
          <select
            value={metadata.document_type || 'regulation'}
            onChange={(e) => setMetadata({ ...metadata, document_type: e.target.value as any })}
            className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
            disabled={uploading}
          >
            <option value="law">Law</option>
            <option value="rule">Rule</option>
            <option value="regulation">Regulation</option>
            <option value="guideline">Guideline</option>
            <option value="directive">Directive</option>
            <option value="circular">Circular</option>
            <option value="notice">Notice</option>
          </select>
        </div>
      </div>

      {/* Status Message */}
      {uploadStatus !== 'idle' && (
        <div className={`
          p-4 rounded-lg flex items-center gap-3
          ${uploadStatus === 'success' ? 'bg-green-50 border-2 border-green-300' : ''}
          ${uploadStatus === 'error' ? 'bg-red-50 border-2 border-red-300' : ''}
        `}>
          {uploadStatus === 'success' && (
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
          )}
          {uploadStatus === 'error' && (
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
          )}
          <span className={`text-sm font-semibold ${
            uploadStatus === 'success' ? 'text-green-700' : 'text-red-700'
          }`}>
            {statusMessage}
          </span>
        </div>
      )}

      {uploading && (
        <div className="flex items-center justify-center gap-2 text-blue-600">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span className="font-semibold">Uploading...</span>
        </div>
      )}
    </div>
  )
}
