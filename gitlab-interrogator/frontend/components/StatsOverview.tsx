'use client';

import { useQuery } from '@tanstack/react-query';
import { FileText, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';

interface StatsOverviewProps {
  projectId: number;
}

export default function StatsOverview({ projectId }: StatsOverviewProps) {
  const { data: issues } = useQuery({
    queryKey: ['issues', projectId],
    queryFn: () => api.listIssues(projectId, { limit: 100 }),
  });

  if (!issues) return null;

  const total = issues.total;
  const closed = issues.issues.filter((i) => i.state === 'closed').length;
  const open = total - closed;

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <StatCard
        icon={<FileText className="w-6 h-6 text-blue-600" />}
        label="Total Issues"
        value={total}
        color="blue"
      />
      <StatCard
        icon={<CheckCircle className="w-6 h-6 text-green-600" />}
        label="Closed"
        value={closed}
        color="green"
      />
      <StatCard
        icon={<Clock className="w-6 h-6 text-orange-600" />}
        label="Open"
        value={open}
        color="orange"
      />
      <StatCard
        icon={<AlertCircle className="w-6 h-6 text-purple-600" />}
        label="Completion Rate"
        value={`${total > 0 ? Math.round((closed / total) * 100) : 0}%`}
        color="purple"
      />
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  color
}: {
  icon: React.ReactNode;
  label: string;
  value: number | string;
  color: string;
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{label}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        </div>
        <div className={`p-3 bg-${color}-100 rounded-lg`}>{icon}</div>
      </div>
    </div>
  );
}
