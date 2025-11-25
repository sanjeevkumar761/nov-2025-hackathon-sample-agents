import { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle2, Clock, TrendingUp } from 'lucide-react';
import TicketForm from './components/TicketForm';
import ClassificationResults from './components/ClassificationResults';
import MockTicketsPanel from './components/MockTicketsPanel';
import StatsPanel from './components/StatsPanel';
import ExecutionTrace from './components/ExecutionTrace';
import WorkflowGraph from './components/WorkflowGraph';
import { smartTechApi } from './api';
import type { Ticket, ClassificationResult, HealthResponse } from './types';

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [classificationResult, setClassificationResult] = useState<ClassificationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const healthData = await smartTechApi.healthCheck();
      setHealth(healthData);
    } catch (err) {
      console.error('Health check failed:', err);
      setHealth(null);
    }
  };

  const handleClassifyTicket = async (ticket: Ticket) => {
    setLoading(true);
    setError(null);
    try {
      const result = await smartTechApi.classifyTicket(ticket);
      setClassificationResult(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Classification failed');
      setClassificationResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectMockTicket = async (ticket: Ticket) => {
    await handleClassifyTicket(ticket);
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white/90 backdrop-blur-lg shadow-lg border-b border-white/20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                SmartTech TSD Agent
              </h1>
              <p className="text-sm text-gray-600 mt-2 font-medium">
                AI-Powered Ticket Classification & Self-Service Recommendations
              </p>
            </div>
            
            {/* Health Status */}
            <div className="flex items-center gap-2">
              {health?.agent_initialized ? (
                <div className="flex items-center gap-2 bg-gradient-to-r from-emerald-50 to-teal-50 px-4 py-2.5 rounded-xl border border-emerald-200 shadow-sm">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                  <span className="text-sm font-semibold text-emerald-700">Agent Ready</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 bg-gradient-to-r from-rose-50 to-red-50 px-4 py-2.5 rounded-xl border border-rose-200 shadow-sm">
                  <AlertCircle className="w-5 h-5 text-rose-600" />
                  <span className="text-sm font-semibold text-rose-700">Agent Offline</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 lg:px-8 py-10">
        {/* Info Banner */}
        <div className="mb-8 bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200/50 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow duration-300">
          <div className="flex items-start gap-4">
            <div className="p-2 bg-blue-100 rounded-xl">
              <TrendingUp className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 className="text-base font-bold text-blue-900 mb-1">How It Works</h3>
              <p className="text-sm text-blue-700 leading-relaxed">
                Submit a support ticket and our AI agent will detect the user's intent, 
                determine if it can be self-serviced, and recommend relevant knowledge base articles.
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Form & Mock Data */}
          <div className="lg:col-span-1 space-y-8">
            <TicketForm 
              onSubmit={handleClassifyTicket} 
              loading={loading}
            />
            
            <MockTicketsPanel 
              onSelectTicket={handleSelectMockTicket}
              loading={loading}
            />
          </div>

          {/* Right Column - Results & Stats */}
          <div className="lg:col-span-2 space-y-8">
            {error && (
              <div className="bg-gradient-to-r from-rose-50 to-red-50 border-2 border-rose-200/50 rounded-2xl p-5 shadow-lg">
                <div className="flex items-start gap-4">
                  <div className="p-2 bg-rose-100 rounded-xl">
                    <AlertCircle className="w-5 h-5 text-rose-600" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-rose-900">Error</h3>
                    <p className="text-sm text-rose-700 mt-1">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {loading && (
              <div className="card">
                <div className="flex items-center justify-center py-16">
                  <div className="flex flex-col items-center gap-4">
                    <Clock className="w-8 h-8 text-indigo-600 animate-spin" />
                    <span className="text-lg font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                      Analyzing ticket with AI...
                    </span>
                  </div>
                </div>
              </div>
            )}

            {classificationResult && !loading && (
              <>
                <ClassificationResults result={classificationResult} />
                
                {/* Execution Trace */}
                {classificationResult.execution_trace && classificationResult.execution_trace.length > 0 && (
                  <ExecutionTrace trace={classificationResult.execution_trace} />
                )}
              </>
            )}

            <StatsPanel />
          </div>
        </div>

        {/* Workflow Graph Section */}
        <div className="mt-12">
          <WorkflowGraph />
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 py-8 bg-white/80 backdrop-blur-lg border-t border-white/20 shadow-lg">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <p className="text-center text-sm font-medium text-gray-600">
            SmartTech TSD Agent v1.0.0 - Powered by Azure OpenAI & LangGraph
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
