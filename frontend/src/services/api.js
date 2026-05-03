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
 * Stream a chat query response from the RAG system.
 */
export const streamChatQuery = async (query, conversationId = null, docType = null, onChunk) => {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        conversation_id: conversationId,
        doc_type: docType,
      }),
    });
  } catch {
    throw new Error('Cannot connect to backend. Is the server running on port 8000?');
  }

  if (!response.ok) {
    let detail = `Backend error ${response.status}`;
    try { const j = await response.json(); detail = j.detail || detail; } catch {}
    throw new Error(detail);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let partialChunk = '';

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      partialChunk += decoder.decode(value, { stream: true });
      const lines = partialChunk.split('\n');
      partialChunk = lines.pop(); // keep last incomplete line

      for (const line of lines) {
        if (!line.startsWith('data: ') || line.includes('[DONE]')) continue;
        try {
          const data = JSON.parse(line.slice(6)); // remove 'data: ' prefix
          if (data.error) throw new Error(data.error);
          if (data.token && onChunk) onChunk({ token: data.token });
          else if (data.sources && onChunk) onChunk({ sources: data.sources });
        } catch (parseErr) {
          // Only re-throw real errors, not JSON parse failures on partial chunks
          if (parseErr.message && !parseErr.message.includes('JSON')) throw parseErr;
          console.warn('Stream parse warning:', parseErr.message);
        }
      }
    }
  } finally {
    reader.releaseLock();
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
