'use client';

import { History, Trash2, RefreshCw, AlertTriangle } from 'lucide-react';
import type { ScanListItem } from '@/types';

interface ScanHistoryProps {
  scans: ScanListItem[];
  onScanSelect: (scanId: string) => void;
  onScanDelete: (scanId: string) => void;
  onRefresh: () => void;
}

export default function ScanHistory({
  scans,
  onScanSelect,
  onScanDelete,
  onRefresh
}: ScanHistoryProps) {
  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'high':
        return 'text-red-400 bg-red-500/20';
      case 'medium':
        return 'text-orange-400 bg-orange-500/20';
      case 'low':
        return 'text-green-400 bg-green-500/20';
      default:
        return 'text-gray-400 bg-gray-500/20';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-400';
      case 'analyzing':
        return 'text-blue-400';
      case 'failed':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="glass-card rounded-2xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <History className="w-6 h-6 text-purple-400" />
          <h2 className="text-2xl font-bold">Scan History</h2>
        </div>
        <button
          onClick={onRefresh}
          className="glass px-4 py-2 rounded-lg hover:bg-white/10 transition-colors flex items-center gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {scans.length === 0 ? (
        <div className="text-center py-12">
          <History className="w-16 h-16 mx-auto mb-4 text-gray-600" />
          <p className="text-gray-400 text-lg">No scans yet</p>
          <p className="text-gray-500 text-sm mt-2">
            Start by submitting content for scanning
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {scans.map((scan) => (
            <div
              key={scan.scan_id}
              className="glass rounded-lg p-4 hover:bg-white/5 transition-colors border border-gray-700"
            >
              <div className="flex items-center justify-between">
                <div
                  className="flex-1 cursor-pointer"
                  onClick={() => scan.status === 'completed' && onScanSelect(scan.scan_id)}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-sm text-gray-500 font-mono">
                      {scan.scan_id.slice(0, 8)}...
                    </span>
                    <span className="text-xs px-2 py-1 rounded bg-purple-500/20 text-purple-400">
                      {scan.content_type}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded ${getStatusColor(scan.status)}`}>
                      {scan.status}
                    </span>
                  </div>

                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-gray-400">
                      {new Date(scan.submitted_at).toLocaleString()}
                    </span>
                    {scan.status === 'completed' && (
                      <>
                        <span className="text-gray-400">
                          {scan.credentials_found} credentials
                        </span>
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${getRiskColor(scan.overall_risk)}`}>
                          {scan.overall_risk.toUpperCase()}
                        </span>
                      </>
                    )}
                  </div>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (confirm('Delete this scan?')) {
                      onScanDelete(scan.scan_id);
                    }
                  }}
                  className="ml-4 p-2 rounded-lg hover:bg-red-500/20 text-gray-400 hover:text-red-400 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
