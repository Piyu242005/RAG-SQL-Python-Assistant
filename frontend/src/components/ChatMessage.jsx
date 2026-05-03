import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, User, AlertCircle, FileText, ChevronDown, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import CodeBlock from './CodeBlock';

const ChatMessage = ({ message }) => {
  const isUser = message.type === 'user';
  const isError = message.type === 'error';
  const [showSources, setShowSources] = useState(false);
  const sourceCount = message.sources?.length || 0;

  /* ─── USER MESSAGE ─── */
  if (isUser) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -6 }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
        className="flex items-start gap-4 mb-8 justify-end w-full group"
      >
        <div className="max-w-[85%] sm:max-w-xl">
          <div className="bg-primary-600 dark:bg-primary-600 text-white
            rounded-2xl rounded-tr-sm px-5 py-3 shadow-lg shadow-primary-500/10 border border-primary-500/20">
            <p className="text-[15px] leading-relaxed font-medium tracking-tight whitespace-pre-wrap">{message.content}</p>
          </div>
          <div className="flex justify-end mt-1.5 px-1 opacity-0 group-hover:opacity-100 transition-opacity">
             <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">You</span>
          </div>
        </div>
      </motion.div>
    );
  }

  /* ─── AI MESSAGE ─── */
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
      className="flex items-start gap-4 mb-10 w-full group"
    >
      {/* Avatar */}
      <div className="flex-shrink-0 w-9 h-9 mt-1 rounded-xl bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10
        flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform duration-300">
        <Bot className="w-5 h-5 text-primary-600 dark:text-primary-400" />
      </div>

      {/* Bubble Container */}
      <div className="flex-1 min-w-0 max-w-3xl">
        <div className={`relative overflow-hidden rounded-2xl rounded-tl-sm px-6 py-5 sm:px-8 sm:py-7
          transition-all duration-300
          ${isError
            ? 'bg-rose-500/5 border border-rose-500/20 shadow-lg shadow-rose-500/5'
            : 'bg-white dark:bg-white/[0.03] border border-slate-200/60 dark:border-white/10 shadow-xl shadow-slate-200/20 dark:shadow-none backdrop-blur-sm'
          }`}
        >
          {/* Header/Title Area */}
          {!isError && (
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2 text-primary-600 dark:text-primary-400">
                <Sparkles className="w-4 h-4" />
                <span className="text-[10px] font-bold tracking-[0.2em] uppercase">AI Response</span>
              </div>
              <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest font-mono">LLM-v1.0</span>
              </div>
            </div>
          )}

          {isError ? (
            <div className="flex items-start gap-3 text-rose-600 dark:text-rose-400">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <p className="text-[15px] leading-relaxed font-bold">{message.content}</p>
            </div>
          ) : (
            <div className="markdown-content text-[16px] text-slate-700 dark:text-slate-200 leading-[1.8] font-normal">
              {message.content ? (
                <ReactMarkdown
                  components={{
                    code({ node, inline, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || '');
                      return !inline && match ? (
                        <div className="my-6 rounded-xl overflow-hidden shadow-2xl border border-black/5 dark:border-white/10">
                          <CodeBlock language={match[1]} value={String(children).replace(/\n$/, '')} />
                        </div>
                      ) : (
                        <code className="px-1.5 py-0.5 mx-0.5 rounded-md bg-slate-100 dark:bg-white/10
                          text-primary-600 dark:text-primary-400 text-[0.85em] font-mono font-semibold" {...props}>
                          {children}
                        </code>
                      );
                    },
                    p: ({ children }) => <p className="mb-4 last:mb-0">{children}</p>,
                    a: ({ children, href }) => <a href={href} target="_blank" rel="noopener noreferrer" className="text-primary-600 dark:text-primary-400 hover:underline underline-offset-4 font-bold">{children}</a>,
                    ul: ({ children }) => <ul className="list-disc list-outside ml-5 mb-5 space-y-2.5">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal list-outside ml-5 mb-5 space-y-2.5">{children}</ol>,
                    li: ({ children }) => <li className="pl-1">{children}</li>,
                    h2: ({ children }) => <h2 className="text-xl font-extrabold mt-10 mb-5 text-slate-900 dark:text-white flex items-center gap-2 pb-2 border-b border-slate-100 dark:border-white/5">{children}</h2>,
                    h3: ({ children }) => <h3 className="text-lg font-bold mt-8 mb-4 text-slate-900 dark:text-white">{children}</h3>,
                    strong: ({ children }) => <strong className="font-bold text-slate-900 dark:text-white">{children}</strong>,
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              ) : (
                <div className="space-y-3 py-2">
                  <div className="h-4 w-3/4 bg-slate-100 dark:bg-white/5 animate-pulse rounded" />
                  <div className="h-4 w-full bg-slate-100 dark:bg-white/5 animate-pulse rounded" />
                  <div className="h-4 w-5/6 bg-slate-100 dark:bg-white/5 animate-pulse rounded" />
                </div>
              )}
            </div>
          )}

          {/* Sources Section */}
          {sourceCount > 0 && !isError && (
            <div className="mt-8 pt-6 border-t border-slate-100 dark:border-white/5">
              <button
                onClick={() => setShowSources(!showSources)}
                className="group/btn flex items-center gap-2.5 text-[11px] font-bold uppercase tracking-[0.15em]
                  text-slate-400 hover:text-primary-500 transition-all duration-300"
              >
                <div className="flex items-center justify-center w-6 h-6 rounded-lg bg-slate-100 dark:bg-white/5 group-hover/btn:bg-primary-500/10 transition-colors">
                  <FileText className="w-3.5 h-3.5" />
                </div>
                Verification Sources ({sourceCount})
                <motion.div
                  animate={{ rotate: showSources ? 180 : 0 }}
                  className="ml-1"
                >
                  <ChevronDown className="w-3.5 h-3.5" />
                </motion.div>
              </button>

              <AnimatePresence>
                {showSources && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3, ease: 'circOut' }}
                    className="overflow-hidden"
                  >
                    <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {message.sources.map((source, i) => (
                        <div key={i}
                          className="flex items-center gap-3 px-4 py-3 rounded-xl
                            bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/5
                            hover:border-primary-500/30 transition-all duration-200 group/item"
                        >
                          <div className="w-8 h-8 rounded-lg bg-white dark:bg-white/10 flex items-center justify-center flex-shrink-0 shadow-sm">
                            <FileText className="w-4 h-4 text-slate-400 group-hover/item:text-primary-500 transition-colors" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-[13px] font-bold text-slate-700 dark:text-slate-200 truncate">
                              {source.source || 'Manual Document'}
                            </p>
                            <p className="text-[10px] font-mono text-slate-400 uppercase tracking-widest mt-0.5">
                              Reference • Page {source.page || 'N/A'}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default ChatMessage;
