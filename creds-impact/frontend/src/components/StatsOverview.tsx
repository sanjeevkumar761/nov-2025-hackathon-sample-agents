'use client';

import { TrendingUp, AlertTriangle, Shield, Scan } from 'lucide-react';
import type { StatsResponse } from '@/types';

interface StatsOverviewProps {
  stats: StatsResponse;
}

export default function StatsOverview({ stats }: StatsOverviewProps) {
  return (
    <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="glass rounded-lg p-4">
        <div className="flex items-center gap-2 mb-2">
          <Scan className="w-4 h-4 text-purple-400" />
          <span className="text-xs text-gray-400">Total Scans</span>
        </div>
        <div className="text-2xl font-bold">{stats.total_scans}</div>
        <div className="text-xs text-gray-500 mt-1">
          {stats.completed_scans} completed
        </div>
      </div>

      <div className="glass rounded-lg p-4">
        <div className="flex items-center gap-2 mb-2">
          <TrendingUp className="w-4 h-4 text-blue-400" />
          <span className="text-xs text-gray-400">Total Findings</span>
        </div>
        <div className="text-2xl font-bold">{stats.total_credentials_found}</div>
        <div className="text-xs text-gray-500 mt-1">
          credentials detected
        </div>
      </div>

      <div className="glass rounded-lg p-4">
        <div className="flex items-center gap-2 mb-2">
          <AlertTriangle className="w-4 h-4 text-red-400" />
          <span className="text-xs text-gray-400">High Risk</span>
        </div>
        <div className="text-2xl font-bold text-red-400">{stats.high_risk_findings}</div>
        <div className="text-xs text-gray-500 mt-1">
          requires immediate action
        </div>
      </div>

      <div className="glass rounded-lg p-4">
        <div className="flex items-center gap-2 mb-2">
          <Shield className="w-4 h-4 text-orange-400" />
          <span className="text-xs text-gray-400">Medium Risk</span>
        </div>
        <div className="text-2xl font-bold text-orange-400">{stats.medium_risk_findings}</div>
        <div className="text-xs text-gray-500 mt-1">
          needs attention
        </div>
      </div>
    </div>
  );
}
