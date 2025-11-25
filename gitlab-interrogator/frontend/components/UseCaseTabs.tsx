'use client';

import { GitBranch, TrendingUp, FileText, FolderKanban } from 'lucide-react';
import type { UseCaseTab } from '@/types';

interface UseCaseTabsProps {
  activeTab: UseCaseTab;
  onTabChange: (tab: UseCaseTab) => void;
}

const tabs = [
  {
    id: 'story' as UseCaseTab,
    name: 'User Stories',
    icon: GitBranch,
    description: 'Generate stories from requirements'
  },
  {
    id: 'sprint' as UseCaseTab,
    name: 'Sprint Summary',
    icon: TrendingUp,
    description: 'Analyze sprint performance'
  },
  {
    id: 'release' as UseCaseTab,
    name: 'Release Notes',
    icon: FileText,
    description: 'Generate release notes'
  },
  {
    id: 'epic' as UseCaseTab,
    name: 'Epic Categorization',
    icon: FolderKanban,
    description: 'Organize epics by theme'
  }
];

export default function UseCaseTabs({ activeTab, onTabChange }: UseCaseTabsProps) {
  return (
    <div className="border-b border-gray-200">
      <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`
                group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm
                ${
                  isActive
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
              aria-current={isActive ? 'page' : undefined}
            >
              <Icon
                className={`
                  -ml-0.5 mr-2 h-5 w-5
                  ${isActive ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'}
                `}
              />
              <span>{tab.name}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
}
