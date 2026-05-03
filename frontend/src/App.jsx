import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Loader2 } from 'lucide-react';
import { ThemeProvider } from './context/ThemeContext';
import Sidebar from './components/Sidebar';
import ChatContainer from './components/ChatContainer';
import ToastProvider from './components/ToastProvider';
import { useChat } from './hooks/useChat';

function AppContent() {
  const [healthStatus, setHealthStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [docFilter, setDocFilter] = useState(null);

  // Single source of truth for all chat state
  const chat = useChat();

  useEffect(() => {
    let attempts = 0;
    const MAX_ATTEMPTS = 5;
    const RETRY_DELAY = 3000; // 3 seconds

    const checkHealth = async () => {
      try {
        const response = await fetch('/api/health');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        setHealthStatus(data);
        setIsLoading(false);
      } catch {
        attempts++;
        if (attempts < MAX_ATTEMPTS) {
          // Backend may still be starting — retry
          setTimeout(checkHealth, RETRY_DELAY);
        } else {
          setHealthStatus({
            status: 'error',
            ollama_running: false,
            model_available: false,
            vectorstore_initialized: false,
          });
          setIsLoading(false);
        }
      }
    };

    checkHealth();
  }, []);

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-[#F3F4F6] dark:bg-[#0B0D11]">
        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="text-center">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-br from-primary-500 to-violet-600 flex items-center justify-center shadow-glow-primary mb-5">
            <Sparkles className="w-6 h-6 text-white animate-pulse" />
          </div>
          <Loader2 className="w-5 h-5 text-primary-400 animate-spin mx-auto mb-3" />
          <p className="text-dark-300 text-sm font-medium">Initializing Piyu RAG...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="h-screen flex bg-[#F8FAFC] dark:bg-[#09090B] overflow-hidden font-sans antialiased text-slate-900 dark:text-slate-100">
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        conversations={chat.conversations}
        activeConversationId={chat.activeConversationId}
        onNewChat={chat.startNewChat}
        onSelectConversation={chat.selectConversation}
        onDeleteConversation={chat.deleteConversation}
        docFilter={docFilter}
        onDocFilterChange={setDocFilter}
      />
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        {/* Background Decorative Glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-4xl h-64 bg-primary-500/5 blur-[120px] pointer-events-none" />
        
        <ChatContainer
          healthStatus={healthStatus}
          docFilter={docFilter}
          onDocFilterChange={setDocFilter}
          chat={chat}
        />
      </main>
      <ToastProvider />
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
