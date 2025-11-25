'use client'

import React, { useState, useEffect } from 'react'
import DocumentUpload from '@/components/DocumentUpload'
import AnalysisResults from '@/components/AnalysisResults'
import DocumentsList from '@/components/DocumentsList'
import WorkflowVisualization from '@/components/WorkflowVisualization'
import { listDocuments, healthCheck } from '@/lib/api'
import { DocumentInfo, AnalysisResult } from '@/types'
import { AlertCircle, CheckCircle, Activity } from 'lucide-react'

export default function Home() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([])
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [serverStatus, setServerStatus] = useState<'online' | 'offline' | 'checking'>('checking')
  const [showWorkflow, setShowWorkflow] = useState(false)

  // Check server health on mount
  useEffect(() => {
    checkServerHealth()
    loadDocuments()
  }, [])

  const checkServerHealth = async () => {
    try {
      await healthCheck()
      setServerStatus('online')
    } catch {
      setServerStatus('offline')
    }
  }

  const loadDocuments = async () => {
    try {
      const docs = await listDocuments()
      setDocuments(docs)
    } catch (error) {
      console.error('Failed to load documents:', error)
    }
  }

  const handleUploadComplete = (documentId: string) => {
    loadDocuments()
    setSelectedDocument(documentId)
  }

  const handleDocumentSelect = (documentId: string) => {
    setSelectedDocument(documentId)
    // Clear previous results
    setAnalysisResult(null)
  }

  const handleAnalysisComplete = (result: AnalysisResult) => {
    setAnalysisResult(result)
    setIsAnalyzing(false)
  }

  const handleAnalysisStart = () => {
    setIsAnalyzing(true)
    setAnalysisResult(null)
  }

  const handleDocumentDelete = async (documentId: string) => {
    if (selectedDocument === documentId) {
      setSelectedDocument(null)
      setAnalysisResult(null)
    }
    await loadDocuments()
  }

  return (
    <div className="space-y-6">
      {/* Server Status Banner */}
      <div className={`card ${
        serverStatus === 'online' ? 'border-l-4 border-l-green-500' : 
        serverStatus === 'offline' ? 'border-l-4 border-l-red-500' : 
        'border-l-4 border-l-yellow-500'
      }`}>
        <div className="flex items-center gap-3">
          {serverStatus === 'online' && (
            <>
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-green-700 font-semibold">Backend Server Online</span>
            </>
          )}
          {serverStatus === 'offline' && (
            <>
              <AlertCircle className="w-5 h-5 text-red-600" />
              <span className="text-red-700 font-semibold">Backend Server Offline - Please start the FastAPI server</span>
            </>
          )}
          {serverStatus === 'checking' && (
            <>
              <Activity className="w-5 h-5 text-yellow-600 animate-spin" />
              <span className="text-yellow-700 font-semibold">Checking server status...</span>
            </>
          )}
        </div>
      </div>

      {/* Workflow Visualization Toggle */}
      <div className="card">
        <button
          onClick={() => setShowWorkflow(!showWorkflow)}
          className="btn-secondary w-full"
        >
          {showWorkflow ? 'Hide' : 'Show'} Workflow Visualization
        </button>
        {showWorkflow && (
          <div className="mt-4">
            <WorkflowVisualization />
          </div>
        )}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Upload & Documents List */}
        <div className="lg:col-span-1 space-y-6">
          <DocumentUpload onUploadComplete={handleUploadComplete} />
          <DocumentsList
            documents={documents}
            selectedDocument={selectedDocument}
            onDocumentSelect={handleDocumentSelect}
            onDocumentDelete={handleDocumentDelete}
          />
        </div>

        {/* Right Column: Analysis Results */}
        <div className="lg:col-span-2">
          <AnalysisResults
            documentId={selectedDocument}
            analysisResult={analysisResult}
            isAnalyzing={isAnalyzing}
            onAnalysisComplete={handleAnalysisComplete}
            onAnalysisStart={handleAnalysisStart}
          />
        </div>
      </div>
    </div>
  )
}
