'use client'

import React from 'react'
import { RiskAssessment as RiskAssessmentType } from '@/types'
import { AlertTriangle, AlertOctagon, Info, TrendingUp } from 'lucide-react'

interface RiskAssessmentProps {
  riskAssessment: RiskAssessmentType
}

export default function RiskAssessment({ riskAssessment }: RiskAssessmentProps) {
  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'high':
        return 'bg-red-50 border-red-300 text-red-700'
      case 'medium':
        return 'bg-amber-50 border-amber-300 text-amber-700'
      case 'low':
        return 'bg-gray-50 border-gray-300 text-gray-700'
      default:
        return 'bg-gray-50 border-gray-300 text-gray-700'
    }
  }

  const getRiskIcon = (level: string) => {
    switch (level.toLowerCase()) {
      case 'high':
        return <AlertOctagon className="w-6 h-6 text-red-600" />
      case 'medium':
        return <AlertTriangle className="w-6 h-6 text-amber-600" />
      case 'low':
        return <Info className="w-6 h-6 text-gray-600" />
      default:
        return <Info className="w-6 h-6 text-gray-600" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Overall Risk Level */}
      <div className={`border-2 rounded-lg p-6 ${getRiskColor(riskAssessment.overall_risk_level)}`}>
        <div className="flex items-center gap-3">
          {getRiskIcon(riskAssessment.overall_risk_level)}
          <div>
            <h3 className="text-2xl font-bold">
              Overall Risk Level: {riskAssessment.overall_risk_level.toUpperCase()}
            </h3>
            <p className="text-sm mt-1 opacity-80">
              Based on analysis of {riskAssessment.high_risks.length + riskAssessment.medium_risks.length + riskAssessment.low_risks.length} identified risks
            </p>
          </div>
        </div>
      </div>

      {/* High Risks */}
      {riskAssessment.high_risks.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-xl font-bold text-red-700 flex items-center gap-2">
            <AlertOctagon className="w-5 h-5" />
            High Priority Risks ({riskAssessment.high_risks.length})
          </h4>
          {riskAssessment.high_risks.map((risk, idx) => (
            <div key={idx} className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <AlertOctagon className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <p className="text-red-800 font-medium">{risk}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Medium Risks */}
      {riskAssessment.medium_risks.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-xl font-bold text-amber-700 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            Medium Priority Risks ({riskAssessment.medium_risks.length})
          </h4>
          {riskAssessment.medium_risks.map((risk, idx) => (
            <div key={idx} className="bg-amber-50 border-2 border-amber-300 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                <p className="text-amber-800 font-medium">{risk}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Low Risks */}
      {riskAssessment.low_risks.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-xl font-bold text-gray-700 flex items-center gap-2">
            <Info className="w-5 h-5" />
            Low Priority Risks ({riskAssessment.low_risks.length})
          </h4>
          {riskAssessment.low_risks.map((risk, idx) => (
            <div key={idx} className="bg-gray-50 border-2 border-gray-300 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Info className="w-5 h-5 text-gray-600 flex-shrink-0 mt-0.5" />
                <p className="text-gray-800 font-medium">{risk}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4 mt-6">
        <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 text-center">
          <p className="text-3xl font-bold text-red-700">{riskAssessment.high_risks.length}</p>
          <p className="text-sm text-red-600 font-semibold mt-1">High Risks</p>
        </div>
        <div className="bg-amber-50 border-2 border-amber-300 rounded-lg p-4 text-center">
          <p className="text-3xl font-bold text-amber-700">{riskAssessment.medium_risks.length}</p>
          <p className="text-sm text-amber-600 font-semibold mt-1">Medium Risks</p>
        </div>
        <div className="bg-gray-50 border-2 border-gray-300 rounded-lg p-4 text-center">
          <p className="text-3xl font-bold text-gray-700">{riskAssessment.low_risks.length}</p>
          <p className="text-sm text-gray-600 font-semibold mt-1">Low Risks</p>
        </div>
      </div>
    </div>
  )
}
