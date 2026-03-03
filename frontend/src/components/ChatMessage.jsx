import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, User, AlertCircle, FileText, ChevronDown, ChevronUp } from 'lucide-react';
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
        className="flex items-start gap-3 mb-5 justify-end"
      >
        <div className="max-w-xl">
          <div className="bg-gradient-to-r from-primary-500 to-primary-600 text-white
            rounded-2xl rounded-br-md px-4 py-3 shadow-lg shadow-primary-600/20">
            <p className="text-sm leading-relaxed">{message.content}</p>
          </div>
        </div>
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-primary-400 to-violet-500
          flex items-center justify-center shadow-depth-sm">
          <User className="w-4 h-4 text-white" />
        </div>
      </motion.div>
    );
  }

  /* ─── AI MESSAGE ─── */
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -6 }}
      transition={{ duration: 0.25 }}
      className="flex items-start gap-3 mb-5"
    >
      {/* Avatar — fixed 8x8 */}
      <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-violet-600
        flex items-center justify-center shadow-glow-primary">
        <Bot className="w-4 h-4 text-white" />
      </div>

      {/* Bubble + sources — single column, visually connected */}
      <div className="max-w-xl min-w-0">
        {/* Main bubble */}
        <div className={`rounded-2xl rounded-tl-md px-5 py-4 shadow-depth-sm
          ${isError
            ? 'bg-rose-500/5 border border-rose-500/10'
            : 'bg-[#151A22] border border-white/[0.04]'
          }`}
        >
          {isError ? (
            <div className="flex items-start gap-2 text-rose-300">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-rose-400" />
              <p className="text-sm">{message.content}</p>
            </div>
          ) : (
            <div className="markdown-content text-sm text-dark-100">
              <ReactMarkdown
                components={{
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '');
                    return !inline && match ? (
                      <CodeBlock language={match[1]} value={String(children).replace(/\n$/, '')} />
                    ) : (
                      <code className="px-1.5 py-0.5 rounded bg-primary-500/10
                        text-primary-400 text-[0.85em] font-mono" {...props}>
                        {children}
                      </code>
                    );
                  },
                }}
              />
            </div>
          )}

          {/* Sources toggle — INSIDE the bubble, separated by a thin divider */}
          {sourceCount > 0 && !isError && (
            <div className="mt-3 pt-3 border-t border-white/[0.05]">
              <button
                onClick={() => setShowSources(!showSources)}
                className="flex items-center gap-1.5 text-[11px] font-medium
                  text-dark-300 hover:text-primary-400 transition-colors duration-200"
              >
                <FileText className="w-3 h-3" />
                {showSources ? 'Hide' : 'View'} Sources ({sourceCount})
                {showSources
                  ? <ChevronUp className="w-3 h-3 ml-0.5" />
                  : <ChevronDown className="w-3 h-3 ml-0.5" />
                }
              </button>

              <AnimatePresence>
                {showSources && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
                    className="overflow-hidden"
                  >
                    <div className="mt-2 rounded-lg bg-[#0D0F13]/60 p-2 space-y-0.5">
                      {message.sources.map((source, i) => {
                        const isPython = source.doc_type === 'python' ||
                          source.source?.toLowerCase().includes('python');
                        return (
                          <div key={i}
                            className="flex items-center gap-2.5 px-2.5 py-1.5 rounded-md
                              hover:bg-white/[0.03] transition-colors duration-150"
                          >
                            <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0
                              ${isPython ? 'bg-emerald-400' : 'bg-blue-400'}`}
                            />
                            <span className="text-[12px] text-dark-100 truncate">
                              {source.source || 'Unknown'}
                            </span>
                            {source.page && (
                              <span className="text-[10px] text-dark-400 font-mono ml-auto flex-shrink-0">
                                p.{source.page}
                              </span>
                            )}
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
