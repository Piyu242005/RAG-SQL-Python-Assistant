import { useState, useCallback } from 'react';
import { sendChatQuery } from '../services/api';
import toast from 'react-hot-toast';

/**
 * Custom hook for managing chat state, conversations, and interactions.
 */
export const useChat = () => {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = async (query, docType = null) => {
    if (!query.trim()) return;

    // Auto-create a conversation if none exists
    if (!activeConversationId) {
      const newId = Date.now().toString();
      const title = query.slice(0, 40) + (query.length > 40 ? '…' : '');
      const newConv = { id: newId, title, createdAt: new Date() };
      setConversations((prev) => [newConv, ...prev]);
      setActiveConversationId(newId);
    }

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: query,
      timestamp: new Date(),
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
        timestamp: new Date(),
        success: response.success,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      setError(err.message);
      toast.error(err.message || 'Failed to get response');

      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: err.message,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const startNewChat = useCallback(() => {
    setMessages([]);
    setActiveConversationId(null);
    setError(null);
  }, []);

  const selectConversation = useCallback((id) => {
    setActiveConversationId(id);
    // In a full app, would load messages from storage here
    setMessages([]);
    setError(null);
  }, []);

  const deleteConversation = useCallback((id) => {
    setConversations((prev) => prev.filter((c) => c.id !== id));
    if (activeConversationId === id) {
      setActiveConversationId(null);
      setMessages([]);
    }
  }, [activeConversationId]);

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
