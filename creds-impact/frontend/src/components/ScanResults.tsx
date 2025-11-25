'use client';

import { useState } from 'react';
import { AlertTriangle, CheckCircle2, Shield, ChevronDown, ChevronUp } from 'lucide-react';
import type { ScanResult } from '@/types';
import CredentialsList from './CredentialsList';
import RiskDashboard from './RiskDashboard';
import RemediationPlan from './RemediationPlan';
import ExecutiveReport from './ExecutiveReport';

interface ScanResultsProps {
  result: ScanResult;
  onNewScan: () => void;
}

export default function ScanResults({ result, onNewScan }: ScanResultsProps) {
  const [activeTab, setActiveTab] = useState<'credentials' | 'risk' | 'remediation' | 'report'>('credentials');

  const { scan_summary } = result;
  const riskColor =
    scan_summary.overall_risk === 'high'
      ? 'text-risk-high'
      : scan_summary.overall_risk === 'medium'
      ? 'text-risk-medium'
      : 'text-risk-low';

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <div className="glass-card rounded-2xl p-6">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold mb-2">Scan Results</h2>
            <p className="text-gray-400">Scan ID: {result.scan_id}</p>
            <p className="text-sm text-gray-500">{new Date(result.timestamp).toLocaleString()}</p>
          </div>
          <button
            onClick={onNewScan}
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold py-2 px-4 rounded-lg"
          >
            New Scan
          </button>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="glass rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-white">
              {scan_summary.credentials_found}
            </div>
            <div className="text-sm text-gray-400 mt-1">Credentials Found</div>
          </div>
          
          <div className="glass rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-risk-high">
              {scan_summary.high_risk}
            </div>
            <div className="text-sm text-gray-400 mt-1">High Risk</div>
          </div>
          
          <div className="glass rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-risk-medium">
              {scan_summary.medium_risk}
            </div>
            <div className="text-sm text-gray-400 mt-1">Medium Risk</div>
          </div>
          
          <div className="glass rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-risk-low">
              {scan_summary.low_risk}
            </div>
            <div className="text-sm text-gray-400 mt-1">Low Risk</div>
          </div>
          
          <div className="glass rounded-lg p-4 text-center">
            <div className={`text-3xl font-bold uppercase ${riskColor}`}>
              {scan_summary.overall_risk}
            </div>
            <div className="text-sm text-gray-400 mt-1">Overall Risk</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="glass-card rounded-2xl">
        <div className="flex border-b border-gray-700">
          <button
            onClick={() => setActiveTab('credentials')}
            className={`flex-1 py-4 px-6 font-semibold transition-colors ${
              activeTab === 'credentials'
                ? 'text-purple-400 border-b-2 border-purple-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Credentials ({result.detected_credentials.length})
          </button>
          <button
            onClick={() => setActiveTab('risk')}
            className={`flex-1 py-4 px-6 font-semibold transition-colors ${
              activeTab === 'risk'
                ? 'text-purple-400 border-b-2 border-purple-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Risk Assessment
          </button>
          <button
            onClick={() => setActiveTab('remediation')}
            className={`flex-1 py-4 px-6 font-semibold transition-colors ${
              activeTab === 'remediation'
                ? 'text-purple-400 border-b-2 border-purple-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Remediation ({result.remediation_plan.length})
          </button>
          <button
            onClick={() => setActiveTab('report')}
            className={`flex-1 py-4 px-6 font-semibold transition-colors ${
              activeTab === 'report'
                ? 'text-purple-400 border-b-2 border-purple-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Executive Report
          </button>
        </div>

        <div className="p-6">
          {activeTab === 'credentials' && (
            <CredentialsList credentials={result.detected_credentials} />
          )}
          {activeTab === 'risk' && (
            <RiskDashboard
              riskAssessment={result.risk_assessment}
              credentials={result.detected_credentials}
            />
          )}
          {activeTab === 'remediation' && (
            <RemediationPlan plan={result.remediation_plan} />
          )}
          {activeTab === 'report' && (
            <ExecutiveReport report={result.executive_report} />
          )}
        </div>
      </div>
    </div>
  );
}
