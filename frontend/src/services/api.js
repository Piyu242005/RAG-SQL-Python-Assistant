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
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        query, 
        conversation_id: conversationId,
        doc_type: docType 
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to start stream');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let partialChunk = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      partialChunk += decoder.decode(value, { stream: true });
      const lines = partialChunk.split('\n');
      
      partialChunk = lines.pop(); // Keep last incomplete line

      for (const line of lines) {
        if (line.startsWith('data: ') && !line.includes('[DONE]')) {
          try {
            const data = JSON.parse(line.replace('data: ', ''));
            if (data.token && onChunk) {
              onChunk({ token: data.token });
            } else if (data.sources && onChunk) {
              onChunk({ sources: data.sources });
            } else if (data.error) {
              throw new Error(data.error);
            }
          } catch (e) {
            if (e.message && e.message.includes('Failed to parse')) {
              console.error("Stream parse error:", e);
            } else if (data?.error) {
               throw new Error(data.error);
            }
          }
        }
      }
    }
  } catch (error) {
    throw new Error(error.message || 'Failed to stream query');
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
