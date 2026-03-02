import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Trash2,
  Sparkles,
  AlertTriangle,
  Database,
  Code2,
  BookOpen,
  Zap,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Rocket,
} from 'lucide-react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import TypingIndicator from './TypingIndicator';
import { useChat } from '../hooks/useChat';

/**
 * Main chat container — premium welcome, status card, gradient bg.
 */
const ChatContainer = ({ healthStatus, docFilter, onDocFilterChange }) => {
  const {
    messages,
    isLoading,
    sendMessage,
    clearMessages,
  } = useChat();

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
    {
      label: 'Ollama LLM',
      ok: healthStatus?.ollama_running,
      detail: healthStatus?.ollama_running ? 'Connected' : 'Not running — run ollama serve',
    },
    {
      label: 'Vector Database',
      ok: healthStatus?.vectorstore_initialized,
      detail: healthStatus?.vectorstore_initialized ? 'Initialized' : 'Run initialize_db.py',
    },
    {
      label: 'Documents Indexed',
      ok: healthStatus?.vectorstore_initialized,
      detail: healthStatus?.vectorstore_initialized ? 'MySQL + Python handbooks' : 'Pending initialization',
    },
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Animated gradient header line */}
      <div className="h-[2px] bg-gradient-to-r from-primary-500 via-violet-500 to-primary-500 bg-[length:200%_100%] animate-gradient-x flex-shrink-0" />

      {/* Header */}
      <header className="glass border-b border-surface-200/40 dark:border-surface-800/40 px-6 py-3 flex-shrink-0">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            {isSystemReady ? (
              <div className="flex items-center gap-1.5">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">Online</span>
              </div>
            ) : (
              <div className="flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-500 dark:text-amber-400" />
                <span className="text-[11px] text-amber-600 dark:text-amber-400 font-medium">System Not Ready</span>
              </div>
            )}
          </div>

          {messages.length > 0 && (
            <button
              onClick={clearMessages}
              className="px-3 py-1.5 rounded-lg text-surface-500 hover:text-surface-700 dark:hover:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-800/40 flex items-center gap-1.5 text-xs font-medium transition-all"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Clear
            </button>
          )}
        </div>
      </header>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto bg-gradient-to-br from-surface-50 via-white to-surface-100/50 dark:from-surface-950 dark:via-surface-950 dark:to-surface-900/30">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center px-6">
            <div className="text-center max-w-2xl w-full">
              {/* Logo + heading */}
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
                className="mb-8"
              >
                <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-primary-500 to-violet-600 flex items-center justify-center shadow-2xl shadow-primary-500/25 mb-5 ring-4 ring-primary-500/10">
                  <Sparkles className="w-8 h-8 text-white" />
                </div>
                <h2 className="text-4xl font-semibold text-surface-900 dark:text-white mb-3 tracking-tight">
                  How can I help you?
                </h2>
                <p className="text-surface-400 dark:text-surface-500 text-sm max-w-md mx-auto leading-relaxed">
                  Ask me anything about MySQL or Python. I search through the handbooks to find accurate, sourced answers.
                </p>
              </motion.div>

              {/* Example cards */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.15, ease: 'easeOut' }}
                className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg mx-auto mb-8"
              >
                {exampleQuestions.map((q, i) => (
                  <motion.button
                    key={i}
                    whileHover={{ scale: 1.03, y: -4 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => sendMessage(q.text, docFilter)}
                    className="glass-card rounded-xl p-4 text-left group
                      hover:shadow-xl hover:shadow-primary-500/5 dark:hover:shadow-black/15
                      hover:border-primary-200/40 dark:hover:border-primary-500/20 transition-all duration-200"
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${q.color} flex items-center justify-center flex-shrink-0 group-hover:shadow-lg transition-shadow duration-200`}>
                        <q.icon className="w-4 h-4 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <span className="text-[9px] font-bold uppercase tracking-wider text-surface-400 dark:text-surface-600">{q.tag}</span>
                        <p className="text-xs text-surface-600 dark:text-surface-400 group-hover:text-surface-800 dark:group-hover:text-surface-200 leading-relaxed mt-0.5 transition-colors">
                          {q.text}
                        </p>
                      </div>
                    </div>
                  </motion.button>
                ))}
              </motion.div>

              {/* System status card */}
              {!isSystemReady && (
                <motion.div
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3, duration: 0.4 }}
                  className="max-w-sm mx-auto text-left"
                >
                  <div className="rounded-2xl overflow-hidden
                    bg-white dark:bg-surface-900/80
                    border border-amber-200/60 dark:border-amber-500/15
                    shadow-lg shadow-amber-500/5 dark:shadow-black/10">

                    {/* Header */}
                    <div className="px-4 py-3 bg-amber-50 dark:bg-amber-500/5 border-b border-amber-200/50 dark:border-amber-500/10 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-md bg-amber-100 dark:bg-amber-500/10 flex items-center justify-center">
                          <AlertTriangle className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
                        </div>
                        <span className="text-xs font-semibold text-amber-800 dark:text-amber-300">System Status</span>
                      </div>
                      <button
                        onClick={() => window.location.reload()}
                        className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium
                          border border-amber-200/60 dark:border-amber-500/20
                          bg-white dark:bg-surface-800/50 hover:bg-amber-50 dark:hover:bg-amber-500/10
                          text-amber-700 dark:text-amber-400 transition-all"
                      >
                        <RefreshCw className="w-3 h-3" />
                        Retry
                      </button>
                    </div>

                    {/* Checklist */}
                    <div className="px-4 py-3 space-y-2.5">
                      {statusChecks.map((check, i) => (
                        <div key={i} className="flex items-start gap-2.5">
                          <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5
                            ${check.ok
                              ? 'bg-emerald-100 dark:bg-emerald-500/10'
                              : 'bg-red-100 dark:bg-red-500/10'
                            }`}>
                            {check.ok ? (
                              <CheckCircle2 className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
                            ) : (
                              <XCircle className="w-3 h-3 text-red-500 dark:text-red-400" />
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className={`text-xs font-medium leading-tight ${check.ok
                                ? 'text-surface-700 dark:text-surface-300'
                                : 'text-surface-800 dark:text-surface-200'
                              }`}>
                              {check.label}
                            </p>
                            <p className={`text-[10px] leading-tight mt-0.5 ${check.ok
                                ? 'text-emerald-600 dark:text-emerald-500'
                                : 'text-red-500/80 dark:text-red-400/70'
                              }`}>
                              {check.detail}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Action */}
                    <div className="px-4 pb-3">
                      <a
                        href="http://localhost:8000/docs"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg
                          bg-primary-600 hover:bg-primary-500 text-white text-xs font-medium
                          transition-all hover:shadow-lg hover:shadow-primary-500/20"
                      >
                        <Rocket className="w-3.5 h-3.5" />
                        Open API Dashboard
                      </a>
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

            <AnimatePresence>
              {isLoading && <TypingIndicator />}
            </AnimatePresence>

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input area */}
      <ChatInput
        onSendMessage={sendMessage}
        isLoading={isLoading}
        disabled={!isSystemReady}
        docFilter={docFilter}
        onDocFilterChange={onDocFilterChange}
      />
    </div>
  );
};

export default ChatContainer;
