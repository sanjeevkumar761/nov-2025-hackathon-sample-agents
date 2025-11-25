'use client';

import { Activity, CheckCircle2, AlertCircle, XCircle } from 'lucide-react';
import type { HealthResponse } from '@/types';

interface HeaderProps {
  health?: HealthResponse;
}

export default function Header({ health }: HeaderProps) {
  const getStatusIcon = () => {
    if (!health) return <Activity className="w-5 h-5 animate-pulse" />;
    
    switch (health.status) {
      case 'healthy':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'degraded':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      default:
        return <XCircle className="w-5 h-5 text-red-500" />;
    }
  };

  const getStatusText = () => {
    if (!health) return 'Checking...';
    return health.status.charAt(0).toUpperCase() + health.status.slice(1);
  };

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg">
              <svg
                className="w-8 h-8 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                GitLab Interrogator
              </h1>
              <p className="text-sm text-gray-600">AI Scrum Master Digital Employee</p>
            </div>
          </div>

          {/* Status Indicator */}
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-2 px-3 py-2 bg-gray-50 rounded-lg">
              {getStatusIcon()}
              <span className="text-sm font-medium text-gray-700">
                {getStatusText()}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
