import { useState, useEffect } from 'react';
import { GitBranch, Loader, Download, ExternalLink } from 'lucide-react';

interface WorkflowNode {
  id: string;
  label: string;
  type: string;
  description: string;
}

interface WorkflowEdge {
  from: string;
  to: string;
  label: string;
}

interface WorkflowGraphData {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  workflow_type: string;
  total_nodes: number;
  total_edges: number;
}

const WorkflowGraph = () => {
  const [graphData, setGraphData] = useState<WorkflowGraphData | null>(null);
  const [mermaidCode, setMermaidCode] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [showMermaid, setShowMermaid] = useState(false);

  useEffect(() => {
    loadWorkflowGraph();
  }, []);

  const loadWorkflowGraph = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/workflow/graph');
      const data = await response.json();
      setGraphData(data);

      // Also load Mermaid syntax
      const mermaidResponse = await fetch('http://localhost:8000/api/v1/workflow/mermaid');
      const mermaidData = await mermaidResponse.json();
      setMermaidCode(mermaidData.mermaid);
    } catch (error) {
      console.error('Failed to load workflow graph:', error);
    } finally {
      setLoading(false);
    }
  };

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'entry':
        return '▶️';
      case 'exit':
        return '🏁';
      default:
        return '⚙️';
    }
  };

  const getNodeColor = (type: string) => {
    switch (type) {
      case 'entry':
        return 'from-emerald-100 to-teal-100 border-emerald-300';
      case 'exit':
        return 'from-purple-100 to-pink-100 border-purple-300';
      default:
        return 'from-blue-100 to-indigo-100 border-blue-300';
    }
  };

  const copyMermaidCode = () => {
    navigator.clipboard.writeText(mermaidCode);
    alert('Mermaid code copied! Paste it at mermaid.live to visualize');
  };

  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-12">
          <Loader className="w-8 h-8 text-indigo-600 animate-spin" />
        </div>
      </div>
    );
  }

  if (!graphData) {
    return (
      <div className="card">
        <p className="text-center text-gray-600">Failed to load workflow graph</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-r from-teal-100 to-cyan-100 rounded-xl">
            <GitBranch className="w-5 h-5 text-teal-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold bg-gradient-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">
              Agent Workflow Graph
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              {graphData.total_nodes} nodes · {graphData.total_edges} edges · {graphData.workflow_type}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowMermaid(!showMermaid)}
            className="px-4 py-2 text-sm font-semibold text-gray-700 bg-white/80 hover:bg-white rounded-xl border-2 border-gray-200 hover:border-gray-300 flex items-center gap-2 shadow-sm hover:shadow-md transition-all duration-200"
          >
            {showMermaid ? 'Hide' : 'Show'} Mermaid
          </button>
        </div>
      </div>

      {/* Workflow Visualization */}
      <div className="mb-6">
        <h3 className="text-base font-bold text-gray-800 mb-4 tracking-wide">Workflow Structure</h3>
        
        <div className="relative">
          {/* Vertical connecting line */}
          <div className="absolute left-8 top-0 bottom-0 w-1 bg-gradient-to-b from-emerald-300 via-blue-300 to-purple-300 rounded-full" />

          {/* Nodes */}
          <div className="space-y-6">
            {graphData.nodes.map((node, index) => (
              <div key={node.id} className="relative pl-20">
                {/* Node circle on timeline */}
                <div className={`absolute left-0 w-16 h-16 rounded-2xl bg-gradient-to-br ${getNodeColor(node.type)} border-2 flex items-center justify-center shadow-lg z-10`}>
                  <span className="text-2xl">{getNodeIcon(node.type)}</span>
                </div>

                {/* Node card */}
                <div className={`bg-gradient-to-r ${getNodeColor(node.type)} rounded-2xl p-5 border-2 shadow-md hover:shadow-lg transition-shadow duration-200`}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="px-2.5 py-1 bg-white/80 rounded-lg text-xs font-bold text-gray-700">
                          {node.type.toUpperCase()}
                        </span>
                        <h4 className="text-lg font-bold text-gray-900">{node.label}</h4>
                      </div>
                      <p className="text-sm text-gray-700">{node.description}</p>
                    </div>
                  </div>

                  {/* Edge indicator */}
                  {index < graphData.edges.length && (
                    <div className="mt-3 flex items-center gap-2 text-xs text-gray-600">
                      <span className="px-2 py-1 bg-white/60 rounded-md font-semibold">
                        → {graphData.edges[index].label}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Edge Details */}
      <div className="bg-gradient-to-r from-gray-50 to-slate-50 rounded-2xl p-5 border-2 border-gray-200/50 mb-6">
        <h3 className="text-base font-bold text-gray-800 mb-3 tracking-wide">Workflow Edges</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {graphData.edges.map((edge, index) => (
            <div key={index} className="bg-white rounded-xl p-3 border border-gray-200 shadow-sm">
              <div className="flex items-center gap-2 text-sm">
                <span className="font-semibold text-gray-900">{edge.from}</span>
                <span className="text-gray-400">→</span>
                <span className="font-semibold text-gray-900">{edge.to}</span>
                <span className="ml-auto px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded-md text-xs font-semibold">
                  {edge.label}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Mermaid Code Section */}
      {showMermaid && mermaidCode && (
        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl p-5 border-2 border-indigo-200/50">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-base font-bold text-gray-800 tracking-wide">Mermaid Diagram Syntax</h3>
            <div className="flex gap-2">
              <button
                onClick={copyMermaidCode}
                className="px-3 py-1.5 text-xs font-semibold text-indigo-700 bg-white rounded-lg border border-indigo-200 hover:bg-indigo-50 flex items-center gap-1.5 transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                Copy Code
              </button>
              <a
                href="https://mermaid.live"
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 text-xs font-semibold text-white bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg hover:shadow-md flex items-center gap-1.5 transition-all"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                Open in Mermaid Live
              </a>
            </div>
          </div>
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-xl overflow-x-auto text-xs font-mono border border-gray-700">
            {mermaidCode}
          </pre>
          <p className="text-xs text-gray-600 mt-2">
            💡 Copy this code and paste it at{' '}
            <a href="https://mermaid.live" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline font-semibold">
              mermaid.live
            </a>
            {' '}to see an interactive visualization
          </p>
        </div>
      )}

      {/* Workflow Summary */}
      <div className="grid grid-cols-3 gap-5 mt-6">
        <div className="bg-gradient-to-br from-teal-50 to-cyan-50 rounded-2xl p-5 border-2 border-teal-200/50 text-center hover:shadow-lg transition-shadow duration-200">
          <div className="text-3xl font-bold bg-gradient-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">
            {graphData.total_nodes}
          </div>
          <div className="text-xs font-semibold text-gray-600 mt-2 tracking-wide">Processing Nodes</div>
        </div>
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-5 border-2 border-blue-200/50 text-center hover:shadow-lg transition-shadow duration-200">
          <div className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            {graphData.total_edges}
          </div>
          <div className="text-xs font-semibold text-gray-600 mt-2 tracking-wide">Workflow Edges</div>
        </div>
        <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-5 border-2 border-purple-200/50 text-center hover:shadow-lg transition-shadow duration-200">
          <div className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent uppercase text-xl">
            {graphData.workflow_type}
          </div>
          <div className="text-xs font-semibold text-gray-600 mt-2 tracking-wide">Execution Type</div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowGraph;
