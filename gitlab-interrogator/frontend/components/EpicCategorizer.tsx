'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Loader2, FolderKanban, Tag } from 'lucide-react';
import { api } from '@/lib/api';
import type { GitLabProject, EpicCategorization } from '@/types';

interface EpicCategorizerProps {
  project: GitLabProject;
}

export default function EpicCategorizer({ project }: EpicCategorizerProps) {
  const [result, setResult] = useState<EpicCategorization | null>(null);

  const categorizeMutation = useMutation({
    mutationFn: (data: { project_id: number }) => api.categorizeEpics(data),
    onSuccess: (data) => {
      setResult(data);
    },
  });

  const handleCategorize = () => {
    categorizeMutation.mutate({ project_id: project.id });
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Epic Categorization
        </h2>
        <p className="text-gray-600">
          Use AI to semantically categorize epics by theme and organize your roadmap.
        </p>
      </div>

      {/* Action Button */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <button
          onClick={handleCategorize}
          disabled={categorizeMutation.isPending}
          className="w-full flex items-center justify-center px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-gray-400 transition"
        >
          {categorizeMutation.isPending ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Categorizing Epics...
            </>
          ) : (
            <>
              <FolderKanban className="w-5 h-5 mr-2" />
              Categorize Epics
            </>
          )}
        </button>
        <p className="text-sm text-gray-500 mt-2 text-center">
          This will analyze all epics in the project and group them by theme
        </p>
      </div>

      {/* Error */}
      {categorizeMutation.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">
            Failed: {(categorizeMutation.error as Error).message}
          </p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6 fade-in">
          {/* Summary */}
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
            <h3 className="text-xl font-bold text-orange-900 mb-2">
              Categorization Complete
            </h3>
            <p className="text-orange-700">
              Found {Object.keys(result.categorized).length} categories with{' '}
              {Object.values(result.categorized).reduce(
                (sum, epics) => sum + epics.length,
                0
              )}{' '}
              epics
            </p>
          </div>

          {/* Categories */}
          <div className="space-y-4">
            {Object.entries(result.categorized).map(([category, epics]) => (
              <div
                key={category}
                className="bg-white border border-gray-200 rounded-lg overflow-hidden"
              >
                <div className="bg-gradient-to-r from-orange-50 to-yellow-50 px-6 py-4 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <h4 className="text-lg font-semibold text-gray-900 flex items-center">
                      <Tag className="w-5 h-5 mr-2 text-orange-600" />
                      {category}
                    </h4>
                    <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-medium">
                      {epics.length} {epics.length === 1 ? 'epic' : 'epics'}
                    </span>
                  </div>
                </div>

                <div className="p-6 space-y-3">
                  {epics.map((epic: any) => (
                    <div
                      key={epic.id}
                      className="flex items-start justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                    >
                      <div className="flex-1">
                        <h5 className="font-medium text-gray-900">{epic.title}</h5>
                        {epic.rationale && (
                          <p className="text-sm text-gray-600 mt-1">
                            {epic.rationale}
                          </p>
                        )}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {Math.round(epic.confidence * 100)}%
                        </div>
                        <div className="text-xs text-gray-500">confidence</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* New Category Suggestions */}
          {result.new_category_suggestions &&
            result.new_category_suggestions.length > 0 && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h4 className="text-lg font-semibold text-blue-900 mb-3">
                  💡 Suggested New Categories
                </h4>
                <div className="flex flex-wrap gap-2">
                  {result.new_category_suggestions.map((suggestion, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                    >
                      {suggestion}
                    </span>
                  ))}
                </div>
              </div>
            )}

          {/* Markdown Output */}
          <details className="bg-white border border-gray-200 rounded-lg">
            <summary className="px-6 py-4 cursor-pointer hover:bg-gray-50 font-medium">
              View Markdown Report
            </summary>
            <div className="px-6 py-4 bg-gray-50">
              <pre className="whitespace-pre-wrap text-sm text-gray-800">
                {result.markdown}
              </pre>
            </div>
          </details>
        </div>
      )}
    </div>
  );
}
