import { useState, useEffect } from 'react';
import { BarChart3, RefreshCw, TrendingUp } from 'lucide-react';
import { smartTechApi } from '../api';
import type { StatsResponse } from '../types';

const StatsPanel = () => {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
    // Refresh stats every 5 seconds
    const interval = setInterval(loadStats, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    try {
      const statsData = await smartTechApi.getStats();
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    try {
      await smartTechApi.resetStats();
      await loadStats();
    } catch (error) {
      console.error('Failed to reset stats:', error);
    }
  };

  if (loading || !stats) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-8">
          <RefreshCw className="w-6 h-6 text-primary-600 animate-spin" />
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-r from-cyan-100 to-blue-100 rounded-xl">
            <BarChart3 className="w-5 h-5 text-cyan-600" />
          </div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
            Classification Statistics
          </h2>
        </div>
        <button
          onClick={handleReset}
          className="px-4 py-2 text-sm font-semibold text-gray-700 bg-white/80 hover:bg-white rounded-xl border-2 border-gray-200 hover:border-gray-300 flex items-center gap-2 shadow-sm hover:shadow-md transition-all duration-200 hover:scale-105"
        >
          <RefreshCw className="w-4 h-4" />
          Reset
        </button>
      </div>

      {stats.total_classifications === 0 ? (
        <div className="text-center py-8 text-gray-600">
          No classifications yet. Submit a ticket to see statistics.
        </div>
      ) : (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-2 gap-5">
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-6 border-2 border-blue-200/50 hover:shadow-lg transition-shadow duration-200">
              <div className="text-sm font-bold text-blue-700 mb-2 tracking-wide">Total Classifications</div>
              <div className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                {stats.total_classifications}
              </div>
            </div>

            <div className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-2xl p-6 border-2 border-emerald-200/50 hover:shadow-lg transition-shadow duration-200">
              <div className="text-sm font-bold text-emerald-700 mb-2 tracking-wide">Self-Service Eligible</div>
              <div className="flex items-baseline gap-2">
                <div className="text-4xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                  {stats.self_service_count}
                </div>
                <span className="text-xl font-semibold text-emerald-700">
                  ({stats.self_service_percentage.toFixed(0)}%)
                </span>
              </div>
            </div>
          </div>

          {/* Intent Distribution */}
          {Object.keys(stats.intent_distribution).length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="p-1.5 bg-gradient-to-r from-indigo-100 to-purple-100 rounded-lg">
                  <TrendingUp className="w-4 h-4 text-indigo-600" />
                </div>
                <h3 className="text-base font-bold text-gray-800 tracking-wide">
                  Intent Distribution
                </h3>
              </div>
              <div className="space-y-4">
                {Object.entries(stats.intent_distribution)
                  .sort((a, b) => b[1] - a[1])
                  .map(([intent, count]) => {
                    const percentage = (count / stats.total_classifications) * 100;
                    return (
                      <div key={intent} className="group">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-semibold text-gray-800 capitalize">
                            {intent.replace(/_/g, ' ')}
                          </span>
                          <span className="text-sm font-bold text-indigo-600">
                            {count} <span className="text-gray-500">({percentage.toFixed(0)}%)</span>
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3 shadow-inner overflow-hidden">
                          <div
                            className="bg-gradient-to-r from-indigo-500 to-purple-500 h-3 rounded-full transition-all duration-500 shadow-sm group-hover:shadow-md"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>
          )}

          {/* Routing Distribution */}
          {Object.keys(stats.routing_distribution).length > 0 && (
            <div>
              <h3 className="text-base font-bold text-gray-800 mb-4 tracking-wide">
                Routing Distribution
              </h3>
              <div className="space-y-4">
                {Object.entries(stats.routing_distribution)
                  .sort((a, b) => b[1] - a[1])
                  .map(([routing, count]) => {
                    const percentage = (count / stats.total_classifications) * 100;
                    const gradientClass = routing === 'SELF_SERVICE'
                      ? 'bg-gradient-to-r from-emerald-500 to-teal-500'
                      : routing === 'TIER_1_HELPDESK'
                      ? 'bg-gradient-to-r from-blue-500 to-cyan-500'
                      : routing === 'TIER_2_HELPDESK'
                      ? 'bg-gradient-to-r from-amber-500 to-yellow-500'
                      : 'bg-gradient-to-r from-rose-500 to-red-500';

                    return (
                      <div key={routing} className="group">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-semibold text-gray-800">
                            {routing.replace(/_/g, ' ')}
                          </span>
                          <span className="text-sm font-bold text-gray-700">
                            {count} <span className="text-gray-500">({percentage.toFixed(0)}%)</span>
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3 shadow-inner overflow-hidden">
                          <div
                            className={`${gradientClass} h-3 rounded-full transition-all duration-500 shadow-sm group-hover:shadow-md`}
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>
          )}

          {/* Impact Summary */}
          {stats.self_service_count > 0 && (
            <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <TrendingUp className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-1">
                    Potential Impact
                  </h4>
                  <p className="text-sm text-gray-700">
                    <strong>{stats.self_service_count}</strong> tickets could be resolved 
                    through self-service, potentially reducing helpdesk workload by{' '}
                    <strong>{stats.self_service_percentage.toFixed(0)}%</strong>.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default StatsPanel;
