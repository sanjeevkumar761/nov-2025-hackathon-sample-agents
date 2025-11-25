'use client'

import React from 'react'
import { deleteDocument } from '@/lib/api'
import { DocumentInfo } from '@/types'
import { FileText, Trash2, Calendar, HardDrive } from 'lucide-react'

interface DocumentsListProps {
  documents: DocumentInfo[]
  selectedDocument: string | null
  onDocumentSelect: (documentId: string) => void
  onDocumentDelete: (documentId: string) => void
}

export default function DocumentsList({
  documents,
  selectedDocument,
  onDocumentSelect,
  onDocumentDelete
}: DocumentsListProps) {
  const handleDelete = async (e: React.MouseEvent, documentId: string) => {
    e.stopPropagation()
    
    if (!confirm('Are you sure you want to delete this document?')) {
      return
    }

    try {
      await deleteDocument(documentId)
      onDocumentDelete(documentId)
    } catch (error) {
      console.error('Failed to delete document:', error)
      alert('Failed to delete document')
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="card">
      <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
        <FileText className="w-6 h-6" />
        Documents ({documents.length})
      </h2>

      {documents.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <FileText className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p className="font-semibold">No documents uploaded</p>
          <p className="text-sm mt-1">Upload your first regulatory document to get started</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-[600px] overflow-y-auto">
          {documents.map((doc) => (
            <div
              key={doc.document_id}
              onClick={() => onDocumentSelect(doc.document_id)}
              className={`
                p-4 rounded-lg border-2 cursor-pointer transition-all duration-200
                ${selectedDocument === doc.document_id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300 bg-white'
                }
              `}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <FileText className="w-4 h-4 text-gray-600 flex-shrink-0" />
                    <p className="font-semibold text-gray-800 truncate">
                      {doc.document_metadata?.filename || 'Unknown Document'}
                    </p>
                  </div>

                  <div className="space-y-1 text-xs text-gray-600">
                    {doc.document_metadata?.file_size && (
                      <div className="flex items-center gap-1">
                        <HardDrive className="w-3 h-3" />
                        <span>{formatFileSize(doc.document_metadata.file_size)}</span>
                      </div>
                    )}
                    {doc.document_metadata?.upload_date && (
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        <span>{formatDate(doc.document_metadata.upload_date)}</span>
                      </div>
                    )}
                    {doc.document_metadata?.source && (
                      <div className="text-xs">
                        <strong>Source:</strong> {doc.document_metadata.source}
                      </div>
                    )}
                    {doc.document_metadata?.document_type && (
                      <span className="inline-block px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-xs font-semibold capitalize">
                        {doc.document_metadata.document_type}
                      </span>
                    )}
                  </div>
                </div>

                <button
                  onClick={(e) => handleDelete(e, doc.document_id)}
                  className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors flex-shrink-0"
                  title="Delete document"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
