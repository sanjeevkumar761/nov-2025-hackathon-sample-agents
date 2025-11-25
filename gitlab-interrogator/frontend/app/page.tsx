'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { GitBranch, TrendingUp, FileText, FolderKanban, AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';
import type { GitLabProject, UseCaseTab } from '@/types';

// Import components (we'll create these next)
import Header from '@/components/Header';
import ProjectSelector from '@/components/ProjectSelector';
import UseCaseTabs from '@/components/UseCaseTabs';
import StoryCreator from '@/components/StoryCreator';
import SprintAnalyzer from '@/components/SprintAnalyzer';
import ReleaseNotesGenerator from '@/components/ReleaseNotesGenerator';
import EpicCategorizer from '@/components/EpicCategorizer';
import StatsOverview from '@/components/StatsOverview';

export default function Home() {
  const [selectedProject, setSelectedProject] = useState<GitLabProject | null>(null);
  const [activeTab, setActiveTab] = useState<UseCaseTab>('story');

  // Health check
  const { data: health, error: healthError } = useQuery({
    queryKey: ['health'],
    queryFn: () => api.healthCheck(),
    refetchInterval: 30000, // Check every 30s
  });

  // Show connection error if backend is down
  if (healthError) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Backend Connection Failed
          </h1>
          <p className="text-gray-600 mb-4">
            Unable to connect to the GitLab Interrogator backend.
          </p>
          <p className="text-sm text-gray-500">
            Make sure the backend server is running on{' '}
            <code className="bg-gray-100 px-2 py-1 rounded">
              {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
            </code>
          </p>
          <button
            onClick={() => window.location.reload()}
            className="mt-6 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  // Show GitLab connection warning if not connected
  const showGitLabWarning = health?.gitlab_connection !== 'connected';

  return (
    <div className="min-h-screen bg-gray-50">
      <Header health={health} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* GitLab Connection Warning */}
        {showGitLabWarning && (
          <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start">
            <AlertCircle className="w-5 h-5 text-yellow-600 mr-3 mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-medium text-yellow-800">
                GitLab Not Connected
              </h3>
              <p className="text-sm text-yellow-700 mt-1">
                Configure your GitLab personal access token in the backend .env file.
                GitLab features will be limited until connected.
              </p>
            </div>
          </div>
        )}

        {/* Project Selector */}
        <div className="mb-8">
          <ProjectSelector
            selectedProject={selectedProject}
            onProjectChange={setSelectedProject}
          />
        </div>

        {/* Stats Overview */}
        {selectedProject && (
          <div className="mb-8">
            <StatsOverview projectId={selectedProject.id} />
          </div>
        )}

        {/* Use Case Tabs */}
        <div className="bg-white rounded-lg shadow mb-8">
          <UseCaseTabs activeTab={activeTab} onTabChange={setActiveTab} />

          {/* Tab Content */}
          <div className="p-6">
            {!selectedProject ? (
              <div className="text-center py-12">
                <GitBranch className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Select a GitLab Project
                </h3>
                <p className="text-gray-600">
                  Choose a project from the dropdown above to get started
                </p>
              </div>
            ) : (
              <>
                {activeTab === 'story' && <StoryCreator project={selectedProject} />}
                {activeTab === 'sprint' && <SprintAnalyzer project={selectedProject} />}
                {activeTab === 'release' && <ReleaseNotesGenerator project={selectedProject} />}
                {activeTab === 'epic' && <EpicCategorizer project={selectedProject} />}
              </>
            )}
          </div>
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <InfoCard
            icon={<GitBranch className="w-6 h-6" />}
            title="User Stories"
            description="Generate formatted stories with acceptance criteria and story points"
            color="agile-story"
          />
          <InfoCard
            icon={<TrendingUp className="w-6 h-6" />}
            title="Sprint Analysis"
            description="Automated sprint summaries with velocity and insights"
            color="agile-sprint"
          />
          <InfoCard
            icon={<FileText className="w-6 h-6" />}
            title="Release Notes"
            description="Professional release notes from commits and issues"
            color="agile-release"
          />
          <InfoCard
            icon={<FolderKanban className="w-6 h-6" />}
            title="Epic Organization"
            description="Semantic categorization of epics by theme"
            color="agile-epic"
          />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600">
            GitLab Interrogator - AI-powered Scrum Master Digital Employee
          </p>
          <p className="text-center text-xs text-gray-500 mt-1">
            Powered by LangGraph & Azure OpenAI GPT-4
          </p>
        </div>
      </footer>
    </div>
  );
}

// Info Card Component
function InfoCard({
  icon,
  title,
  description,
  color
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  color: string;
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className={`inline-flex p-3 rounded-lg bg-${color}/10 text-${color} mb-4`}>
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
}
