import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, Loader2, Mic, Paperclip } from 'lucide-react';

/**
 * Floating premium input bar with focus glow, animated placeholder, mic/attach placeholders.
 */
const ChatInput = ({ onSendMessage, isLoading, disabled, docFilter, onDocFilterChange }) => {
  const [input, setInput] = useState('');
  const [placeholderIdx, setPlaceholderIdx] = useState(0);
  const textareaRef = useRef(null);

  const placeholders = [
    'Ask about SQL JOINs...',
    'How do Python list comprehensions work?',
    'Explain MySQL indexing...',
    'What are Python decorators?',
  ];

  // Rotate placeholder text
  useEffect(() => {
    if (input) return;
    const interval = setInterval(() => {
      setPlaceholderIdx((prev) => (prev + 1) % placeholders.length);
    }, 3500);
    return () => clearInterval(interval);
  }, [input]);

  // Auto-resize
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 160) + 'px';
    }
  }, [input]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input, docFilter);
      setInput('');
      if (textareaRef.current) textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const filters = [
    { value: null, label: 'All', icon: '📚' },
    { value: 'mysql', label: 'MySQL', icon: '🗄️' },
    { value: 'python', label: 'Python', icon: '🐍' },
  ];

  const canSend = input.trim() && !isLoading && !disabled;

  return (
    <div className="relative">
      {/* Subtle top shadow for floating effect */}
      <div className="absolute inset-x-0 -top-6 h-6 bg-gradient-to-t from-surface-50 dark:from-surface-950 to-transparent pointer-events-none" />

      <div className="border-t border-surface-200/40 dark:border-surface-800/40 bg-surface-50/80 dark:bg-surface-950/80 backdrop-blur-xl">
        <div className="max-w-3xl mx-auto px-4 py-3">
          {/* Filter chips */}
          <div className="flex items-center gap-1.5 mb-2.5">
            {filters.map((f) => (
              <button
                key={f.label}
                type="button"
                onClick={() => onDocFilterChange(f.value)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 ${docFilter === f.value
                    ? 'bg-primary-100 dark:bg-primary-600/20 text-primary-700 dark:text-primary-300 ring-1 ring-primary-300/60 dark:ring-primary-500/30 shadow-sm'
                    : 'text-surface-400 dark:text-surface-500 hover:text-surface-700 dark:hover:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-800/40'
                  }`}
              >
                <span className="text-[10px]">{f.icon}</span>
                {f.label}
              </button>
            ))}
          </div>

          {/* Input form */}
          <form onSubmit={handleSubmit} className="relative">
            <div className="rounded-2xl flex items-end gap-1.5 p-2
              bg-white dark:bg-surface-900/60
              border border-surface-200/80 dark:border-surface-800/60
              shadow-lg shadow-surface-900/[0.03] dark:shadow-black/10
              focus-within:ring-2 focus-within:ring-primary-500/20 focus-within:border-primary-300/50 dark:focus-within:border-primary-500/30
              transition-all duration-300">

              {/* Attachment button (future) */}
              <button
                type="button"
                disabled
                className="flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center
                  text-surface-300 dark:text-surface-600 cursor-not-allowed opacity-50"
                title="Attachments (coming soon)"
              >
                <Paperclip className="w-4 h-4" />
              </button>

              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={placeholders[placeholderIdx]}
                disabled={disabled || isLoading}
                rows={1}
                className="flex-1 bg-transparent text-surface-800 dark:text-surface-100 placeholder-surface-300 dark:placeholder-surface-600 px-2 py-2 focus:outline-none disabled:opacity-40 disabled:cursor-not-allowed resize-none text-sm leading-relaxed"
                style={{ minHeight: '36px', maxHeight: '160px' }}
              />

              {/* Mic button (future) */}
              <button
                type="button"
                disabled
                className="flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center
                  text-surface-300 dark:text-surface-600 cursor-not-allowed opacity-50"
                title="Voice input (coming soon)"
              >
                <Mic className="w-4 h-4" />
              </button>

              {/* Send button */}
              <motion.button
                type="submit"
                disabled={!canSend}
                whileHover={canSend ? { scale: 1.05 } : {}}
                whileTap={canSend ? { scale: 0.92 } : {}}
                className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200 ${canSend
                    ? 'bg-primary-600 hover:bg-primary-500 text-white shadow-lg shadow-primary-500/25'
                    : 'bg-surface-100 dark:bg-surface-800/40 text-surface-300 dark:text-surface-600 cursor-not-allowed'
                  }`}
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </motion.button>
            </div>

            {/* Keyboard hints */}
            <div className="flex items-center justify-center gap-3 mt-2">
              <span className="text-[10px] text-surface-300 dark:text-surface-600">
                <kbd className="px-1.5 py-0.5 rounded bg-surface-100 dark:bg-surface-800/50 text-surface-400 dark:text-surface-500 font-mono text-[9px]">Enter</kbd> send
              </span>
              <span className="text-[10px] text-surface-300 dark:text-surface-600">
                <kbd className="px-1.5 py-0.5 rounded bg-surface-100 dark:bg-surface-800/50 text-surface-400 dark:text-surface-500 font-mono text-[9px]">⇧ Enter</kbd> new line
              </span>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;
