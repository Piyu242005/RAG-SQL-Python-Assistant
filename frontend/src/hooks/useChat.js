import { useState, useCallback, useEffect, useRef } from 'react';
import { sendChatQuery } from '../services/api';
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
    // Storage full or unavailable — silently ignore
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
 * All conversations and messages are persisted to localStorage.
 */
export const useChat = () => {
  // Load initial state from localStorage
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
  const [error, setError] = useState(null);

  // Track activeConversationId for use inside sendMessage without stale closures
  const activeIdRef = useRef(activeConversationId);
  useEffect(() => {
    activeIdRef.current = activeConversationId;
  }, [activeConversationId]);

  // ── Persist conversations list whenever it changes ──────
  useEffect(() => {
    saveToStorage(STORAGE_KEYS.CONVERSATIONS, conversations);
  }, [conversations]);

  // ── Persist active conversation ID ──────────────────────
  useEffect(() => {
    saveToStorage(STORAGE_KEYS.ACTIVE_ID, activeConversationId);
  }, [activeConversationId]);

  // ── Persist messages for the active conversation ────────
  useEffect(() => {
    const id = activeIdRef.current;
    if (id && messages.length > 0) {
      saveToStorage(STORAGE_KEYS.MESSAGES + id, messages);
    }
  }, [messages]);

  // ── Send a message ──────────────────────────────────────
  const sendMessage = async (query, docType = null) => {
    if (!query.trim()) return;

    let convId = activeIdRef.current;

    // Auto-create a conversation if none exists
    if (!convId) {
      const newId = Date.now().toString();
      const title = query.slice(0, 40) + (query.length > 40 ? '...' : '');
      const newConv = { id: newId, title, createdAt: new Date().toISOString() };
      setConversations((prev) => [newConv, ...prev]);
      setActiveConversationId(newId);
      activeIdRef.current = newId;
      convId = newId;
    }

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: query,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await sendChatQuery(query, docType);

      const aiMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.answer,
        sources: response.sources || [],
        timestamp: new Date().toISOString(),
        success: response.success,
      };

      setMessages((prev) => {
        const updated = [...prev, aiMessage];
        // Save immediately so even if user closes the tab, it's persisted
        saveToStorage(STORAGE_KEYS.MESSAGES + convId, updated);
        return updated;
      });
    } catch (err) {
      setError(err.message);
      toast.error(err.message || 'Failed to get response');

      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: err.message,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // ── Clear messages for current conversation ─────────────
  const clearMessages = useCallback(() => {
    const id = activeIdRef.current;
    setMessages([]);
    setError(null);
    if (id) {
      removeFromStorage(STORAGE_KEYS.MESSAGES + id);
    }
  }, []);

  // ── Start a new chat ────────────────────────────────────
  const startNewChat = useCallback(() => {
    setMessages([]);
    setActiveConversationId(null);
    activeIdRef.current = null;
    setError(null);
  }, []);

  // ── Select a conversation and load its messages ─────────
  const selectConversation = useCallback((id) => {
    setActiveConversationId(id);
    activeIdRef.current = id;
    // Load messages from localStorage for this conversation
    const savedMessages = loadFromStorage(STORAGE_KEYS.MESSAGES + id, []);
    setMessages(savedMessages);
    setError(null);
  }, []);

  // ── Delete a conversation and its messages ──────────────
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
    error,
    sendMessage,
    clearMessages,
    startNewChat,
    selectConversation,
    deleteConversation,
  };
};
