'use client';

import { useQuery } from '@tanstack/react-query';
import { Loader2 } from 'lucide-react';
import { api } from '@/lib/api';
import type { GitLabProject } from '@/types';

interface ProjectSelectorProps {
  selectedProject: GitLabProject | null;
  onProjectChange: (project: GitLabProject | null) => void;
}

export default function ProjectSelector({
  selectedProject,
  onProjectChange
}: ProjectSelectorProps) {
  const { data: projects, isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: () => api.listProjects(),
  });

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-sm text-red-800">
          Failed to load projects. Make sure GitLab is configured.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <label
        htmlFor="project-select"
        className="block text-sm font-medium text-gray-700 mb-2"
      >
        Select GitLab Project
      </label>
      
      {isLoading ? (
        <div className="flex items-center space-x-2 text-gray-600">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Loading projects...</span>
        </div>
      ) : (
        <div className="relative">
          <select
            id="project-select"
            value={selectedProject?.id || ''}
            onChange={(e) => {
              const project = projects?.find(
                (p) => p.id === parseInt(e.target.value)
              );
              onProjectChange(project || null);
            }}
            className="block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
          >
            <option value="">-- Select a project --</option>
            {projects?.map((project) => (
              <option key={project.id} value={project.id}>
                {project.path_with_namespace}
              </option>
            ))}
          </select>
        </div>
      )}

      {selectedProject && (
        <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="text-sm font-semibold text-blue-900 mb-1">
            {selectedProject.name}
          </h3>
          {selectedProject.description && (
            <p className="text-sm text-blue-700">{selectedProject.description}</p>
          )}
          <a
            href={selectedProject.web_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-blue-600 hover:text-blue-800 underline mt-2 inline-block"
          >
            View in GitLab →
          </a>
        </div>
      )}
    </div>
  );
}
