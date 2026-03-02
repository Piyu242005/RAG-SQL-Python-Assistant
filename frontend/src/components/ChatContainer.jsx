import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Trash2, Sparkles, AlertTriangle, Database, Code2, BookOpen, Zap,
  CheckCircle2, XCircle, RefreshCw, Rocket,
} from 'lucide-react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import TypingIndicator from './TypingIndicator';
import { useChat } from '../hooks/useChat';

const ChatContainer = ({ healthStatus, docFilter, onDocFilterChange }) => {
  const { messages, isLoading, sendMessage, clearMessages } = useChat();
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const isSystemReady = healthStatus?.ollama_running && healthStatus?.vectorstore_initialized;

  const exampleQuestions = [
    { icon: Database, text: 'What are SQL JOINs and when to use each type?', color: 'from-blue-500 to-cyan-500', tag: 'SQL' },
    { icon: Code2, text: 'How do Python decorators work?', color: 'from-emerald-500 to-teal-500', tag: 'Python' },
    { icon: BookOpen, text: 'Explain MySQL indexing strategies', color: 'from-violet-500 to-purple-500', tag: 'SQL' },
    { icon: Zap, text: 'What are Python list comprehensions?', color: 'from-amber-500 to-orange-500', tag: 'Python' },
  ];

  const statusChecks = [
    { label: 'Ollama LLM', ok: healthStatus?.ollama_running, detail: healthStatus?.ollama_running ? 'Connected' : 'Not running — run ollama serve' },
    { label: 'Vector Database', ok: healthStatus?.vectorstore_initialized, detail: healthStatus?.vectorstore_initialized ? 'Initialized' : 'Run initialize_db.py' },
    { label: 'Documents Indexed', ok: healthStatus?.vectorstore_initialized, detail: healthStatus?.vectorstore_initialized ? 'MySQL + Python handbooks' : 'Pending' },
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Gradient accent */}
      <div className="h-[1px] bg-gradient-to-r from-transparent via-primary-500/40 to-transparent flex-shrink-0" />

      {/* Header */}
      <header className="px-6 py-3 flex-shrink-0 bg-white/80 dark:bg-[#0D0F13]/80 backdrop-blur-xl border-b border-black/5 dark:border-white/[0.04]">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            {isSystemReady ? (
              <div className="flex items-center gap-2">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400/60 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-400 shadow-glow-emerald"></span>
                </span>
                <span className="text-[11px] text-emerald-400 font-medium">Online</span>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                <span className="text-[11px] text-amber-400 font-medium">Not Ready</span>
              </div>
            )}
          </div>
          {messages.length > 0 && (
            <motion.button
              onClick={clearMessages}
              whileTap={{ scale: 0.92 }}
              className="px-3 py-1.5 rounded-lg text-dark-300 hover:text-dark-50
                hover:bg-white/[0.04] flex items-center gap-1.5 text-xs font-medium transition-all duration-200"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Clear
            </motion.button>
          )}
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto bg-[#F3F4F6] dark:bg-deep-glow">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center px-6">
            <div className="text-center max-w-2xl w-full">
              {/* Logo */}
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
                className="mb-10"
              >
                <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-primary-500 to-violet-600
                  flex items-center justify-center shadow-glow-primary-strong mb-6">
                  <Sparkles className="w-7 h-7 text-white" />
                </div>
                <h2 className="text-3xl sm:text-4xl font-bold text-dark-600 dark:text-dark-50 mb-3 tracking-tight">
                  How can I help you?
                </h2>
                <p className="text-dark-300 text-sm max-w-md mx-auto leading-relaxed">
                  Ask me anything about MySQL or Python. I search through the handbooks to find accurate, sourced answers.
                </p>
              </motion.div>

              {/* Cards */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.15 }}
                className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg mx-auto mb-10"
              >
                {exampleQuestions.map((q, i) => (
                  <motion.button
                    key={i}
                    whileHover={{ y: -2, scale: 1.01 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => sendMessage(q.text, docFilter)}
                    className="bg-white dark:bg-[#151A22] rounded-xl p-4 text-left group
                      border border-black/5 dark:border-white/[0.04]
                      hover:border-primary-500/20 dark:hover:border-primary-500/15
                      hover:shadow-depth-md dark:hover:shadow-glow-primary
                      transition-all duration-300"
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${q.color}
                        flex items-center justify-center flex-shrink-0 shadow-depth-sm`}>
                        <q.icon className="w-4 h-4 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <span className="text-[9px] font-bold uppercase tracking-widest text-dark-300">{q.tag}</span>
                        <p className="text-xs text-dark-200 dark:text-dark-200 group-hover:text-dark-50 leading-relaxed mt-0.5 transition-colors">
                          {q.text}
                        </p>
                      </div>
                    </div>
                  </motion.button>
                ))}
              </motion.div>

              {/* Status card */}
              {!isSystemReady && (
                <motion.div
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3, duration: 0.4 }}
                  className="max-w-sm mx-auto text-left"
                >
                  <div className="bg-white dark:bg-[#111318] rounded-2xl overflow-hidden
                    border border-black/5 dark:border-white/[0.04] shadow-depth-md">
                    {/* Header */}
                    <div className="px-4 py-3 border-b border-black/5 dark:border-white/[0.04] flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-md bg-amber-500/10 flex items-center justify-center">
                          <AlertTriangle className="w-3 h-3 text-amber-400" />
                        </div>
                        <span className="text-xs font-semibold text-dark-50">System Status</span>
                      </div>
                      <motion.button
                        onClick={() => window.location.reload()}
                        whileTap={{ scale: 0.92 }}
                        className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium
                          text-dark-200 hover:text-dark-50 hover:bg-white/[0.04] transition-all"
                      >
                        <RefreshCw className="w-3 h-3" />
                        Retry
                      </motion.button>
                    </div>

                    {/* Items */}
                    <div className="px-4 py-3 space-y-2.5">
                      {statusChecks.map((check, i) => (
                        <div key={i} className="flex items-start gap-2.5">
                          <div className={`w-5 h-5 rounded-md flex items-center justify-center flex-shrink-0 mt-0.5
                            ${check.ok ? 'bg-emerald-500/10' : 'bg-rose-500/10'}`}>
                            {check.ok
                              ? <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                              : <XCircle className="w-3 h-3 text-rose-400" />
                            }
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-xs font-medium text-dark-50 leading-tight">{check.label}</p>
                            <p className={`text-[10px] leading-tight mt-0.5 ${check.ok ? 'text-emerald-400/70' : 'text-rose-400/60'
                              }`}>{check.detail}</p>
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="px-4 pb-3">
                      <motion.a
                        href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer"
                        whileTap={{ scale: 0.96 }}
                        className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg
                          bg-gradient-to-r from-primary-500 to-primary-600 text-white text-xs font-semibold
                          shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 transition-all"
                      >
                        <Rocket className="w-3.5 h-3.5" />
                        Open API Dashboard
                      </motion.a>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto px-6 py-6">
            <AnimatePresence mode="popLayout">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
            </AnimatePresence>
            <AnimatePresence>{isLoading && <TypingIndicator />}</AnimatePresence>
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <ChatInput onSendMessage={sendMessage} isLoading={isLoading} disabled={!isSystemReady}
        docFilter={docFilter} onDocFilterChange={onDocFilterChange} />
    </div>
  );
};

export default ChatContainer;
