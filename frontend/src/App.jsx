import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import ChatContainer from './components/ChatContainer';
import Sidebar from './components/Sidebar';
import ToastProvider from './components/ToastProvider';
import { ThemeProvider } from './context/ThemeContext';
import { getHealthStatus } from './services/api';
import { useChat } from './hooks/useChat';
import { Loader2, Sparkles } from 'lucide-react';

function AppContent() {
  const [healthStatus, setHealthStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [docFilter, setDocFilter] = useState(null);

  const {
    conversations,
    activeConversationId,
    startNewChat,
    selectConversation,
    deleteConversation,
  } = useChat();

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const status = await getHealthStatus();
        setHealthStatus(status);
      } catch (error) {
        console.error('Failed to check health:', error);
        setHealthStatus({ status: 'error' });
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="h-screen bg-surface-50 dark:bg-surface-950 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-br from-primary-500 to-violet-600 flex items-center justify-center shadow-2xl shadow-primary-500/30 mb-5">
            <Sparkles className="w-7 h-7 text-white animate-pulse" />
          </div>
          <Loader2 className="w-5 h-5 text-primary-500 dark:text-primary-400 animate-spin mx-auto mb-3" />
          <p className="text-surface-500 text-sm font-medium">Initializing Aurora…</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-surface-50 dark:bg-surface-950 flex overflow-hidden">
      <ToastProvider />

      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        conversations={conversations}
        activeConversationId={activeConversationId}
        onNewChat={startNewChat}
        onSelectConversation={selectConversation}
        onDeleteConversation={deleteConversation}
        docFilter={docFilter}
        onDocFilterChange={setDocFilter}
      />

      <main className="flex-1 min-w-0">
        <ChatContainer
          healthStatus={healthStatus}
          docFilter={docFilter}
          onDocFilterChange={setDocFilter}
        />
      </main>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;
