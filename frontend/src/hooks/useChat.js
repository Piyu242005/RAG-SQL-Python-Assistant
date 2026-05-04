import { useState, useCallback, useEffect, useRef } from 'react';
import { streamChatQuery } from '../services/api';
import toast from 'react-hot-toast';

// ── localStorage helpers ──────────────────────────────────
const STORAGE_KEYS = {
  CONVERSATIONS: 'rag_conversations',
  MESSAGES: 'rag_messages_',       // suffixed with conversation id
  ACTIVE_ID: 'rag_active_conversation',
};

const loadFromStorage = (key, fallback) => {
  try {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : fallback;
  } catch {
    return fallback;
  }
};

const saveToStorage = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Storage full or unavailable
  }
};

const removeFromStorage = (key) => {
  try {
    localStorage.removeItem(key);
  } catch {
    // ignore
  }
};

/**
 * Custom hook for managing chat state, conversations, and interactions.
 */
export const useChat = () => {
  const [conversations, setConversations] = useState(() =>
    loadFromStorage(STORAGE_KEYS.CONVERSATIONS, [])
  );
  const [activeConversationId, setActiveConversationId] = useState(() =>
    loadFromStorage(STORAGE_KEYS.ACTIVE_ID, null)
  );
  const [messages, setMessages] = useState(() => {
    const savedId = loadFromStorage(STORAGE_KEYS.ACTIVE_ID, null);
    return savedId
      ? loadFromStorage(STORAGE_KEYS.MESSAGES + savedId, [])
      : [];
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);

  const activeIdRef = useRef(activeConversationId);
  useEffect(() => {
    activeIdRef.current = activeConversationId;
  }, [activeConversationId]);

  useEffect(() => {
    saveToStorage(STORAGE_KEYS.CONVERSATIONS, conversations);
  }, [conversations]);

  useEffect(() => {
    saveToStorage(STORAGE_KEYS.ACTIVE_ID, activeConversationId);
  }, [activeConversationId]);

  useEffect(() => {
    const id = activeIdRef.current;
    if (id && messages.length > 0) {
      saveToStorage(STORAGE_KEYS.MESSAGES + id, messages);
    }
  }, [messages]);

  const sendMessage = async (query, docType = null) => {
    if (!query.trim() || isLoading) return;

    let convId = activeIdRef.current;

    // Create conversation if none exists
    if (!convId) {
      convId = Date.now().toString();
      const title = query.slice(0, 35) + (query.length > 35 ? '...' : '');
      const newConv = { id: convId, title, createdAt: new Date().toISOString() };
      setConversations((prev) => [newConv, ...prev]);
      setActiveConversationId(convId);
      activeIdRef.current = convId;
    }

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: query,
      timestamp: new Date().toISOString(),
    };

    const aiMessageId = Date.now() + 1;
    const initialAiMessage = {
      id: aiMessageId,
      type: 'assistant',
      content: '▋', // Force immediate non-empty to skip skeleton
      sources: [],
      timestamp: new Date().toISOString(),
      success: true,
    };

    setMessages((prev) => [...prev, userMessage, initialAiMessage]);
    setIsLoading(true);
    setIsStreaming(true);
    setError(null);

    try {
      await streamChatQuery(query, convId, docType, (chunk) => {
        console.log("Stream chunk:", chunk);
        if (typeof chunk.token === 'string') {
          setMessages(prev => {
            const updated = [...prev];
            const lastIndex = updated.length - 1;

            if (lastIndex >= 0) {
              const last = { ...updated[lastIndex] };

              if (last.type === 'assistant' || last.role === 'assistant') {
                // If it was just the cursor, replace it
                if (last.content === '▋') last.content = '';
                last.content += chunk.token;
                updated[lastIndex] = last;
              }
            }

            return updated;
          });
        } else if (chunk.sources) {
          setMessages(prev => {
            const updated = [...prev];
            const lastIndex = updated.length - 1;

            if (lastIndex >= 0) {
              const last = { ...updated[lastIndex] };

              if (last.type === 'assistant' || last.role === 'assistant') {
                last.sources = chunk.sources;
                updated[lastIndex] = last;
              }
            }

            return updated;
          });
        }
      });

      // Update conversation title if it's the first message
      setConversations(prev => prev.map(c => {
        if (c.id === convId && c.title.includes('...')) {
          return { ...c, title: query.slice(0, 40) };
        }
        return c;
      }));

    } catch (err) {
      setError(err.message);
      toast.error(err.message || 'Streaming failed');

      setMessages((prev) => {
        const filtered = prev.filter(m => m.id !== aiMessageId || m.content.length > 0);
        const errorMessage = {
          id: Date.now() + 5,
          type: 'error',
          content: err.message || 'Failed to connect to AI service.',
          timestamp: new Date().toISOString(),
        };
        return [...filtered, errorMessage];
      });
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
    }
  };

  const clearMessages = useCallback(() => {
    const id = activeIdRef.current;
    setMessages([]);
    setError(null);
    if (id) {
      removeFromStorage(STORAGE_KEYS.MESSAGES + id);
    }
  }, []);

  const startNewChat = useCallback(() => {
    setMessages([]);
    setActiveConversationId(null);
    activeIdRef.current = null;
    setError(null);
  }, []);

  const selectConversation = useCallback((id) => {
    setActiveConversationId(id);
    activeIdRef.current = id;
    const savedMessages = loadFromStorage(STORAGE_KEYS.MESSAGES + id, []);
    setMessages(savedMessages);
    setError(null);
  }, []);

  const deleteConversation = useCallback((id) => {
    setConversations((prev) => prev.filter((c) => c.id !== id));
    removeFromStorage(STORAGE_KEYS.MESSAGES + id);
    if (activeIdRef.current === id) {
      setActiveConversationId(null);
      activeIdRef.current = null;
      setMessages([]);
    }
  }, []);

  return {
    conversations,
    activeConversationId,
    messages,
    isLoading,
    isStreaming,
    error,
    sendMessage,
    clearMessages,
    startNewChat,
    selectConversation,
    deleteConversation,
  };
};
