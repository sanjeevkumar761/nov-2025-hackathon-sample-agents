'use client'

import { FileSearch, Sparkles, Files, BarChart3 } from 'lucide-react'
import type { ModuleTab } from '@/types'

interface ModuleTabsProps {
  currentModule: ModuleTab
  onModuleChange: (module: ModuleTab) => void
}

const tabs = [
  { id: 'analyzer' as ModuleTab, label: 'Ticket Analyzer', icon: FileSearch, description: 'Analyze ticket quality' },
  { id: 'enrichment' as ModuleTab, label: 'Enrich Ticket', icon: Sparkles, description: 'AI-powered enrichment' },
  { id: 'batch' as ModuleTab, label: 'Batch Processing', icon: Files, description: 'Enrich multiple tickets' },
  { id: 'analytics' as ModuleTab, label: 'Analytics', icon: BarChart3, description: 'Quality insights' },
]

export default function ModuleTabs({ currentModule, onModuleChange }: ModuleTabsProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm p-2">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = currentModule === tab.id
          
          return (
            <button
              key={tab.id}
              onClick={() => onModuleChange(tab.id)}
              className={`
                flex flex-col items-center gap-2 p-4 rounded-lg transition-all
                ${isActive 
                  ? 'bg-snow-primary text-white shadow-md' 
                  : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                }
              `}
            >
              <Icon className="h-6 w-6" />
              <div className="text-center">
                <div className="font-medium text-sm">{tab.label}</div>
                <div className={`text-xs mt-1 ${isActive ? 'text-white/80' : 'text-gray-500'}`}>
                  {tab.description}
                </div>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
