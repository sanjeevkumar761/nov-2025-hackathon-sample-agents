'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Loader2, TrendingUp, CheckCircle, AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';
import type { GitLabProject, GitLabMilestone, SprintSummary } from '@/types';

interface SprintAnalyzerProps {
  project: GitLabProject;
}

export default function SprintAnalyzer({ project }: SprintAnalyzerProps) {
  const [selectedMilestone, setSelectedMilestone] = useState<number | null>(null);
  const [result, setResult] = useState<SprintSummary | null>(null);

  const { data: milestones, isLoading } = useQuery({
    queryKey: ['milestones', project.id],
    queryFn: () => api.listMilestones(project.id),
  });

  const summarizeMutation = useMutation({
    mutationFn: (data: { project_id: number; milestone_id: number }) =>
      api.summarizeSprint(data),
    onSuccess: (data) => {
      setResult(data);
    },
  });

  const handleAnalyze = () => {
    if (!selectedMilestone) return;
    summarizeMutation.mutate({
      project_id: project.id,
      milestone_id: selectedMilestone,
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Sprint Analyzer</h2>
        <p className="text-gray-600">
          Get AI-powered sprint summaries with velocity, completion rates, and actionable recommendations.
        </p>
      </div>

      {/* Milestone Selection */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Sprint / Milestone
        </label>
        {isLoading ? (
          <div className="flex items-center text-gray-600">
            <Loader2 className="w-5 h-5 mr-2 animate-spin" />
            Loading milestones...
          </div>
        ) : (
          <>
            <select
              value={selectedMilestone || ''}
              onChange={(e) => setSelectedMilestone(parseInt(e.target.value) || null)}
              className="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
            >
              <option value="">-- Select a milestone --</option>
              {milestones?.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.title} ({m.state}) {m.due_date ? `- Due: ${m.due_date}` : ''}
                </option>
              ))}
            </select>

            <button
              onClick={handleAnalyze}
              disabled={!selectedMilestone || summarizeMutation.isPending}
              className="mt-4 w-full flex items-center justify-center px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition"
            >
              {summarizeMutation.isPending ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Analyzing Sprint...
                </>
              ) : (
                <>
                  <TrendingUp className="w-5 h-5 mr-2" />
                  Analyze Sprint
                </>
              )}
            </button>
          </>
        )}
      </div>

      {/* Error */}
      {summarizeMutation.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">
            Analysis failed: {(summarizeMutation.error as Error).message}
          </p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6 fade-in">
          {/* Assessment Banner */}
          <div className={`rounded-lg p-6 ${
            result.assessment === 'Good' ? 'bg-green-50 border border-green-200' :
            result.assessment === 'Fair' ? 'bg-yellow-50 border border-yellow-200' :
            'bg-red-50 border border-red-200'
          }`}>
            <h3 className="text-2xl font-bold mb-2">
              {result.milestone_title}
            </h3>
            <div className="flex items-center space-x-2">
              {result.assessment === 'Good' ? (
                <CheckCircle className="w-6 h-6 text-green-600" />
              ) : (
                <AlertCircle className="w-6 h-6 text-yellow-600" />
              )}
              <span className="text-lg font-semibold">
                Assessment: {result.assessment}
              </span>
            </div>
          </div>

          {/* Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard
              label="Velocity"
              value={result.metrics.velocity}
              unit="pts"
              color="blue"
            />
            <MetricCard
              label="Completion"
              value={Math.round(result.metrics.completion_rate * 100)}
              unit="%"
              color="green"
            />
            <MetricCard
              label="Completed"
              value={`${result.metrics.completed_issues}/${result.metrics.total_issues}`}
              unit="issues"
              color="purple"
            />
            <MetricCard
              label="MRs"
              value={result.metrics.merge_requests}
              unit=""
              color="orange"
            />
          </div>

          {/* Achievements */}
          {result.achievements.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-3">
                🎯 Key Achievements
              </h4>
              <ul className="space-y-2">
                {result.achievements.map((achievement, idx) => (
                  <li key={idx} className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{achievement}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Blockers */}
          {result.blockers.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <h4 className="text-lg font-semibold text-red-900 mb-3">
                🚧 Blockers & Risks
              </h4>
              <ul className="space-y-2">
                {result.blockers.map((blocker, idx) => (
                  <li key={idx} className="flex items-start">
                    <AlertCircle className="w-5 h-5 text-red-600 mr-2 mt-0.5 flex-shrink-0" />
                    <span className="text-red-800">{blocker}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {result.recommendations.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h4 className="text-lg font-semibold text-blue-900 mb-3">
                💡 Recommendations
              </h4>
              <ul className="space-y-2">
                {result.recommendations.map((rec, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="w-5 h-5 text-blue-600 mr-2 font-bold">{idx + 1}.</span>
                    <span className="text-blue-800">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Full Report */}
          <details className="bg-white border border-gray-200 rounded-lg">
            <summary className="px-6 py-4 cursor-pointer hover:bg-gray-50 font-medium">
              View Full Markdown Report
            </summary>
            <div className="px-6 py-4 bg-gray-50">
              <pre className="whitespace-pre-wrap text-sm text-gray-800">
                {result.report_markdown}
              </pre>
            </div>
          </details>
        </div>
      )}
    </div>
  );
}

function MetricCard({ label, value, unit, color }: any) {
  return (
    <div className={`bg-${color}-50 border border-${color}-200 rounded-lg p-4`}>
      <p className="text-sm font-medium text-gray-600">{label}</p>
      <p className="text-2xl font-bold text-gray-900 mt-1">
        {value} <span className="text-sm font-normal text-gray-600">{unit}</span>
      </p>
    </div>
  );
}
