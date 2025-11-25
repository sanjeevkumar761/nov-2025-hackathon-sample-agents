'use client'

import { Activity, CheckCircle, AlertCircle, XCircle } from 'lucide-react'
import type { HealthResponse } from '@/types'

interface HeaderProps {
  health?: HealthResponse
  healthLoading: boolean
}

export default function Header({ health, healthLoading }: HeaderProps) {
  const getStatusIcon = () => {
    if (healthLoading) {
      return <Activity className="h-5 w-5 text-gray-400 animate-pulse" />
    }
    
    switch (health?.status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'degraded':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />
      case 'down':
        return <XCircle className="h-5 w-5 text-red-500" />
      default:
        return <Activity className="h-5 w-5 text-gray-400" />
    }
  }

  const getStatusText = () => {
    if (healthLoading) return 'Checking...'
    return health?.status || 'Unknown'
  }

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-snow-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">ASR</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                ASR Data Enrichment
              </h1>
              <p className="text-sm text-gray-600">
                ServiceNow Ticket Quality Enhancement
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-gray-50 px-4 py-2 rounded-lg">
              {getStatusIcon()}
              <span className="text-sm font-medium text-gray-700 capitalize">
                {getStatusText()}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
