'use client';

import { CheckCircle2, Clock, AlertCircle } from 'lucide-react';
import type { RemediationAction } from '@/types';

interface RemediationPlanProps {
  plan: RemediationAction[];
}

export default function RemediationPlan({ plan }: RemediationPlanProps) {
  if (plan.length === 0) {
    return (
      <div className="text-center py-12">
        <CheckCircle2 className="w-16 h-16 mx-auto mb-4 text-green-500" />
        <p className="text-gray-400 text-lg">No remediation actions required</p>
      </div>
    );
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'immediate':
        return 'bg-red-500/20 text-red-400 border-red-500/50';
      case 'urgent':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/50';
      default:
        return 'bg-blue-500/20 text-blue-400 border-blue-500/50';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'immediate':
        return <AlertCircle className="w-5 h-5" />;
      case 'urgent':
        return <Clock className="w-5 h-5" />;
      default:
        return <CheckCircle2 className="w-5 h-5" />;
    }
  };

  return (
    <div className="space-y-4">
      {plan.map((action, index) => (
        <div key={index} className="glass rounded-lg p-6 border border-gray-700">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg border ${getPriorityColor(action.priority)}`}>
                {getPriorityIcon(action.priority)}
              </div>
              <div>
                <h3 className="font-semibold text-lg">
                  {action.credential_type.replace(/_/g, ' ').toUpperCase()}
                </h3>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`text-xs px-2 py-1 rounded border ${getPriorityColor(action.priority)}`}>
                    {action.priority.toUpperCase()}
                  </span>
                  <span className="text-xs text-gray-400">Timeline: {action.timeline}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Immediate Actions */}
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-purple-400 mb-2">Immediate Actions</h4>
            <ul className="space-y-1">
              {action.immediate_actions.map((act, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-gray-300">
                  <span className="text-purple-400 mt-1">→</span>
                  <span>{act}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Verification Steps */}
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-blue-400 mb-2">Verification Steps</h4>
            <ul className="space-y-1">
              {action.verification_steps.map((step, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-gray-300">
                  <span className="text-blue-400 mt-1">✓</span>
                  <span>{step}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Prevention Measures */}
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-green-400 mb-2">Prevention Measures</h4>
            <ul className="space-y-1">
              {action.prevention.map((measure, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-gray-300">
                  <span className="text-green-400 mt-1">●</span>
                  <span>{measure}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Notification Template */}
          {action.notification_template && (
            <div className="bg-black/30 rounded p-4 border-l-4 border-yellow-500">
              <h4 className="text-sm font-semibold text-yellow-400 mb-2">Notification Template</h4>
              <p className="text-sm text-gray-300 whitespace-pre-wrap">
                {action.notification_template}
              </p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
