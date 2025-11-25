'use client';

import { Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { AlertTriangle, Shield } from 'lucide-react';
import type { RiskAssessment, CredentialFinding } from '@/types';

ChartJS.register(
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface RiskDashboardProps {
  riskAssessment: RiskAssessment;
  credentials: CredentialFinding[];
}

export default function RiskDashboard({ riskAssessment, credentials }: RiskDashboardProps) {
  // Risk distribution pie chart
  const riskDistributionData = {
    labels: ['High Risk', 'Medium Risk', 'Low Risk'],
    datasets: [
      {
        data: [
          riskAssessment.high_risk_count,
          riskAssessment.medium_risk_count,
          riskAssessment.low_risk_count
        ],
        backgroundColor: ['#ef4444', '#f97316', '#22c55e'],
        borderColor: ['#dc2626', '#ea580c', '#16a34a'],
        borderWidth: 2,
      },
    ],
  };

  // Credential types bar chart
  const credTypeCount = credentials.reduce((acc, cred) => {
    acc[cred.type] = (acc[cred.type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const credTypesData = {
    labels: Object.keys(credTypeCount).map(k => k.replace(/_/g, ' ')),
    datasets: [
      {
        label: 'Count',
        data: Object.values(credTypeCount),
        backgroundColor: '#8b5cf6',
        borderColor: '#7c3aed',
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#9ca3af',
        },
      },
    },
    scales: {
      y: {
        ticks: { color: '#9ca3af' },
        grid: { color: '#374151' },
      },
      x: {
        ticks: { color: '#9ca3af' },
        grid: { color: '#374151' },
      },
    },
  };

  return (
    <div className="space-y-6">
      {/* Overall Risk Banner */}
      <div className={`p-4 rounded-lg border-2 ${
        riskAssessment.overall_risk === 'high'
          ? 'bg-red-500/10 border-red-500/50'
          : riskAssessment.overall_risk === 'medium'
          ? 'bg-orange-500/10 border-orange-500/50'
          : 'bg-green-500/10 border-green-500/50'
      }`}>
        <div className="flex items-center gap-3">
          {riskAssessment.overall_risk === 'high' ? (
            <AlertTriangle className="w-8 h-8 text-red-400" />
          ) : (
            <Shield className="w-8 h-8 text-green-400" />
          )}
          <div>
            <div className="font-bold text-lg">
              Overall Risk Level: {riskAssessment.overall_risk.toUpperCase()}
            </div>
            <div className="text-sm text-gray-300">
              {riskAssessment.high_risk_count > 0 && (
                <span>Immediate action required for {riskAssessment.high_risk_count} high-risk findings</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Risk Distribution</h3>
          <div className="h-64">
            <Doughnut data={riskDistributionData} options={{ ...chartOptions, scales: undefined }} />
          </div>
        </div>

        <div className="glass rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Credential Types</h3>
          <div className="h-64">
            <Bar data={credTypesData} options={chartOptions} />
          </div>
        </div>
      </div>

      {/* Critical Findings */}
      {riskAssessment.critical_findings && riskAssessment.critical_findings.length > 0 && (
        <div className="glass rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            Critical Findings
          </h3>
          <ul className="space-y-2">
            {riskAssessment.critical_findings.map((finding, index) => (
              <li key={index} className="flex items-start gap-2 text-gray-300">
                <span className="text-red-400 mt-1">•</span>
                <span>{finding}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Compliance Violations */}
      {riskAssessment.compliance_violations && riskAssessment.compliance_violations.length > 0 && (
        <div className="glass rounded-lg p-6 border-orange-500/30">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Shield className="w-5 h-5 text-orange-400" />
            Compliance Violations
          </h3>
          <ul className="space-y-2">
            {riskAssessment.compliance_violations.map((violation, index) => (
              <li key={index} className="flex items-start gap-2 text-gray-300">
                <span className="text-orange-400 mt-1">•</span>
                <span>{violation}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
