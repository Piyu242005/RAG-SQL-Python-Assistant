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
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -6 }}
        transition={{ duration: 0.25 }}
        className="flex items-start gap-3 mb-6 justify-end w-full"
      >
        <div className="max-w-[85%] sm:max-w-2xl">
          <div className="bg-gradient-to-r from-primary-600 to-indigo-600 text-white
            rounded-3xl rounded-tr-sm px-6 py-4 shadow-md shadow-primary-500/20">
            <p className="text-[15px] leading-relaxed font-medium tracking-wide">{message.content}</p>
          </div>
        </div>
      </motion.div>
    );
  }

  /* ─── AI MESSAGE ─── */
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
      className="flex items-start gap-4 mb-8 w-full"
    >
      {/* Avatar */}
      <div className="flex-shrink-0 w-9 h-9 mt-1 rounded-xl bg-gradient-to-br from-primary-500 to-violet-600
        flex items-center justify-center shadow-md shadow-primary-500/30 border border-white/10">
        <Bot className="w-5 h-5 text-white" />
      </div>

      {/* Bubble Container */}
      <div className="flex-1 min-w-0 max-w-3xl">
        <div className={`relative overflow-hidden rounded-3xl rounded-tl-sm px-6 py-5 sm:px-7 sm:py-6
          shadow-sm transition-colors duration-300
          ${isError
            ? 'bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20'
            : 'bg-white dark:bg-[#151A22] border border-black/5 dark:border-white/[0.06] shadow-[0_4px_20px_-4px_rgba(0,0,0,0.05)] dark:shadow-[0_8px_30px_-4px_rgba(0,0,0,0.4)]'
          }`}
        >
          {/* Optional decorative background glow for AI */}
          {!isError && (
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary-500/20 via-violet-500/20 to-transparent" />
          )}

          {/* Header/Title Area (Optional) */}
          {!isError && (
            <div className="flex items-center gap-2 mb-3 text-primary-600 dark:text-primary-400">
              <Sparkles className="w-4 h-4" />
              <span className="text-xs font-semibold tracking-wider uppercase">Extracted Answer</span>
            </div>
          )}

          {isError ? (
            <div className="flex items-start gap-3 text-rose-600 dark:text-rose-300">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <p className="text-[15px] leading-relaxed font-medium">{message.content}</p>
            </div>
          ) : (
            <div className="markdown-content text-[15px] text-gray-800 dark:text-gray-200">
              {message.content ? (
                <ReactMarkdown
                  components={{
                    code({ node, inline, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || '');
                      return !inline && match ? (
                        <div className="mt-4 mb-6 rounded-xl overflow-hidden shadow-sm border border-black/5 dark:border-white/10">
                          <CodeBlock language={match[1]} value={String(children).replace(/\n$/, '')} />
                        </div>
                      ) : (
                        <code className="px-1.5 py-0.5 mx-0.5 rounded-md bg-primary-50 dark:bg-primary-500/15
                          text-primary-700 dark:text-primary-300 text-[0.85em] font-mono border border-primary-100 dark:border-primary-500/20" {...props}>
                          {children}
                        </code>
                      );
                    },
                    p: ({ children }) => <p className="mb-4 last:mb-0 leading-[1.75] font-normal">{children}</p>,
                    a: ({ children, href }) => <a href={href} target="_blank" rel="noopener noreferrer" className="text-primary-600 dark:text-primary-400 hover:underline underline-offset-4 decoration-primary-500/30 transition-all font-medium">{children}</a>,
                    ul: ({ children }) => <ul className="list-disc list-outside ml-5 mb-4 space-y-2">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal list-outside ml-5 mb-4 space-y-2">{children}</ol>,
                    li: ({ children }) => <li className="leading-relaxed pl-1">{children}</li>,
                    h2: ({ children }) => <h2 className="text-xl font-bold mt-8 mb-4 text-gray-900 dark:text-white border-b border-black/5 dark:border-white/10 pb-2">{children}</h2>,
                    h3: ({ children }) => <h3 className="text-lg font-semibold mt-6 mb-3 text-gray-900 dark:text-white">{children}</h3>,
                    strong: ({ children }) => <strong className="font-semibold text-gray-900 dark:text-white bg-primary-500/5 px-1 rounded-sm">{children}</strong>,
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              ) : (
                <p className="italic text-gray-400 dark:text-gray-500">Retrieving information...</p>
              )}
            </div>
          )}

          {/* Sources Section */}
          {sourceCount > 0 && !isError && (
            <div className="mt-6 pt-4 border-t border-black/5 dark:border-white/[0.08]">
              <button
                onClick={() => setShowSources(!showSources)}
                className="group flex items-center gap-2 text-xs font-semibold uppercase tracking-wider
                  text-gray-500 hover:text-primary-600 dark:text-gray-400 dark:hover:text-primary-400 transition-colors duration-200"
              >
                <div className="flex items-center justify-center w-5 h-5 rounded bg-gray-100 dark:bg-white/5 group-hover:bg-primary-50 dark:group-hover:bg-primary-500/10 transition-colors">
                  <FileText className="w-3 h-3" />
                </div>
                View Sources ({sourceCount})
                <motion.div
                  animate={{ rotate: showSources ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                  className="ml-0.5"
                >
                  <ChevronDown className="w-3 h-3" />
                </motion.div>
              </button>

              <AnimatePresence>
                {showSources && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
                    className="overflow-hidden"
                  >
                    <div className="mt-3 grid gap-2">
                      {message.sources.map((source, i) => {
                        const isPython = source.doc_type === 'python' ||
                          (source.source && source.source.toLowerCase().includes('python'));
                        return (
                          <div key={i}
                            className="group/source flex items-center gap-3 px-3 py-2.5 rounded-lg
                              bg-gray-50 dark:bg-black/20 border border-black/5 dark:border-white/5
                              hover:border-primary-500/20 dark:hover:border-primary-500/20 hover:bg-white dark:hover:bg-white/[0.02]
                              transition-all duration-200"
                          >
                            <div className={`w-2 h-2 rounded-full flex-shrink-0 shadow-sm
                              ${isPython ? 'bg-emerald-400 shadow-emerald-400/20' : 'bg-blue-500 shadow-blue-500/20'}`}
                            />
                            <div className="flex-1 min-w-0 flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-3">
                              <span className="text-[13px] font-medium text-gray-700 dark:text-gray-300 truncate">
                                {source.source || 'Unknown Source'}
                              </span>
                              {source.page && (
                                <span className="text-[11px] font-mono text-gray-400 dark:text-gray-500 flex-shrink-0 bg-black/5 dark:bg-white/5 px-1.5 py-0.5 rounded">
                                  Page {source.page}
                                </span>
                              )}
                            </div>
                          </div>
                        );
                      })}
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
