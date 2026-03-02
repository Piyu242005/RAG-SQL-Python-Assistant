/**
 * API client for communicating with the RAG backend.
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Send a chat query to the RAG system.
 */
export const sendChatQuery = async (query, docType = null) => {
  try {
    const response = await apiClient.post('/api/chat', {
      query,
      doc_type: docType,
    });
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail || 'Failed to send query'
    );
  }
};

/**
 * Get health status of the system.
 */
export const getHealthStatus = async () => {
  try {
    const response = await apiClient.get('/api/health');
    return response.data;
  } catch (error) {
    throw new Error('Failed to get health status');
  }
};

/**
 * Get document statistics.
 */
export const getDocumentStats = async () => {
  try {
    const response = await apiClient.get('/api/documents');
    return response.data;
  } catch (error) {
    throw new Error('Failed to get document stats');
  }
};

/**
 * Initialize or reinitialize the system.
 */
export const initializeSystem = async () => {
  try {
    const response = await apiClient.post('/api/initialize');
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail || 'Failed to initialize system'
    );
  }
};

export default apiClient;
