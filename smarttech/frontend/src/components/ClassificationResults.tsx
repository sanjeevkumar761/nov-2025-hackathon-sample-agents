import { CheckCircle, XCircle, Book, TrendingUp, Clock, Target } from 'lucide-react';
import type { ClassificationResult } from '../types';

interface ClassificationResultsProps {
  result: ClassificationResult;
}

const ClassificationResults = ({ result }: ClassificationResultsProps) => {
  const getRoutingBadge = (routing: string) => {
    const badges: Record<string, { class: string; text: string }> = {
      SELF_SERVICE: { class: 'badge-success', text: 'Self-Service' },
      TIER_1_HELPDESK: { class: 'badge-info', text: 'Tier 1 Support' },
      TIER_2_HELPDESK: { class: 'badge-warning', text: 'Tier 2 Support' },
      MANUAL_REVIEW: { class: 'badge-danger', text: 'Manual Review' },
    };
    return badges[routing] || badges.MANUAL_REVIEW;
  };

  const routingBadge = getRoutingBadge(result.routing);

  return (
    <div className="space-y-8">
      {/* Main Result Card */}
      <div className="card border-2 border-indigo-200/50 shadow-2xl">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              Classification Result
            </h2>
            <p className="text-sm text-gray-600 mt-2 font-medium">Ticket: {result.ticket_id}</p>
          </div>
          
          {result.self_service_eligible ? (
            <div className="p-3 bg-gradient-to-r from-emerald-100 to-teal-100 rounded-2xl">
              <CheckCircle className="w-8 h-8 text-emerald-600" />
            </div>
          ) : (
            <div className="p-3 bg-gradient-to-r from-rose-100 to-red-100 rounded-2xl">
              <XCircle className="w-8 h-8 text-rose-600" />
            </div>
          )}
        </div>

        <div className="bg-gradient-to-r from-gray-50 to-slate-50 rounded-2xl p-5 mb-6 border border-gray-200/50">
          <h3 className="text-sm font-bold text-gray-700 mb-2.5 tracking-wide">Subject</h3>
          <p className="text-gray-900 font-medium">{result.subject}</p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-5 mb-8">
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-5 border border-blue-200/50 hover:shadow-lg transition-shadow duration-200">
            <div className="flex items-center gap-2 mb-3">
              <div className="p-1.5 bg-blue-100 rounded-lg">
                <Target className="w-4 h-4 text-blue-600" />
              </div>
              <span className="text-xs font-bold text-blue-900 tracking-wide">Intent</span>
            </div>
            <p className="text-lg font-bold text-blue-900 capitalize">
              {result.detected_intent.replace(/_/g, ' ')}
            </p>
          </div>

          <div className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-2xl p-5 border border-emerald-200/50 hover:shadow-lg transition-shadow duration-200">
            <div className="flex items-center gap-2 mb-3">
              <div className="p-1.5 bg-emerald-100 rounded-lg">
                <TrendingUp className="w-4 h-4 text-emerald-600" />
              </div>
              <span className="text-xs font-bold text-emerald-900 tracking-wide">Confidence</span>
            </div>
            <p className="text-lg font-bold text-emerald-900">
              {(result.confidence * 100).toFixed(0)}%
            </p>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-2xl p-5 border border-purple-200/50 hover:shadow-lg transition-shadow duration-200">
            <div className="flex items-center gap-2 mb-3">
              <div className="p-1.5 bg-purple-100 rounded-lg">
                <Clock className="w-4 h-4 text-purple-600" />
              </div>
              <span className="text-xs font-bold text-purple-900 tracking-wide">Routing</span>
            </div>
            <span className={`badge ${routingBadge.class}`}>
              {routingBadge.text}
            </span>
          </div>

          <div className="bg-gradient-to-br from-amber-50 to-yellow-50 rounded-2xl p-5 border border-amber-200/50 hover:shadow-lg transition-shadow duration-200">
            <div className="flex items-center gap-2 mb-3">
              <div className="p-1.5 bg-amber-100 rounded-lg">
                <Book className="w-4 h-4 text-amber-600" />
              </div>
              <span className="text-xs font-bold text-amber-900 tracking-wide">Self-Service</span>
            </div>
            <p className="text-lg font-bold text-amber-900">
              {result.self_service_eligible ? 'Yes' : 'No'}
            </p>
          </div>
        </div>

        {/* Analysis */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200/50 rounded-2xl p-5 shadow-md">
          <h3 className="text-sm font-bold text-blue-900 mb-3 tracking-wide">AI Analysis</h3>
          <p className="text-sm text-blue-800 leading-relaxed">{result.analysis}</p>
        </div>
      </div>

      {/* Knowledge Base Articles */}
      {result.knowledge_base_articles.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-gradient-to-r from-blue-100 to-indigo-100 rounded-xl">
              <Book className="w-5 h-5 text-blue-600" />
            </div>
            <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Recommended Knowledge Base Articles
            </h3>
          </div>

          <div className="space-y-3">
            {result.knowledge_base_articles.map((article) => (
              <div
                key={article.article_id}
                className="bg-gradient-to-r from-primary-50 to-blue-50 border border-primary-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="badge badge-info">{article.article_id}</span>
                      <h4 className="font-semibold text-gray-900">{article.title}</h4>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-600 mt-2">
                      <div className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        <span>Avg: {article.avg_resolution_time}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <TrendingUp className="w-4 h-4" />
                        <span>Success: {article.success_rate}%</span>
                      </div>
                      {article.steps_count && (
                        <div className="flex items-center gap-1">
                          <Book className="w-4 h-4" />
                          <span>{article.steps_count} steps</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex-shrink-0">
                    <div className="text-right">
                      <div className="text-2xl font-bold text-primary-600">
                        {article.success_rate}%
                      </div>
                      <div className="text-xs text-gray-600">Success Rate</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendation */}
      <div className={`card ${result.self_service_eligible ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}`}>
        <h3 className="text-lg font-bold text-gray-900 mb-2">Recommendation</h3>
        <p className="text-gray-700">
          {result.self_service_eligible ? (
            <>
              ✅ This ticket can be resolved through <strong>self-service</strong>. 
              Direct the user to the recommended knowledge base articles above.
              This will reduce helpdesk workload and provide faster resolution.
            </>
          ) : (
            <>
              ⚠️ This ticket requires <strong>helpdesk attention</strong>. 
              Route to {routingBadge.text} for proper handling.
            </>
          )}
        </p>
      </div>
    </div>
  );
};

export default ClassificationResults;
