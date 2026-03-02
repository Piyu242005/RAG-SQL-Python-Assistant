import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, Loader2, Mic, Paperclip } from 'lucide-react';

const ChatInput = ({ onSendMessage, isLoading, disabled, docFilter, onDocFilterChange }) => {
  const [input, setInput] = useState('');
  const [placeholderIdx, setPlaceholderIdx] = useState(0);
  const textareaRef = useRef(null);

  const placeholders = [
    'Ask about SQL JOINs...',
    'How do Python decorators work?',
    'Explain MySQL indexing...',
    'What are Python list comprehensions?',
  ];

  useEffect(() => {
    if (input) return;
    const iv = setInterval(() => setPlaceholderIdx((p) => (p + 1) % placeholders.length), 3500);
    return () => clearInterval(iv);
  }, [input]);

  useEffect(() => {
    const el = textareaRef.current;
    if (el) { el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 160) + 'px'; }
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
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit(e); }
  };

  const filters = [
    { value: null, label: 'All', icon: '📚' },
    { value: 'mysql', label: 'MySQL', icon: '🗄️' },
    { value: 'python', label: 'Python', icon: '🐍' },
  ];

  const canSend = input.trim() && !isLoading && !disabled;

  return (
    <div className="relative">
      <div className="absolute inset-x-0 -top-8 h-8 bg-gradient-to-t from-[#F3F4F6] dark:from-[#0B0D11] to-transparent pointer-events-none" />

      <div className="bg-[#F3F4F6] dark:bg-[#0B0D11] px-4 py-3">
        <div className="max-w-3xl mx-auto">
          {/* Chips */}
          <div className="flex items-center gap-1.5 mb-2.5">
            {filters.map((f) => (
              <motion.button
                key={f.label}
                type="button"
                onClick={() => onDocFilterChange(f.value)}
                whileTap={{ scale: 0.93 }}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200
                  ${docFilter === f.value
                    ? 'bg-primary-500/10 text-primary-400 ring-1 ring-primary-500/20'
                    : 'text-dark-300 hover:text-dark-50 hover:bg-white/[0.04]'
                  }`}
              >
                <span className="text-[10px]">{f.icon}</span>
                {f.label}
              </motion.button>
            ))}
          </div>

          {/* Input bar */}
          <form onSubmit={handleSubmit}>
            <div className="bg-white dark:bg-[#111318] rounded-xl flex items-end gap-1 p-1.5
              border border-black/5 dark:border-white/[0.04]
              shadow-depth-sm
              focus-within:border-primary-500/30 focus-within:shadow-[0_0_0_1px_rgba(99,102,241,0.15),0_0_20px_rgba(99,102,241,0.06)]
              transition-all duration-300">

              <button type="button" disabled
                className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-dark-400 opacity-30 cursor-not-allowed"
                title="Attachments (coming soon)">
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
                className="flex-1 bg-transparent text-dark-600 dark:text-dark-50
                  placeholder-dark-400 px-1.5 py-1.5
                  focus:outline-none disabled:opacity-30 disabled:cursor-not-allowed
                  resize-none text-sm leading-relaxed"
                style={{ minHeight: '32px', maxHeight: '160px' }}
              />

              <button type="button" disabled
                className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-dark-400 opacity-30 cursor-not-allowed"
                title="Voice (coming soon)">
                <Mic className="w-4 h-4" />
              </button>

              <motion.button
                type="submit"
                disabled={!canSend}
                whileHover={canSend ? { scale: 1.05 } : {}}
                whileTap={canSend ? { scale: 0.9 } : {}}
                className={`flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center transition-all duration-200 ${canSend
                    ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg shadow-primary-600/25 hover:shadow-primary-500/35'
                    : 'bg-transparent text-dark-400 cursor-not-allowed opacity-30'
                  }`}
              >
                {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </motion.button>
            </div>

            <div className="flex items-center justify-center gap-3 mt-2">
              <span className="text-[10px] text-dark-400">
                <kbd className="px-1 py-0.5 rounded bg-white/[0.04] text-dark-300 font-mono text-[9px]">Enter</kbd> send
              </span>
              <span className="text-[10px] text-dark-400">
                <kbd className="px-1 py-0.5 rounded bg-white/[0.04] text-dark-300 font-mono text-[9px]">⇧ Enter</kbd> new line
              </span>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;
