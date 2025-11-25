// API client for SmartTech TSD Classification API

import axios from 'axios';
import type {
  Ticket,
  ClassificationResult,
  BatchClassificationResult,
  HealthResponse,
  StatsResponse,
  MockTicketsResponse,
} from './types';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds for LLM processing
});

export const smartTechApi = {
  // Health check
  async healthCheck(): Promise<HealthResponse> {
    const response = await apiClient.get<HealthResponse>('/api/v1/health');
    return response.data;
  },

  // Classify single ticket
  async classifyTicket(ticket: Ticket): Promise<ClassificationResult> {
    const response = await apiClient.post<ClassificationResult>(
      '/api/v1/tickets/classify',
      ticket
    );
    return response.data;
  },

  // Batch classify tickets
  async batchClassifyTickets(tickets: Ticket[]): Promise<BatchClassificationResult> {
    const response = await apiClient.post<BatchClassificationResult>(
      '/api/v1/tickets/batch-classify',
      { tickets }
    );
    return response.data;
  },

  // Get mock tickets
  async getMockTickets(): Promise<MockTicketsResponse> {
    const response = await apiClient.get<MockTicketsResponse>('/api/v1/tickets/mock');
    return response.data;
  },

  // Get mock ticket by ID
  async getMockTicketById(ticketId: string): Promise<Ticket> {
    const response = await apiClient.get<Ticket>(`/api/v1/tickets/mock/${ticketId}`);
    return response.data;
  },

  // Get statistics
  async getStats(): Promise<StatsResponse> {
    const response = await apiClient.get<StatsResponse>('/api/v1/stats');
    return response.data;
  },

  // Reset statistics
  async resetStats(): Promise<{ message: string; timestamp: string }> {
    const response = await apiClient.delete('/api/v1/stats');
    return response.data;
  },
};
