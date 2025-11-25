'use client'

import React, { useEffect, useState } from 'react'
import { getWorkflowGraph } from '@/lib/api'
import { WorkflowGraph } from '@/types'
import { Network, GitBranch, Loader2, AlertCircle } from 'lucide-react'

export default function WorkflowVisualization() {
  const [workflow, setWorkflow] = useState<WorkflowGraph | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadWorkflow()
  }, [])

  const loadWorkflow = async () => {
    try {
      const data = await getWorkflowGraph()
      setWorkflow(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load workflow')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 flex items-center gap-3">
        <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
        <span className="text-red-700 font-semibold">{error}</span>
      </div>
    )
  }

  if (!workflow) {
    return null
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 mb-4">
        <Network className="w-6 h-6 text-blue-600" />
        <h3 className="text-xl font-bold text-gray-800">
          {workflow.workflow_type} Workflow
        </h3>
        <span className="text-sm text-gray-500">
          {workflow.total_nodes} nodes, {workflow.total_edges} connections
        </span>
      </div>

      {/* Visual Workflow Display */}
      <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-6 border-2 border-blue-200">
        <div className="flex items-center justify-between gap-4">
          {workflow.nodes.map((node, idx) => (
            <React.Fragment key={node.id}>
              {/* Node */}
              <div className="flex-1 text-center">
                <div className="bg-white border-3 border-blue-500 rounded-lg p-4 shadow-lg">
                  <div className="w-12 h-12 mx-auto mb-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                    {idx + 1}
                  </div>
                  <p className="font-bold text-gray-800 text-sm">{node.name}</p>
                  {node.description && (
                    <p className="text-xs text-gray-600 mt-1">{node.description}</p>
                  )}
                </div>
              </div>

              {/* Arrow between nodes */}
              {idx < workflow.nodes.length - 1 && (
                <div className="flex-shrink-0">
                  <svg width="40" height="40" viewBox="0 0 40 40" className="text-blue-600">
                    <path
                      d="M5 20 L30 20 M30 20 L25 15 M30 20 L25 25"
                      stroke="currentColor"
                      strokeWidth="3"
                      fill="none"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Nodes List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {workflow.nodes.map((node, idx) => (
          <div key={node.id} className="bg-white border-2 border-gray-200 rounded-lg p-3">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                {idx + 1}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-gray-800 text-sm">{node.name}</p>
                {node.description && (
                  <p className="text-xs text-gray-600 mt-1">{node.description}</p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Edges List */}
      <div className="bg-gray-50 rounded-lg p-4 border-2 border-gray-200">
        <h4 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
          <GitBranch className="w-5 h-5" />
          Workflow Connections ({workflow.edges.length})
        </h4>
        <div className="space-y-2">
          {workflow.edges.map((edge, idx) => (
            <div key={idx} className="flex items-center gap-2 text-sm">
              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded font-mono text-xs">
                {edge.source}
              </span>
              <span className="text-gray-400">→</span>
              <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded font-mono text-xs">
                {edge.target}
              </span>
              {edge.label && (
                <span className="text-gray-600 text-xs">({edge.label})</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
