import { Clock, CheckCircle, AlertCircle, Activity, Zap, Database, Target, Route } from 'lucide-react';
import type { ExecutionTraceStep } from '../types';

interface ExecutionTraceProps {
  trace: ExecutionTraceStep[];
}

const ExecutionTrace = ({ trace }: ExecutionTraceProps) => {
  if (!trace || trace.length === 0) {
    return null;
  }

  const getNodeIcon = (node: string) => {
    switch (node) {
      case 'analyze_intent':
        return <Target className="w-4 h-4" />;
      case 'check_self_service_eligibility':
        return <CheckCircle className="w-4 h-4" />;
      case 'find_knowledge_base_articles':
        return <Database className="w-4 h-4" />;
      case 'recommend_routing':
        return <Route className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  const getNodeColor = (status: string) => {
    return status === 'success' ? 'text-green-600' : 'text-red-600';
  };

  const getNodeBgColor = (status: string) => {
    return status === 'success' ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200';
  };

  const totalDuration = trace.reduce((sum, step) => sum + (step.duration_ms || 0), 0);

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-r from-violet-100 to-fuchsia-100 rounded-xl">
            <Activity className="w-5 h-5 text-violet-600" />
          </div>
          <h3 className="text-2xl font-bold bg-gradient-to-r from-violet-600 to-fuchsia-600 bg-clip-text text-transparent">
            Agent Execution Trace
          </h3>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-gray-50 to-slate-50 rounded-xl border-2 border-gray-200 shadow-sm">
          <Clock className="w-4 h-4 text-violet-600" />
          <span className="text-sm font-bold text-gray-700">Total: <span className="text-violet-600">{totalDuration}ms</span></span>
        </div>
      </div>

      {/* Workflow Timeline */}
      <div className="relative">
        {/* Vertical Line */}
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200" />

        {/* Steps */}
        <div className="space-y-4">
          {trace.map((step, index) => (
            <div key={index} className="relative pl-14">
              {/* Step Number Circle */}
              <div className={`absolute left-0 w-12 h-12 rounded-full border-2 flex items-center justify-center font-bold ${getNodeBgColor(step.status)} ${getNodeColor(step.status)}`}>
                {step.status === 'success' ? (
                  <CheckCircle className="w-6 h-6" />
                ) : (
                  <AlertCircle className="w-6 h-6" />
                )}
              </div>

              {/* Step Content */}
              <div className={`border-2 rounded-lg p-4 ${getNodeBgColor(step.status)}`}>
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-white rounded text-xs font-medium text-gray-700 border border-gray-300">
                        {getNodeIcon(step.node)}
                        Step {step.step}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(step.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <h4 className="font-semibold text-gray-900">{step.action}</h4>
                    <p className="text-sm text-gray-600 mt-1 font-mono">{step.node}</p>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    <Zap className="w-4 h-4 text-yellow-600" />
                    <span className="text-sm font-medium text-gray-700">
                      {step.duration_ms}ms
                    </span>
                  </div>
                </div>

                {/* Details */}
                {step.details && Object.keys(step.details).length > 0 && (
                  <div className="bg-white rounded border border-gray-200 p-3 mt-3">
                    <div className="text-xs font-semibold text-gray-700 mb-2">Details:</div>
                    <div className="space-y-2">
                      {/* LLM Call Details */}
                      {step.details.llm_call && (
                        <div className="bg-blue-50 rounded p-2 border border-blue-200">
                          <div className="flex items-center gap-2 mb-1">
                            <Zap className="w-3 h-3 text-blue-600" />
                            <span className="text-xs font-semibold text-blue-900">LLM Invocation</span>
                          </div>
                          <div className="text-xs text-blue-800 space-y-1">
                            <div>Model: <span className="font-mono">{step.details.llm_call.model}</span></div>
                            <div>Prompt Length: <span className="font-mono">{step.details.llm_call.prompt_length} chars</span></div>
                            <div>Messages: <span className="font-mono">{step.details.llm_call.messages_sent}</span></div>
                          </div>
                        </div>
                      )}

                      {/* Result Details */}
                      {step.details.result && (
                        <div className="bg-green-50 rounded p-2 border border-green-200">
                          <div className="flex items-center gap-2 mb-1">
                            <Target className="w-3 h-3 text-green-600" />
                            <span className="text-xs font-semibold text-green-900">Result</span>
                          </div>
                          <div className="text-xs text-green-800 space-y-1">
                            {step.details.result.intent && (
                              <div>Intent: <span className="font-semibold">{step.details.result.intent}</span></div>
                            )}
                            {step.details.result.confidence !== undefined && (
                              <div>Confidence: <span className="font-semibold">{(step.details.result.confidence * 100).toFixed(1)}%</span></div>
                            )}
                            {step.details.result.reasoning && (
                              <div className="mt-1 italic">{step.details.result.reasoning}</div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Eligibility Check */}
                      {step.details.eligible !== undefined && (
                        <div className="bg-purple-50 rounded p-2 border border-purple-200">
                          <div className="text-xs text-purple-800 space-y-1">
                            <div>
                              Eligible: <span className="font-semibold">{step.details.eligible ? 'YES' : 'NO'}</span>
                            </div>
                            {step.details.reason && (
                              <div className="italic">{step.details.reason}</div>
                            )}
                            {step.details.threshold_checked && (
                              <div>Threshold: <span className="font-mono">{(step.details.threshold_checked * 100).toFixed(0)}%</span></div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* KB Articles */}
                      {step.details.articles_found !== undefined && (
                        <div className="bg-yellow-50 rounded p-2 border border-yellow-200">
                          <div className="text-xs text-yellow-800 space-y-1">
                            <div>
                              Articles Found: <span className="font-semibold">{step.details.articles_found}</span>
                            </div>
                            {step.details.article_ids && step.details.article_ids.length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-1">
                                {step.details.article_ids.map((id: string) => (
                                  <span key={id} className="inline-block px-1.5 py-0.5 bg-yellow-100 rounded text-xs font-mono">
                                    {id}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Routing Decision */}
                      {step.details.routing && (
                        <div className="bg-indigo-50 rounded p-2 border border-indigo-200">
                          <div className="text-xs text-indigo-800 space-y-1">
                            <div>
                              Routing: <span className="font-semibold">{step.details.routing}</span>
                            </div>
                            {step.details.recommendation && (
                              <div className="italic">{step.details.recommendation}</div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Generic Details */}
                      {Object.entries(step.details).map(([key, value]) => {
                        if (['llm_call', 'result', 'eligible', 'reason', 'threshold_checked', 
                             'articles_found', 'article_ids', 'routing', 'recommendation'].includes(key)) {
                          return null;
                        }
                        return (
                          <div key={key} className="text-xs">
                            <span className="font-semibold text-gray-700">{key}:</span>{' '}
                            <span className="text-gray-600">
                              {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Error Display */}
                {step.error && (
                  <div className="bg-red-100 border border-red-300 rounded p-2 mt-3">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="w-4 h-4 text-red-600 mt-0.5" />
                      <div className="text-xs text-red-800">
                        <span className="font-semibold">Error:</span> {step.error}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Summary */}
      <div className="mt-8 grid grid-cols-3 gap-5">
        <div className="bg-gradient-to-br from-violet-50 to-purple-50 rounded-2xl p-5 border-2 border-violet-200/50 text-center hover:shadow-lg transition-shadow duration-200">
          <div className="text-3xl font-bold bg-gradient-to-r from-violet-600 to-purple-600 bg-clip-text text-transparent">{trace.length}</div>
          <div className="text-xs font-semibold text-gray-600 mt-2 tracking-wide">Workflow Steps</div>
        </div>
        <div className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-2xl p-5 border-2 border-emerald-200/50 text-center hover:shadow-lg transition-shadow duration-200">
          <div className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
            {trace.filter(s => s.status === 'success').length}
          </div>
          <div className="text-xs font-semibold text-gray-600 mt-2 tracking-wide">Successful</div>
        </div>
        <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl p-5 border-2 border-amber-200/50 text-center hover:shadow-lg transition-shadow duration-200">
          <div className="text-3xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">{totalDuration}ms</div>
          <div className="text-xs font-semibold text-gray-600 mt-2 tracking-wide">Total Duration</div>
        </div>
      </div>
    </div>
  );
};

export default ExecutionTrace;
