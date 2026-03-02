import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Loader2 } from 'lucide-react';
import { ThemeProvider } from './context/ThemeContext';
import Sidebar from './components/Sidebar';
import ChatContainer from './components/ChatContainer';
import ToastProvider from './components/ToastProvider';

function AppContent() {
  const [healthStatus, setHealthStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [docFilter, setDocFilter] = useState(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/health');
        const data = await response.json();
        setHealthStatus(data);
      } catch (error) {
        setHealthStatus({ status: 'error', ollama_running: false, model_available: false, vectorstore_initialized: false });
      } finally {
        setIsLoading(false);
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
    <div className="h-screen flex bg-[#F3F4F6] dark:bg-[#0B0D11] overflow-hidden">
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        conversations={conversations}
        activeConversationId={activeConversationId}
        onNewChat={() => setActiveConversationId(null)}
        onSelectConversation={setActiveConversationId}
        onDeleteConversation={(id) => {
          setConversations(conversations.filter((c) => c.id !== id));
          if (activeConversationId === id) setActiveConversationId(null);
        }}
        docFilter={docFilter}
        onDocFilterChange={setDocFilter}
      />
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <ChatContainer healthStatus={healthStatus} docFilter={docFilter} onDocFilterChange={setDocFilter} />
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
