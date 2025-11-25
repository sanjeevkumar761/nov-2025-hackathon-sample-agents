'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Loader2, CheckCircle, Sparkles } from 'lucide-react';
import { api } from '@/lib/api';
import type { GitLabProject, StoryCreationResult } from '@/types';

interface StoryCreatorProps {
  project: GitLabProject;
}

export default function StoryCreator({ project }: StoryCreatorProps) {
  const [requirement, setRequirement] = useState('');
  const [context, setContext] = useState('');
  const [result, setResult] = useState<StoryCreationResult | null>(null);

  const createStoryMutation = useMutation({
    mutationFn: (data: { requirement: string; project_id: number; context?: string }) =>
      api.createUserStory(data),
    onSuccess: (data) => {
      setResult(data);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!requirement.trim()) return;

    createStoryMutation.mutate({
      requirement,
      project_id: project.id,
      context: context || undefined,
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Create User Story
        </h2>
        <p className="text-gray-600">
          Describe your requirements, and AI will generate a properly formatted user story
          with acceptance criteria and story points.
        </p>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="requirement"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Requirement Description <span className="text-red-500">*</span>
          </label>
          <textarea
            id="requirement"
            value={requirement}
            onChange={(e) => setRequirement(e.target.value)}
            rows={6}
            className="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Example: Users should be able to reset their password using their email address. The system should send a secure reset link that expires after 1 hour."
            required
          />
          <p className="mt-2 text-sm text-gray-500">
            Describe what you need built. Be as detailed as possible.
          </p>
        </div>

        <div>
          <label
            htmlFor="context"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Additional Context (Optional)
          </label>
          <textarea
            id="context"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            rows={3}
            className="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Add any relevant background, constraints, or dependencies..."
          />
        </div>

        <button
          type="submit"
          disabled={createStoryMutation.isPending || !requirement.trim()}
          className="w-full flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
        >
          {createStoryMutation.isPending ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Generating Story...
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5 mr-2" />
              Generate User Story
            </>
          )}
        </button>
      </form>

      {/* Error */}
      {createStoryMutation.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">
            Failed to generate story: {(createStoryMutation.error as Error).message}
          </p>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="bg-white border border-gray-200 rounded-lg shadow-md overflow-hidden fade-in">
          {/* Success Header */}
          <div className="bg-green-50 border-b border-green-200 px-6 py-4 flex items-center">
            <CheckCircle className="w-6 h-6 text-green-600 mr-3" />
            <div>
              <h3 className="text-lg font-semibold text-green-900">
                User Story Generated!
              </h3>
              <p className="text-sm text-green-700">
                Task ID: {result.task_id}
              </p>
            </div>
          </div>

          {/* Story Content */}
          <div className="p-6 space-y-6">
            {/* Title */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Title
              </label>
              <div className="px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg">
                <p className="text-gray-900 font-semibold">{result.title}</p>
              </div>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <div className="px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg">
                <div className="markdown-content whitespace-pre-wrap text-gray-900">
                  {result.description}
                </div>
              </div>
            </div>

            {/* Metadata */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Story Points
                </label>
                <div className="px-4 py-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-2xl font-bold text-blue-900">
                    {result.story_points}
                  </p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Labels
                </label>
                <div className="px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg">
                  <div className="flex flex-wrap gap-2">
                    {result.labels.map((label, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                      >
                        {label}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* GitLab Payload */}
            <details className="border border-gray-200 rounded-lg">
              <summary className="px-4 py-3 cursor-pointer hover:bg-gray-50 font-medium text-gray-700">
                GitLab Issue Payload (JSON)
              </summary>
              <div className="px-4 py-3 bg-gray-900 text-gray-100">
                <pre className="text-sm overflow-x-auto">
                  {JSON.stringify(result.gitlab_payload, null, 2)}
                </pre>
              </div>
            </details>

            {/* Execution Trace */}
            {result.execution_trace && result.execution_trace.length > 0 && (
              <details className="border border-gray-200 rounded-lg">
                <summary className="px-4 py-3 cursor-pointer hover:bg-gray-50 font-medium text-gray-700">
                  Execution Trace ({result.execution_trace.length} steps)
                </summary>
                <div className="px-4 py-3 space-y-2">
                  {result.execution_trace.map((step, idx) => (
                    <div
                      key={idx}
                      className="flex items-start space-x-3 text-sm"
                    >
                      <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center font-medium">
                        {step.step}
                      </span>
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{step.node}</p>
                        <p className="text-gray-600">{step.action}</p>
                        <p className="text-xs text-gray-500">
                          {step.duration_ms}ms
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </details>
            )}
          </div>

          {/* Actions */}
          <div className="bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-end space-x-3">
            <button
              onClick={() => {
                navigator.clipboard.writeText(result.description);
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition"
            >
              Copy Description
            </button>
            <button
              onClick={() => {
                navigator.clipboard.writeText(JSON.stringify(result.gitlab_payload, null, 2));
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Copy GitLab Payload
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
