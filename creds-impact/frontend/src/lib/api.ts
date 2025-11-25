/**
 * API client for Creds Inspect backend
 */

import axios from 'axios';
import type {
  ContentSubmission,
  ScanSubmissionResponse,
  ScanResult,
  ScanListItem,
  WorkflowGraph,
  HealthResponse,
  StatsResponse
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  /**
   * Health check
   */
  async healthCheck(): Promise<HealthResponse> {
    const response = await apiClient.get('/health');
    return response.data;
  },

  /**
   * Submit text content for scanning
   */
  async submitContent(submission: ContentSubmission): Promise<ScanSubmissionResponse> {
    const response = await apiClient.post('/scans/submit', submission);
    return response.data;
  },

  /**
   * Upload file for scanning
   */
  async uploadFile(file: File, contentType: string = 'attachment'): Promise<ScanSubmissionResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post(
      `/scans/upload?content_type=${contentType}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * Start analysis for a submitted scan
   */
  async analyzeScan(scanId: string): Promise<ScanResult> {
    const response = await apiClient.post(`/scans/${scanId}/analyze`);
    return response.data;
  },

  /**
   * Get scan result
   */
  async getScanResult(scanId: string): Promise<ScanResult> {
    const response = await apiClient.get(`/scans/${scanId}`);
    return response.data;
  },

  /**
   * List all scans
   */
  async listScans(limit: number = 50, offset: number = 0): Promise<ScanListItem[]> {
    const response = await apiClient.get(`/scans?limit=${limit}&offset=${offset}`);
    return response.data;
  },

  /**
   * Delete scan
   */
  async deleteScan(scanId: string): Promise<{ message: string; scan_id: string }> {
    const response = await apiClient.delete(`/scans/${scanId}`);
    return response.data;
  },

  /**
   * Get workflow graph
   */
  async getWorkflowGraph(): Promise<WorkflowGraph> {
    const response = await apiClient.get('/workflow/graph');
    return response.data;
  },

  /**
   * Get statistics
   */
  async getStats(): Promise<StatsResponse> {
    const response = await apiClient.get('/stats');
    return response.data;
  },
};
