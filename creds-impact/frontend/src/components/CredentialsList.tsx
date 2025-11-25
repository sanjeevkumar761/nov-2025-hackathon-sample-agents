'use client';

import { useState } from 'react';
import { AlertTriangle, Key, Code, ChevronDown, ChevronUp } from 'lucide-react';
import type { CredentialFinding } from '@/types';

interface CredentialsListProps {
  credentials: CredentialFinding[];
}

export default function CredentialsList({ credentials }: CredentialsListProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  if (credentials.length === 0) {
    return (
      <div className="text-center py-12">
        <Key className="w-16 h-16 mx-auto mb-4 text-gray-600" />
        <p className="text-gray-400 text-lg">No credentials detected</p>
        <p className="text-gray-500 text-sm mt-2">
          The content appears to be clean of exposed credentials.
        </p>
      </div>
    );
  }

  const getSeverityColor = (severity?: string) => {
    switch (severity) {
      case 'high':
        return 'text-risk-high bg-risk-high/10 border-risk-high/30';
      case 'medium':
        return 'text-risk-medium bg-risk-medium/10 border-risk-medium/30';
      case 'low':
        return 'text-risk-low bg-risk-low/10 border-risk-low/30';
      default:
        return 'text-gray-400 bg-gray-400/10 border-gray-400/30';
    }
  };

  const getMethodBadge = (method: string) => {
    return method === 'pattern' ? (
      <span className="text-xs px-2 py-1 rounded bg-blue-500/20 text-blue-400">Pattern</span>
    ) : (
      <span className="text-xs px-2 py-1 rounded bg-purple-500/20 text-purple-400">AI</span>
    );
  };

  return (
    <div className="space-y-3">
      {credentials.map((cred, index) => (
        <div
          key={index}
          className="glass rounded-lg border border-gray-700 overflow-hidden"
        >
          <div
            className="p-4 cursor-pointer hover:bg-white/5"
            onClick={() => setExpandedIndex(expandedIndex === index ? null : index)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <AlertTriangle className={`w-5 h-5 ${getSeverityColor(cred.severity).split(' ')[0]}`} />
                  <span className="font-semibold">{cred.type.replace(/_/g, ' ').toUpperCase()}</span>
                  {getMethodBadge(cred.detection_method)}
                  {cred.severity && (
                    <span className={`text-xs px-2 py-1 rounded border ${getSeverityColor(cred.severity)}`}>
                      {cred.severity.toUpperCase()}
                    </span>
                  )}
                </div>
                
                <div className="text-sm text-gray-400">
                  Line {cred.line} • Confidence: {(cred.confidence * 100).toFixed(0)}%
                  {cred.exposure_scope && ` • Exposure: ${cred.exposure_scope}`}
                </div>
              </div>

              {expandedIndex === index ? (
                <ChevronUp className="w-5 h-5 text-gray-400" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-400" />
              )}
            </div>
          </div>

          {expandedIndex === index && (
            <div className="px-4 pb-4 border-t border-gray-700 bg-black/20">
              <div className="mt-4 space-y-3">
                <div>
                  <div className="text-xs text-gray-500 mb-1">VALUE PREVIEW</div>
                  <code className="block bg-black/40 rounded px-3 py-2 text-sm font-mono text-yellow-400">
                    {cred.value}
                  </code>
                </div>

                <div>
                  <div className="text-xs text-gray-500 mb-1">CONTEXT</div>
                  <code className="block bg-black/40 rounded px-3 py-2 text-sm font-mono text-gray-300 whitespace-pre-wrap">
                    {cred.context}
                  </code>
                </div>

                {cred.is_active !== undefined && (
                  <div>
                    <div className="text-xs text-gray-500 mb-1">STATUS</div>
                    <span className={`text-sm ${cred.is_active ? 'text-red-400' : 'text-gray-400'}`}>
                      {cred.is_active ? '⚠️ Potentially Active' : '✓ Likely Expired'}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
