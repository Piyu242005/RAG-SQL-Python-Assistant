import { useState, useCallback, useEffect, useRef } from 'react';
import { streamChatQuery } from '../services/api';
import toast from 'react-hot-toast';

// ── localStorage helpers ──────────────────────────────────
const STORAGE_KEYS = {
  CONVERSATIONS: 'rag_conversations',
  MESSAGES: 'rag_messages_',
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
  } catch {}
};

const removeFromStorage = (key) => {
  try {
    localStorage.removeItem(key);
  } catch {}
};

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
  const abortControllerRef = useRef(null);

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

  const sendMessage = async (query, docType = null, readinessStatus = null) => {
    if (!query.trim() || isLoading || isStreaming) return;

    if (!readinessStatus?.ready) {
      const reason =
        Array.isArray(readinessStatus?.reasons) && readinessStatus.reasons.length
          ? readinessStatus.reasons.join(', ')
          : 'System dependencies not ready';

      toast.error(`System not ready: ${reason}`);
      setError(`System not ready: ${reason}`);
      return;
    }

    let convId = activeIdRef.current;

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
      content: '▋',
      sources: [],
      timestamp: new Date().toISOString(),
      success: true,
    };

    setMessages((prev) => [...prev, userMessage, initialAiMessage]);
    setIsLoading(true);
    setIsStreaming(true);
    setError(null);

    // Abort previous stream if active
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    try {
      await streamChatQuery(query, convId, docType, (chunk) => {
        // ✅ FIXED: Accept ALL tokens (including spaces/newlines)
        if (Object.prototype.hasOwnProperty.call(chunk, 'token')) {
          setMessages((prev) => {
            const updated = [...prev];
            const lastIndex = updated.length - 1;

            if (lastIndex >= 0) {
              const last = { ...updated[lastIndex] };

              if (last.type === 'assistant' || last.role === 'assistant') {
                if (last.content === '▋') last.content = '';
                last.content += chunk.token;
                updated[lastIndex] = last;
              }
            }

            return updated;
          });
        } else if (chunk.sources) {
          setMessages((prev) => {
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
      }, abortControllerRef.current.signal);

      setConversations((prev) =>
        prev.map((c) => {
          if (c.id === convId && c.title.includes('...')) {
            return { ...c, title: query.slice(0, 40) };
          }
          return c;
        })
      );
    } catch (err) {
      if (err.name === 'AbortError' || err.message === 'signal is aborted without reason') {
        console.log('Stream aborted.');
        return;
      }
      setError(err.message);
      toast.error(err.message || 'Streaming failed');

      setMessages((prev) => {
        const filtered = prev.filter(
          (m) => m.id !== aiMessageId || m.content.length > 0
        );

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
      abortControllerRef.current = null;
    }
  };

  const clearMessages = useCallback(() => {
    if (abortControllerRef.current) abortControllerRef.current.abort();
    const id = activeIdRef.current;
    setMessages([]);
    setError(null);

    if (id) {
      removeFromStorage(STORAGE_KEYS.MESSAGES + id);
    }
  }, []);

  const startNewChat = useCallback(() => {
    if (abortControllerRef.current) abortControllerRef.current.abort();
    setMessages([]);
    setActiveConversationId(null);
    activeIdRef.current = null;
    setError(null);
  }, []);

  const selectConversation = useCallback((id) => {
    if (abortControllerRef.current) abortControllerRef.current.abort();
    setActiveConversationId(id);
    activeIdRef.current = id;

    const savedMessages = loadFromStorage(
      STORAGE_KEYS.MESSAGES + id,
      []
    );

    setMessages(savedMessages);
    setError(null);
  }, []);

  const deleteConversation = useCallback((id) => {
    if (activeIdRef.current === id && abortControllerRef.current) abortControllerRef.current.abort();
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