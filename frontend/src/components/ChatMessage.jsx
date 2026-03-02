import React from 'react';
import { motion } from 'framer-motion';
import { Bot, User, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import CodeBlock from './CodeBlock';
import SourceCard from './SourceCard';

const ChatMessage = ({ message }) => {
  const isUser = message.role === 'user';
  const isError = message.isError;

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

      <div className={`max-w-[75%] ${isUser ? 'order-first' : ''}`}>
        <div
          className={`rounded-2xl px-4 py-3 transition-all duration-200
            ${isUser
              ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg shadow-primary-600/20 rounded-br-md'
              : isError
                ? 'bg-rose-500/5 border border-rose-500/10 text-rose-300 rounded-bl-md'
                : 'bg-white dark:bg-[#151A22] border border-black/5 dark:border-white/[0.04] text-dark-200 dark:text-dark-100 rounded-bl-md'
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
        </div>

        {message.sources && message.sources.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.3 }}
            className="mt-2.5 space-y-1.5"
          >
            {message.sources.map((source, i) => (
              <SourceCard key={i} source={source} index={i} />
            ))}
          </motion.div>
        )}
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
