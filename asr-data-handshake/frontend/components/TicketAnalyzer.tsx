'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { analyzeTicket } from '@/lib/api'
import { Search, AlertTriangle, CheckCircle, TrendingUp } from 'lucide-react'

export default function TicketAnalyzer() {
  const [ticketId, setTicketId] = useState('')

  const analyzeMutation = useMutation({
    mutationFn: (id: string) => analyzeTicket(id, true),
  })

  const handleAnalyze = () => {
    if (!ticketId.trim()) return
    analyzeMutation.mutate(ticketId)
  }

  const getQualityColor = (score: number) => {
    if (score >= 91) return 'quality-excellent'
    if (score >= 71) return 'quality-good'
    if (score >= 41) return 'quality-fair'
    return 'quality-poor'
  }

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <div className="ticket-card">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Analyze Ticket Quality</h2>
        <p className="text-gray-600 mb-6">
          Enter a ServiceNow ticket ID to assess its quality across 4 dimensions
        </p>

        <div className="flex gap-3">
          <input
            type="text"
            value={ticketId}
            onChange={(e) => setTicketId(e.target.value)}
            placeholder="Enter ticket ID (e.g., INC0025000)"
            className="form-input flex-1"
            onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
          />
          <button
            onClick={handleAnalyze}
            disabled={analyzeMutation.isPending || !ticketId.trim()}
            className="btn-primary flex items-center gap-2"
          >
            <Search className="h-5 w-5" />
            {analyzeMutation.isPending ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
      </div>

      {/* Results */}
      {analyzeMutation.isSuccess && analyzeMutation.data && (
        <div className="space-y-6 animate-fade-in">
          {/* Overall Score */}
          <div className="ticket-card">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-semibold text-gray-900">Overall Quality Score</h3>
                <p className="text-gray-600">Ticket ID: {analyzeMutation.data.ticket_id}</p>
              </div>
              <div className="text-center">
                <div className={`text-5xl font-bold text-${getQualityColor(analyzeMutation.data.overall_score)}`}>
                  {analyzeMutation.data.overall_score.toFixed(1)}
                </div>
                <div className="text-sm text-gray-600 mt-1">out of 100</div>
                <div className={`quality-badge ${analyzeMutation.data.quality_status.toLowerCase()} mt-2`}>
                  {analyzeMutation.data.quality_status}
                </div>
              </div>
            </div>

            {/* Automation Ready Banner */}
            <div className={`p-4 rounded-lg flex items-center gap-3 ${
              analyzeMutation.data.automation_ready 
                ? 'bg-green-50 border border-green-200' 
                : 'bg-yellow-50 border border-yellow-200'
            }`}>
              {analyzeMutation.data.automation_ready ? (
                <>
                  <CheckCircle className="h-6 w-6 text-green-600" />
                  <div>
                    <div className="font-semibold text-green-900">Automation Ready ✓</div>
                    <div className="text-sm text-green-700">
                      This ticket meets the quality threshold for AI automation
                    </div>
                  </div>
                </>
              ) : (
                <>
                  <AlertTriangle className="h-6 w-6 text-yellow-600" />
                  <div>
                    <div className="font-semibold text-yellow-900">Enrichment Needed</div>
                    <div className="text-sm text-yellow-700">
                      Score must be ≥70 for automation. Current: {analyzeMutation.data.overall_score.toFixed(1)}
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Dimension Scores */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(analyzeMutation.data.dimension_scores).map(([dimension, score]) => (
              <div key={dimension} className="dimension-card">
                <div className="text-sm font-medium text-gray-600 mb-2 capitalize">
                  {dimension.replace('_', ' ')}
                </div>
                <div className="flex items-end justify-between">
                  <div className="text-3xl font-bold text-gray-900">{score.toFixed(0)}</div>
                  <div className="text-sm text-gray-500">/ 100</div>
                </div>
                <div className="mt-3 progress-bar">
                  <div 
                    className={`progress-fill ${getQualityColor(score)}`}
                    style={{ width: `${score}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Deficiencies */}
          {analyzeMutation.data.deficiencies.length > 0 && (
            <div className="ticket-card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-red-500" />
                Identified Issues ({analyzeMutation.data.deficiencies.length})
              </h3>
              <div className="issue-list">
                {analyzeMutation.data.deficiencies.map((issue, index) => (
                  <div key={index} className="issue-item">
                    <span className="text-red-500">•</span>
                    <span>{issue}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {analyzeMutation.data.recommendations && analyzeMutation.data.recommendations.length > 0 && (
            <div className="ticket-card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-blue-500" />
                Improvement Recommendations ({analyzeMutation.data.recommendations.length})
              </h3>
              <div className="space-y-2">
                {analyzeMutation.data.recommendations.map((rec, index) => (
                  <div key={index} className="flex items-start gap-2 text-sm text-gray-700 bg-blue-50 p-3 rounded">
                    <span className="font-semibold text-blue-600">{index + 1}.</span>
                    <span>{rec}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error */}
      {analyzeMutation.isError && (
        <div className="ticket-card bg-red-50 border border-red-200">
          <div className="flex items-center gap-2 text-red-800">
            <AlertTriangle className="h-5 w-5" />
            <span className="font-semibold">Analysis Failed</span>
          </div>
          <p className="text-sm text-red-700 mt-2">
            {(analyzeMutation.error as Error).message}
          </p>
        </div>
      )}
    </div>
  )
}
