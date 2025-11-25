'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Loader2, FileText, Download } from 'lucide-react';
import { api } from '@/lib/api';
import type { GitLabProject, ReleaseNotes } from '@/types';

interface ReleaseNotesGeneratorProps {
  project: GitLabProject;
}

export default function ReleaseNotesGenerator({ project }: ReleaseNotesGeneratorProps) {
  const [tagName, setTagName] = useState('');
  const [since, setSince] = useState('');
  const [result, setResult] = useState<ReleaseNotes | null>(null);

  const generateMutation = useMutation({
    mutationFn: (data: any) => api.generateReleaseNotes(data),
    onSuccess: (data) => {
      setResult(data);
    },
  });

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault();
    generateMutation.mutate({
      project_id: project.id,
      tag_name: tagName,
      since: since || undefined,
    });
  };

  const downloadMarkdown = () => {
    if (!result) return;
    const blob = new Blob([result.markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `release-notes-${result.version}.md`;
    a.click();
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Release Notes Generator
        </h2>
        <p className="text-gray-600">
          Automatically generate professional release notes from commits and issues.
        </p>
      </div>

      {/* Input Form */}
      <form onSubmit={handleGenerate} className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Version / Tag Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={tagName}
            onChange={(e) => setTagName(e.target.value)}
            placeholder="v1.2.0"
            className="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Since Date (Optional)
          </label>
          <input
            type="date"
            value={since}
            onChange={(e) => setSince(e.target.value)}
            className="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
          />
          <p className="text-sm text-gray-500 mt-1">
            Fetch changes since this date. Leave empty for last 30 days.
          </p>
        </div>

        <button
          type="submit"
          disabled={generateMutation.isPending || !tagName}
          className="w-full flex items-center justify-center px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 transition"
        >
          {generateMutation.isPending ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Generating Release Notes...
            </>
          ) : (
            <>
              <FileText className="w-5 h-5 mr-2" />
              Generate Release Notes
            </>
          )}
        </button>
      </form>

      {/* Error */}
      {generateMutation.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">
            Failed: {(generateMutation.error as Error).message}
          </p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6 fade-in">
          {/* Header */}
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
            <h3 className="text-2xl font-bold text-purple-900">
              Release {result.version}
            </h3>
            <p className="text-purple-700">{result.date}</p>
            <p className="text-gray-700 mt-2">{result.summary}</p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Features" value={result.features.length} color="blue" />
            <StatCard label="Bug Fixes" value={result.fixes.length} color="green" />
            <StatCard label="Breaking" value={result.breaking_changes.length} color="red" />
            <StatCard label="Contributors" value={result.contributors.length} color="purple" />
          </div>

          {/* Features */}
          {result.features.length > 0 && (
            <ChangeSection
              title="✨ Features"
              items={result.features}
              color="blue"
            />
          )}

          {/* Fixes */}
          {result.fixes.length > 0 && (
            <ChangeSection
              title="🐛 Bug Fixes"
              items={result.fixes}
              color="green"
            />
          )}

          {/* Breaking Changes */}
          {result.breaking_changes.length > 0 && (
            <ChangeSection
              title="⚠️ Breaking Changes"
              items={result.breaking_changes}
              color="red"
            />
          )}

          {/* Full Markdown */}
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h4 className="font-semibold text-gray-900">Markdown Output</h4>
              <button
                onClick={downloadMarkdown}
                className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
              >
                <Download className="w-4 h-4 mr-2" />
                Download
              </button>
            </div>
            <div className="p-6 bg-gray-50">
              <pre className="whitespace-pre-wrap text-sm text-gray-800">
                {result.markdown}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, color }: any) {
  return (
    <div className={`bg-${color}-50 border border-${color}-200 rounded-lg p-4`}>
      <p className="text-sm font-medium text-gray-600">{label}</p>
      <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
    </div>
  );
}

function ChangeSection({ title, items, color }: any) {
  return (
    <div className={`bg-${color}-50 border border-${color}-200 rounded-lg p-6`}>
      <h4 className="text-lg font-semibold mb-3">{title}</h4>
      <ul className="space-y-2">
        {items.map((item: string, idx: number) => (
          <li key={idx} className="flex items-start">
            <span className="mr-2">•</span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
