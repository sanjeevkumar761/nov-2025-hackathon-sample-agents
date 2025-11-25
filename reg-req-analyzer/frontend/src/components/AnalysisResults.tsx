'use client'

import React, { useEffect, useState } from 'react'
import { analyzeDocument, getAnalysisResults } from '@/lib/api'
import { AnalysisResult } from '@/types'
import { FileText, Loader2, AlertTriangle, CheckCircle2, TrendingUp } from 'lucide-react'
import RiskAssessment from './RiskAssessment'

interface AnalysisResultsProps {
  documentId: string | null
  analysisResult: AnalysisResult | null
  isAnalyzing: boolean
  onAnalysisComplete: (result: AnalysisResult) => void
  onAnalysisStart: () => void
}

export default function AnalysisResults({
  documentId,
  analysisResult,
  isAnalyzing,
  onAnalysisComplete,
  onAnalysisStart
}: AnalysisResultsProps) {
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'lrr' | 'taxonomy' | 'summary' | 'risk'>('lrr')

  const handleAnalyze = async () => {
    if (!documentId) return

    setError(null)
    onAnalysisStart()

    try {
      const result = await analyzeDocument(documentId)
      
      // Poll for results
      const maxAttempts = 60
      let attempts = 0
      
      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        try {
          const analysisData = await getAnalysisResults(documentId)
          if (analysisData) {
            onAnalysisComplete(analysisData)
            return
          }
        } catch {
          // Continue polling
        }
        
        attempts++
      }
      
      setError('Analysis timed out. Please try again.')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze document')
    }
  }

  if (!documentId) {
    return (
      <div className="card h-full flex items-center justify-center">
        <div className="text-center text-gray-500">
          <FileText className="w-16 h-16 mx-auto mb-4 opacity-30" />
          <p className="text-lg font-semibold">No Document Selected</p>
          <p className="text-sm mt-2">Upload or select a document to begin analysis</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">Analysis Results</h2>
        {!analysisResult && !isAnalyzing && (
          <button onClick={handleAnalyze} className="btn-primary">
            Start Analysis
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <span className="text-red-700 font-semibold">{error}</span>
        </div>
      )}

      {isAnalyzing && (
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
          <p className="text-lg font-semibold text-gray-700">Analyzing Document...</p>
          <p className="text-sm text-gray-500 mt-2">This may take 30-60 seconds</p>
        </div>
      )}

      {analysisResult && !isAnalyzing && (
        <div className="space-y-6">
          {/* Tab Navigation */}
          <div className="flex gap-2 border-b-2 border-gray-200">
            <button
              onClick={() => setActiveTab('lrr')}
              className={`px-4 py-2 font-semibold transition-colors ${
                activeTab === 'lrr'
                  ? 'text-blue-600 border-b-2 border-blue-600 -mb-0.5'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Laws, Rules & Regulations
            </button>
            <button
              onClick={() => setActiveTab('taxonomy')}
              className={`px-4 py-2 font-semibold transition-colors ${
                activeTab === 'taxonomy'
                  ? 'text-blue-600 border-b-2 border-blue-600 -mb-0.5'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Taxonomy Impacts
            </button>
            <button
              onClick={() => setActiveTab('risk')}
              className={`px-4 py-2 font-semibold transition-colors ${
                activeTab === 'risk'
                  ? 'text-blue-600 border-b-2 border-blue-600 -mb-0.5'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Risk Assessment
            </button>
            <button
              onClick={() => setActiveTab('summary')}
              className={`px-4 py-2 font-semibold transition-colors ${
                activeTab === 'summary'
                  ? 'text-blue-600 border-b-2 border-blue-600 -mb-0.5'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Summary
            </button>
          </div>

          {/* Tab Content */}
          <div>
            {activeTab === 'lrr' && (
              <div className="space-y-4">
                <h3 className="text-xl font-bold text-gray-800">
                  Identified Requirements ({analysisResult.identified_lrr.length})
                </h3>
                {analysisResult.identified_lrr.map((item, idx) => (
                  <div key={idx} className="border-2 border-gray-200 rounded-lg p-4 space-y-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`badge badge-${item.type.toLowerCase()}`}>
                            {item.type}
                          </span>
                          <span className={`badge badge-${item.severity}`}>
                            {item.severity} Priority
                          </span>
                          {item.reference && (
                            <span className="text-sm text-gray-500 font-mono">
                              {item.reference}
                            </span>
                          )}
                        </div>
                        <p className="font-semibold text-gray-800 mb-2">
                          {item.description}
                        </p>
                        {item.requirement && (
                          <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">
                            <strong>Requirement:</strong> {item.requirement}
                          </p>
                        )}
                      </div>
                    </div>

                    {item.obligated_parties && item.obligated_parties.length > 0 && (
                      <div className="text-sm">
                        <strong className="text-gray-700">Obligated Parties:</strong>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {item.obligated_parties.map((party, pidx) => (
                            <span key={pidx} className="bg-blue-100 text-blue-700 px-2 py-1 rounded">
                              {party}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {item.penalties && (Array.isArray(item.penalties) ? item.penalties.length > 0 : item.penalties) && (
                      <div className="text-sm">
                        <strong className="text-red-600">Penalties:</strong>
                        <ul className="list-disc list-inside mt-1 text-gray-700">
                          {Array.isArray(item.penalties) ? (
                            item.penalties.map((penalty, pidx) => (
                              <li key={pidx}>{penalty}</li>
                            ))
                          ) : (
                            <li>{item.penalties}</li>
                          )}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'taxonomy' && (
              <div className="space-y-4">
                <h3 className="text-xl font-bold text-gray-800">
                  Taxonomy Impacts ({analysisResult.taxonomy_impacts.length})
                </h3>
                {analysisResult.taxonomy_impacts.map((impact, idx) => (
                  <div key={idx} className="border-2 border-purple-200 bg-purple-50 rounded-lg p-4 space-y-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-lg font-bold text-purple-700">
                            {impact.area}
                          </span>
                          <span className={`badge badge-${impact.urgency}`}>
                            {impact.urgency} Urgency
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">
                          <strong>Type:</strong> {impact.impact_type}
                        </p>
                        <p className="text-gray-700 mb-3">
                          {impact.description}
                        </p>
                        <div className="bg-white border-2 border-purple-300 rounded-lg p-3">
                          <strong className="text-purple-700">Recommended Action:</strong>
                          <p className="text-gray-700 mt-1">{impact.recommended_action}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'risk' && analysisResult.risk_assessment && (
              <RiskAssessment riskAssessment={analysisResult.risk_assessment} />
            )}

            {activeTab === 'summary' && (
              <div className="space-y-4">
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200 rounded-lg p-6">
                  <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                    <CheckCircle2 className="w-6 h-6 text-green-600" />
                    Executive Summary
                  </h3>
                  <div className="prose max-w-none text-gray-700 whitespace-pre-line">
                    {analysisResult.summary}
                  </div>
                </div>

                {/* Metadata */}
                {analysisResult.document_metadata && (
                  <div className="grid grid-cols-2 gap-4">
                    {analysisResult.document_metadata.source && (
                      <div className="bg-gray-50 rounded-lg p-4">
                        <p className="text-sm text-gray-600 font-semibold">Source</p>
                        <p className="text-gray-800">{analysisResult.document_metadata.source}</p>
                      </div>
                    )}
                    {analysisResult.document_metadata.regulator && (
                      <div className="bg-gray-50 rounded-lg p-4">
                        <p className="text-sm text-gray-600 font-semibold">Regulator</p>
                        <p className="text-gray-800">{analysisResult.document_metadata.regulator}</p>
                      </div>
                    )}
                    {analysisResult.document_metadata.document_type && (
                      <div className="bg-gray-50 rounded-lg p-4">
                        <p className="text-sm text-gray-600 font-semibold">Document Type</p>
                        <p className="text-gray-800 capitalize">{analysisResult.document_metadata.document_type}</p>
                      </div>
                    )}
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm text-gray-600 font-semibold">Analysis Date</p>
                      <p className="text-gray-800">{new Date(analysisResult.analysis_date).toLocaleString()}</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
