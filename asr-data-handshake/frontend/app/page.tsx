'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { healthCheck } from '@/lib/api'
import Header from '@/components/Header'
import ModuleTabs from '@/components/ModuleTabs'
import TicketAnalyzer from '@/components/TicketAnalyzer'
import TicketEnricher from '@/components/TicketEnricher'
import BatchProcessor from '@/components/BatchProcessor'
import AnalyticsDashboard from '@/components/AnalyticsDashboard'
import type { ModuleTab } from '@/types'
import { AlertCircle } from 'lucide-react'

export default function Home() {
  const [currentModule, setCurrentModule] = useState<ModuleTab>('analyzer')

  // Health check
  const { data: health, isLoading: healthLoading } = useQuery({
    queryKey: ['health'],
    queryFn: healthCheck,
    refetchInterval: 30000, // Check every 30 seconds
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-snow-light to-white">
      <Header health={health} healthLoading={healthLoading} />
      
      <main className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12 animate-fade-in">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            ASR Data Enrichment Handshake
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            AI-powered ServiceNow ticket enhancement to enable agentic automation
          </p>
          <div className="mt-6 inline-flex items-center gap-4 bg-white px-6 py-3 rounded-lg shadow-md">
            <div className="text-center">
              <div className="text-3xl font-bold text-quality-poor">2.6%</div>
              <div className="text-sm text-gray-600">Current Quality</div>
            </div>
            <div className="text-2xl text-gray-400">→</div>
            <div className="text-center">
              <div className="text-3xl font-bold text-quality-excellent">95%+</div>
              <div className="text-sm text-gray-600">Target Quality</div>
            </div>
          </div>
        </div>

        {/* Warning if API is down */}
        {health?.status !== 'healthy' && !healthLoading && (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6 animate-slide-up">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-yellow-400 mr-2" />
              <p className="text-yellow-700">
                {health?.status === 'degraded' 
                  ? 'API is degraded. Some features may not work properly.'
                  : 'Cannot connect to backend API. Please ensure the server is running.'}
              </p>
            </div>
          </div>
        )}

        {/* Module Tabs */}
        <ModuleTabs currentModule={currentModule} onModuleChange={setCurrentModule} />

        {/* Module Content */}
        <div className="mt-8 animate-fade-in">
          {currentModule === 'analyzer' && <TicketAnalyzer />}
          {currentModule === 'enrichment' && <TicketEnricher />}
          {currentModule === 'batch' && <BatchProcessor />}
          {currentModule === 'analytics' && <AnalyticsDashboard />}
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <div className="ticket-card">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">📊 Quality Dimensions</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Short Description (25%)</li>
              <li>• Long Description (30%)</li>
              <li>• Categorization (25%)</li>
              <li>• Resolution Detail (20%)</li>
            </ul>
          </div>

          <div className="ticket-card">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">🎯 Quality Threshold</h3>
            <p className="text-sm text-gray-600">
              Minimum score of <span className="font-bold text-snow-primary">70/100</span> required 
              for AI automation readiness
            </p>
            <div className="mt-3 space-y-1 text-xs text-gray-500">
              <div>🔴 0-40: Poor (blocks automation)</div>
              <div>🟡 41-70: Fair (needs enrichment)</div>
              <div>🟢 71-90: Good (automation-ready)</div>
              <div>⭐ 91-100: Excellent (best practice)</div>
            </div>
          </div>

          <div className="ticket-card">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">⚡ Impact</h3>
            <div className="text-sm text-gray-600 space-y-1">
              <div><span className="font-semibold">15,000+</span> hours saved/year</div>
              <div><span className="font-semibold">$1.5M+</span> cost savings</div>
              <div><span className="font-semibold">97.4%</span> automation enablement</div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-16 text-center text-gray-500 text-sm pb-8">
          <p>ASR Data Enrichment • Powered by LangGraph, Azure OpenAI & ServiceNow API</p>
          <p className="mt-2">Transforming ticket quality from 2.6% to 95%+ for true agentic AI automation</p>
        </footer>
      </main>
    </div>
  )
}
