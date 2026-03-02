import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';

/**
 * Component for chat input with send button.
 */
const ChatInput = ({ onSendMessage, isLoading, disabled }) => {
  const [input, setInput] = useState('');
  const [docFilter, setDocFilter] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input, docFilter);
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-slate-700 bg-slate-800/50 p-4">
      {/* Filter buttons */}
      <div className="flex gap-2 mb-3">
        <button
          type="button"
          onClick={() => setDocFilter(null)}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
            docFilter === null
              ? 'bg-primary-600 text-white'
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          All Docs
        </button>
        <button
          type="button"
          onClick={() => setDocFilter('mysql')}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
            docFilter === 'mysql'
              ? 'bg-blue-600 text-white'
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          MySQL Only
        </button>
        <button
          type="button"
          onClick={() => setDocFilter('python')}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
            docFilter === 'python'
              ? 'bg-green-600 text-white'
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          Python Only
        </button>
      </div>

      {/* Input field */}
      <div className="flex gap-3">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about SQL or Python... (Shift+Enter for new line)"
          disabled={disabled || isLoading}
          rows={1}
          className="flex-1 bg-slate-700 text-slate-100 placeholder-slate-400 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed resize-none"
          style={{ minHeight: '48px', maxHeight: '120px' }}
        />
        
        <button
          type="submit"
          disabled={disabled || isLoading || !input.trim()}
          className="px-6 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* Active filter indicator */}
      {docFilter && (
        <p className="text-xs text-slate-400 mt-2">
          Searching in: <span className="font-semibold text-slate-300">
            {docFilter === 'mysql' ? 'MySQL Handbook' : 'Python Handbook'}
          </span>
        </p>
      )}
    </form>
  );
};

export default ChatInput;
