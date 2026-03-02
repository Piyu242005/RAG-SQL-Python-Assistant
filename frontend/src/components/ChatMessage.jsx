import React from 'react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { User, Bot, AlertCircle } from 'lucide-react';
import CodeBlock from './CodeBlock';
import SourceCard from './SourceCard';

/**
 * Single chat message with animated entrance and themed bubbles.
 */
const ChatMessage = ({ message }) => {
  const isUser = message.type === 'user';
  const isError = message.type === 'error';

  if (isUser) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
        className="flex justify-end gap-3 mb-6"
      >
        <div className="max-w-[75%] bg-gradient-to-br from-primary-600 to-primary-700 text-white rounded-2xl rounded-tr-sm px-5 py-3 shadow-lg shadow-primary-500/10">
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
        </div>
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center flex-shrink-0 shadow-md shadow-primary-500/20">
          <User className="w-4 h-4 text-white" />
        </div>
      </motion.div>
    );
  }

  if (isError) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
        className="flex gap-3 mb-6"
      >
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-red-500 to-red-600 flex items-center justify-center flex-shrink-0 shadow-md shadow-red-500/20">
          <AlertCircle className="w-4 h-4 text-white" />
        </div>
        <div className="max-w-[75%] bg-red-500/10 border border-red-500/20 text-red-700 dark:text-red-200 rounded-2xl rounded-tl-sm px-5 py-3">
          <p className="text-sm leading-relaxed">{message.content}</p>
        </div>
      </motion.div>
    );
  }

  // Assistant message
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className="flex gap-3 mb-6"
    >
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-violet-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary-500/20">
        <Bot className="w-4 h-4 text-white" />
      </div>

      <div className="flex-1 max-w-[80%]">
        <div className="glass-card rounded-2xl rounded-tl-sm px-5 py-4">
          <div className="markdown-content text-sm">
            <ReactMarkdown
              components={{
                code({ node, inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline && match ? (
                    <CodeBlock language={match[1]}>{children}</CodeBlock>
                  ) : (
                    <code
                      className="bg-surface-100 dark:bg-surface-800/80 text-primary-600 dark:text-primary-300 px-1.5 py-0.5 rounded-md text-xs font-mono"
                      {...props}
                    >
                      {children}
                    </code>
                  );
                },
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        </div>

        {message.sources && message.sources.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="mt-3 space-y-2"
          >
            <p className="text-[10px] font-semibold text-surface-400 dark:text-surface-500 uppercase tracking-widest px-1">
              Sources ({message.sources.length})
            </p>
            <div className="space-y-2">
              {message.sources.map((source, index) => (
                <SourceCard key={index} source={source} />
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

export default ChatMessage;
