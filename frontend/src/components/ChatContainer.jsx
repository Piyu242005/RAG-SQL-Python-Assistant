import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Trash2, Sparkles, AlertTriangle, Database, Code2, BookOpen, Zap,
  CheckCircle2, XCircle, RefreshCw, Rocket,
} from 'lucide-react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import TypingIndicator from './TypingIndicator';

const ChatContainer = ({ healthStatus, readinessStatus, docFilter, onDocFilterChange, chat }) => {
  const { messages, isLoading, isStreaming, sendMessage, clearMessages } = chat;
  const messagesEndRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    if (messagesEndRef.current && containerRef.current) {
      const container = containerRef.current;
      const distanceFromBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
      // Only auto-scroll if we are already close to the bottom (e.g. within 100px)
      // or if it's not streaming (e.g. final update or clear)
      if (!isStreaming || distanceFromBottom < 100) {
        messagesEndRef.current.scrollIntoView({ behavior: isStreaming ? 'auto' : 'smooth' });
      }
    }
  }, [messages, isLoading, isStreaming]);

  const isSystemReady = Boolean(readinessStatus?.ready);

  const exampleQuestions = [
    { icon: Database, text: 'What are SQL JOINs and when to use each type?', color: 'from-blue-500 to-cyan-500', tag: 'SQL' },
    { icon: Code2, text: 'How do Python decorators work?', color: 'from-emerald-500 to-teal-500', tag: 'Python' },
    { icon: BookOpen, text: 'Explain MySQL indexing strategies', color: 'from-violet-500 to-purple-500', tag: 'SQL' },
    { icon: Zap, text: 'What are Python list comprehensions?', color: 'from-amber-500 to-orange-500', tag: 'Python' },
  ];

  const statusChecks = [
    { label: 'Ollama LLM', ok: healthStatus?.ollama_running, detail: healthStatus?.ollama_running ? 'Connected' : 'Not running — run ollama serve' },
    { label: 'Vector Database', ok: !readinessStatus?.reasons?.includes('VECTORSTORE_ERROR'), detail: readinessStatus?.reasons?.includes('VECTORSTORE_ERROR') ? 'Vector store error' : 'Accessible' },
    { label: 'Documents Indexed', ok: (readinessStatus?.vectorstore_docs || 0) > 0, detail: (readinessStatus?.vectorstore_docs || 0) > 0 ? `${readinessStatus.vectorstore_docs} chunks` : 'Pending' },
  ];

  return (
    <div className="flex flex-col h-full relative">
      {/* Header */}
      <header className="sticky top-0 z-10 px-6 py-4 flex-shrink-0 bg-white/70 dark:bg-[#09090B]/70 backdrop-blur-md border-b border-slate-200/50 dark:border-white/5">
        <div className="max-w-4xl mx-auto flex items-center justify-between w-full">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-primary-500/20">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-bold tracking-tight text-slate-800 dark:text-slate-100">Piyu AI Assistant</h1>
              <div className="flex items-center gap-1.5 mt-0.5">
                {isSystemReady ? (
                  <>
                    <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                    <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold uppercase tracking-wider">Ready</span>
                  </>
                ) : (
                  <>
                    <div className="h-1.5 w-1.5 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]" />
                    <span className="text-[10px] text-amber-600 dark:text-amber-400 font-semibold uppercase tracking-wider">Initializing</span>
                  </>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {messages.length > 0 && (
              <motion.button
                onClick={clearMessages}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="p-2 rounded-lg text-slate-400 hover:text-rose-500 hover:bg-rose-500/10 transition-all duration-200"
                title="Clear Conversation"
              >
                <Trash2 className="w-4 h-4" />
              </motion.button>
            )}
          </div>
        </div>
      </header>

      {/* Messages Scroll Area */}
      <div ref={containerRef} className="flex-1 overflow-y-auto scrollbar-hide bg-transparent">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center px-6">
            <div className="text-center max-w-2xl w-full py-12">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-12"
              >
                <div className="w-20 h-20 mx-auto rounded-3xl bg-gradient-to-tr from-primary-600 to-indigo-600 flex items-center justify-center shadow-2xl shadow-primary-500/40 mb-8 border border-white/20">
                  <Sparkles className="w-10 h-10 text-white" />
                </div>
                <h2 className="text-4xl font-extrabold text-slate-900 dark:text-white mb-4 tracking-tight">
                  Intelligent SQL & Python RAG
                </h2>
                <p className="text-slate-500 dark:text-slate-400 text-lg max-w-lg mx-auto font-medium">
                  Experience production-grade document intelligence. Sourced answers, real-time streaming, and high precision.
                </p>
              </motion.div>

              {/* Example Question Grid */}
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl mx-auto"
              >
                {exampleQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => sendMessage(q.text, docFilter, readinessStatus)}
                    className="group relative bg-white dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] p-5 rounded-2xl text-left hover:border-primary-500/50 dark:hover:border-primary-500/50 transition-all duration-300 hover:shadow-xl hover:shadow-primary-500/5"
                  >
                    <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${q.color} flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                      <q.icon className="w-5 h-5 text-white" />
                    </div>
                    <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest bg-slate-100 dark:bg-white/5 text-slate-500 dark:text-slate-400 mb-2">
                      {q.tag}
                    </span>
                    <p className="text-sm font-semibold text-slate-700 dark:text-slate-200 group-hover:text-primary-500 transition-colors leading-snug">
                      {q.text}
                    </p>
                  </button>
                ))}
              </motion.div>

              {/* Status Warning Card */}
              {!isSystemReady && (
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="mt-12 max-w-sm mx-auto p-4 rounded-2xl bg-amber-50 dark:bg-amber-500/5 border border-amber-200 dark:border-amber-500/20"
                >
                  <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400 mb-3 font-bold text-xs uppercase tracking-wider">
                    <AlertTriangle className="w-4 h-4" />
                    System Check Required
                  </div>
                  <div className="space-y-2">
                    {statusChecks.map((check, i) => (
                      <div key={i} className="flex items-center justify-between text-[11px] font-medium">
                        <span className="text-slate-500">{check.label}</span>
                        <span className={check.ok ? "text-emerald-500" : "text-rose-500"}>{check.ok ? "OK" : "Error"}</span>
                      </div>
                    ))}
                  </div>
                  <button 
                    onClick={() => window.location.reload()}
                    className="w-full mt-4 py-2 bg-amber-500 text-white rounded-lg text-xs font-bold shadow-lg shadow-amber-500/20 flex items-center justify-center gap-2"
                  >
                    <RefreshCw className="w-3 h-3" />
                    Retry Connection
                  </button>
                </motion.div>
              )}
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto w-full px-6 py-8">
            <AnimatePresence mode="popLayout">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
            </AnimatePresence>
            <AnimatePresence>{isLoading && <TypingIndicator />}</AnimatePresence>
            <div ref={messagesEndRef} className="h-32" />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="sticky bottom-0 bg-gradient-to-t from-white dark:from-[#09090B] via-white/90 dark:via-[#09090B]/90 to-transparent pt-10 pb-6 px-6">
        <div className="max-w-3xl mx-auto w-full">
          <ChatInput onSendMessage={(q, dt) => sendMessage(q, dt, readinessStatus)} isLoading={isLoading} disabled={!isSystemReady}
            docFilter={docFilter} onDocFilterChange={onDocFilterChange} />
          <p className="text-center text-[10px] text-slate-400 dark:text-slate-500 mt-4 font-medium uppercase tracking-widest">
            Powered by Ollama + ChromaDB + FlashRank
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatContainer;
