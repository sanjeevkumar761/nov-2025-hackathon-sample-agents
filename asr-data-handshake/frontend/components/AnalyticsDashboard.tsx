'use client'

import { useQuery } from '@tanstack/react-query'
import { getAnalyticsSummary } from '@/lib/api'
import { BarChart3, TrendingUp, DollarSign } from 'lucide-react'

export default function AnalyticsDashboard() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => getAnalyticsSummary('last_30_days'),
  })

  if (isLoading) {
    return <div className="ticket-card">Loading analytics...</div>
  }

  return (
    <div className="space-y-6">
      <div className="ticket-card">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Quality Analytics Dashboard</h2>
        <p className="text-gray-600">
          Period: {analytics?.period || 'Last 30 days'}
        </p>
      </div>

      {/* Overall Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="metric-card border-l-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-600">Avg Quality Score</div>
              <div className="text-3xl font-bold text-gray-900">
                {analytics?.overall_statistics.avg_score.toFixed(1) || '0'}
              </div>
            </div>
            <BarChart3 className="h-8 w-8 text-blue-500" />
          </div>
        </div>

        <div className="metric-card border-l-green-500">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-600">Threshold Met</div>
              <div className="text-3xl font-bold text-gray-900">
                {analytics?.overall_statistics.threshold_met_percentage.toFixed(1) || '0'}%
              </div>
            </div>
            <TrendingUp className="h-8 w-8 text-green-500" />
          </div>
        </div>

        <div className="metric-card border-l-yellow-500">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-600">Tickets Analyzed</div>
              <div className="text-3xl font-bold text-gray-900">
                {analytics?.total_tickets_analyzed.toLocaleString() || '0'}
              </div>
            </div>
            <BarChart3 className="h-8 w-8 text-yellow-500" />
          </div>
        </div>

        <div className="metric-card border-l-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-600">Cost Savings</div>
              <div className="text-3xl font-bold text-gray-900">
                ${(analytics?.enrichment_roi?.cost_savings_usd || 0).toLocaleString()}
              </div>
            </div>
            <DollarSign className="h-8 w-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Dimension Breakdown */}
      <div className="ticket-card">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Dimension Breakdown</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {analytics && Object.entries(analytics.dimension_breakdown).map(([dimension, data]) => (
            <div key={dimension} className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <div className="font-semibold text-gray-900 capitalize">
                  {dimension.replace('_', ' ')}
                </div>
                <div className="text-2xl font-bold text-snow-primary">
                  {data.avg_score.toFixed(1)}
                </div>
              </div>
              <div className="space-y-1">
                <div className="text-sm font-medium text-gray-600">Common Issues:</div>
                {data.common_issues.slice(0, 3).map((issue, i) => (
                  <div key={i} className="text-xs text-gray-600">• {issue}</div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
