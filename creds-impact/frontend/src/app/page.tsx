'use client';

import { useState, useEffect } from 'react';
import { Shield, AlertTriangle, CheckCircle2, FileText, Upload, Link as LinkIcon } from 'lucide-react';
import { api } from '@/lib/api';
import type { ScanResult, ScanListItem, StatsResponse } from '@/types';
import ContentSubmit from '@/components/ContentSubmit';
import ScanResults from '@/components/ScanResults';
import ScanHistory from '@/components/ScanHistory';
import StatsOverview from '@/components/StatsOverview';

export default function Home() {
  const [currentScan, setCurrentScan] = useState<ScanResult | null>(null);
  const [scans, setScans] = useState<ScanListItem[]>([]);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<'submit' | 'results' | 'history'>('submit');

  // Load scans and stats on mount
  useEffect(() => {
    loadScans();
    loadStats();
  }, []);

  const loadScans = async () => {
    try {
      const scansList = await api.listScans();
      setScans(scansList);
    } catch (err) {
      console.error('Failed to load scans:', err);
    }
  };

  const loadStats = async () => {
    try {
      const statsData = await api.getStats();
      setStats(statsData);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const handleContentSubmit = async (content: string, type: string, sourceUrl?: string) => {
    setError(null);
    setIsAnalyzing(true);

    try {
      // Submit content
      const submission = await api.submitContent({
        content,
        content_type: type,
        source_url: sourceUrl,
      });

      // Start analysis
      const result = await api.analyzeScan(submission.scan_id);
      
      setCurrentScan(result);
      setView('results');
      
      // Refresh scans and stats
      await loadScans();
      await loadStats();
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleFileSubmit = async (file: File) => {
    setError(null);
    setIsAnalyzing(true);

    try {
      // Upload file
      const submission = await api.uploadFile(file);

      // Start analysis
      const result = await api.analyzeScan(submission.scan_id);
      
      setCurrentScan(result);
      setView('results');
      
      // Refresh scans and stats
      await loadScans();
      await loadStats();
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleScanSelect = async (scanId: string) => {
    try {
      const result = await api.getScanResult(scanId);
      setCurrentScan(result);
      setView('results');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load scan');
    }
  };

  const handleScanDelete = async (scanId: string) => {
    try {
      await api.deleteScan(scanId);
      await loadScans();
      await loadStats();
      
      if (currentScan?.scan_id === scanId) {
        setCurrentScan(null);
        setView('submit');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete scan');
    }
  };

  const handleNewScan = () => {
    setCurrentScan(null);
    setView('submit');
    setError(null);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield className="w-10 h-10 text-purple-400" />
            <div>
              <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600">
                Creds Inspect
              </h1>
              <p className="text-gray-400 text-sm">AI-Powered Credential Detection</p>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex gap-2">
            <button
              onClick={() => setView('submit')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                view === 'submit'
                  ? 'bg-purple-600 text-white'
                  : 'glass text-gray-300 hover:text-white'
              }`}
            >
              <Upload className="w-4 h-4 inline mr-2" />
              New Scan
            </button>
            <button
              onClick={() => setView('results')}
              disabled={!currentScan}
              className={`px-4 py-2 rounded-lg transition-colors ${
                view === 'results'
                  ? 'bg-purple-600 text-white'
                  : 'glass text-gray-300 hover:text-white disabled:opacity-50'
              }`}
            >
              <FileText className="w-4 h-4 inline mr-2" />
              Results
            </button>
            <button
              onClick={() => setView('history')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                view === 'history'
                  ? 'bg-purple-600 text-white'
                  : 'glass text-gray-300 hover:text-white'
              }`}
            >
              History ({scans.length})
            </button>
          </div>
        </div>

        {/* Stats Overview */}
        {stats && <StatsOverview stats={stats} />}
      </div>

      {/* Error Display */}
      {error && (
        <div className="max-w-7xl mx-auto mb-6">
          <div className="glass-card p-4 border-red-500/50 flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            <p className="text-red-400">{error}</p>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-gray-400 hover:text-white"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto">
        {view === 'submit' && (
          <ContentSubmit
            onContentSubmit={handleContentSubmit}
            onFileSubmit={handleFileSubmit}
            isAnalyzing={isAnalyzing}
          />
        )}

        {view === 'results' && currentScan && (
          <ScanResults
            result={currentScan}
            onNewScan={handleNewScan}
          />
        )}

        {view === 'history' && (
          <ScanHistory
            scans={scans}
            onScanSelect={handleScanSelect}
            onScanDelete={handleScanDelete}
            onRefresh={loadScans}
          />
        )}
      </div>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto mt-12 text-center text-gray-500 text-sm">
        <p>Powered by Azure OpenAI GPT-4 and LangGraph</p>
      </footer>
    </main>
  );
}
