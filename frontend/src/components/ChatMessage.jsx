import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Bot, User, AlertCircle, FileText, ChevronDown, ChevronUp, Hash } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import CodeBlock from './CodeBlock';

const SourceItem = ({ source, index }) => {
  const docType = source.doc_type || (source.source?.toLowerCase().includes('python') ? 'python' : 'mysql');
  const accentColor = docType === 'python' ? 'text-emerald-400' : 'text-blue-400';
  const dotColor = docType === 'python' ? 'bg-emerald-400' : 'bg-blue-400';

  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05, duration: 0.2 }}
      className="flex items-center gap-3 px-3 py-2 rounded-lg
        hover:bg-white/[0.02] transition-colors duration-200 group"
    >
      <div className={`w-1.5 h-1.5 rounded-full ${dotColor} flex-shrink-0`} />
      <div className="flex-1 min-w-0 flex items-center gap-2">
        <span className="text-[12px] text-dark-100 font-medium truncate">
          {source.source || 'Unknown'}
        </span>
        {source.page && (
          <span className="text-[10px] text-dark-400 font-mono flex-shrink-0">
            p.{source.page}
          </span>
        )}
      </div>
    </motion.div>
  );
};

const ChatMessage = ({ message }) => {
  const isUser = message.role === 'user';
  const isError = message.isError;
  const [showSources, setShowSources] = useState(false);
  const sourceCount = message.sources?.length || 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      className={`flex gap-3 mb-5 ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      {/* AI avatar */}
      {!isUser && (
        <div className="flex-shrink-0 w-7 h-7 rounded-lg bg-gradient-to-br from-primary-500 to-violet-600
          flex items-center justify-center shadow-glow-primary mt-1">
          <Bot className="w-3.5 h-3.5 text-white" />
        </div>
      )}

      <div className={`max-w-[78%] ${isUser ? 'order-first' : ''}`}>
        {/* Message bubble */}
        <div
          className={`rounded-2xl px-5 py-4 transition-all duration-200
            ${isUser
              ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg shadow-primary-600/20 rounded-br-md'
              : isError
                ? 'bg-rose-500/5 border border-rose-500/10 text-rose-300 rounded-bl-md'
                : 'bg-white dark:bg-[#151A22] border border-black/5 dark:border-white/[0.04] rounded-bl-md shadow-depth-sm'
            }`}
        >
          {isError ? (
            <div className="flex items-start gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-rose-400" />
              <p className="text-sm">{message.content}</p>
            </div>
          ) : isUser ? (
            <p className="text-sm leading-relaxed">{message.content}</p>
          ) : (
            <div className="markdown-content text-sm">
              <ReactMarkdown
                components={{
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '');
                    return !inline && match ? (
                      <CodeBlock language={match[1]} value={String(children).replace(/\n$/, '')} />
                    ) : (
                      <code className="px-1.5 py-0.5 rounded bg-primary-500/8 dark:bg-primary-500/10
                        text-primary-400 text-[0.85em] font-mono" {...props}>
                        {children}
                      </code>
                    );
                  },
                }}
              />
            </div>
          )}

          {/* Sources toggle — inside the bubble, below the answer */}
          {sourceCount > 0 && !isUser && !isError && (
            <div className="mt-4 pt-3 border-t border-black/5 dark:border-white/[0.04]">
              <button
                onClick={() => setShowSources(!showSources)}
                className="flex items-center gap-2 text-[11px] font-medium text-dark-300 hover:text-primary-400
                  transition-colors duration-200 group"
              >
                <FileText className="w-3 h-3" />
                <span>
                  {showSources ? 'Hide' : 'View'} Sources ({sourceCount})
                </span>
                {showSources
                  ? <ChevronUp className="w-3 h-3 text-dark-400" />
                  : <ChevronDown className="w-3 h-3 text-dark-400" />
                }
              </button>

              {/* Collapsible source list */}
              {showSources && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
                  className="mt-2 -mx-1"
                >
                  {message.sources.map((source, i) => (
                    <SourceItem key={i} source={source} index={i} />
                  ))}
                </motion.div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* User avatar */}
      {isUser && (
        <div className="flex-shrink-0 w-7 h-7 rounded-lg bg-gradient-to-br from-primary-400 to-violet-500
          flex items-center justify-center shadow-depth-sm mt-1">
          <User className="w-3.5 h-3.5 text-white" />
        </div>
      )}
    </motion.div>
  );
};

export default ChatMessage;
