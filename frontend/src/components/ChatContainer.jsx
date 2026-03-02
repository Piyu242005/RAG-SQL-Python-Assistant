import React, { useEffect, useRef } from 'react';
import { Trash2, Database, AlertTriangle, CheckCircle } from 'lucide-react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { useChat } from '../hooks/useChat';

/**
 * Main chat container component.
 */
const ChatContainer = ({ healthStatus }) => {
  const { messages, isLoading, error, sendMessage, clearMessages } = useChat();
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const isSystemReady = healthStatus?.ollama_running && healthStatus?.vectorstore_initialized;

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-slate-700 bg-slate-800/80 backdrop-blur-sm px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              <Database className="w-6 h-6 text-primary-500" />
              SQL & Python Assistant
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Ask questions about MySQL and Python from the handbooks
            </p>
          </div>

          {messages.length > 0 && (
            <button
              onClick={clearMessages}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg flex items-center gap-2 text-sm transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              Clear Chat
            </button>
          )}
        </div>

        {/* Status indicator */}
        <div className="mt-3 flex items-center gap-2">
          {isSystemReady ? (
            <>
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span className="text-xs text-green-400 font-medium">System Ready</span>
            </>
          ) : (
            <>
              <AlertTriangle className="w-4 h-4 text-yellow-400" />
              <span className="text-xs text-yellow-400 font-medium">System Not Ready</span>
            </>
          )}
        </div>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center max-w-2xl">
              <Database className="w-16 h-16 text-primary-500 mx-auto mb-4 opacity-50" />
              <h2 className="text-2xl font-bold text-white mb-3">
                Welcome to the RAG Assistant
              </h2>
              <p className="text-slate-400 mb-6">
                Ask me anything about SQL (MySQL) or Python programming. I'll search through the handbooks to find the best answers for you.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
                <div className="bg-slate-700/30 border border-slate-600 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-blue-300 mb-2">Example SQL Questions:</h3>
                  <ul className="text-xs text-slate-400 space-y-1">
                    <li>• What are SQL JOINs?</li>
                    <li>• How do I create a MySQL table?</li>
                    <li>• Explain the SELECT statement</li>
                  </ul>
                </div>
                
                <div className="bg-slate-700/30 border border-slate-600 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-green-300 mb-2">Example Python Questions:</h3>
                  <ul className="text-xs text-slate-400 space-y-1">
                    <li>• How do I create a Python class?</li>
                    <li>• What are list comprehensions?</li>
                    <li>• Explain Python decorators</li>
                  </ul>
                </div>
              </div>

              {!isSystemReady && (
                <div className="mt-6 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                  <p className="text-sm text-yellow-400">
                    ⚠️ System is not fully ready. Please ensure:
                  </p>
                  <ul className="text-xs text-yellow-300 mt-2 text-left space-y-1">
                    {!healthStatus?.ollama_running && <li>• Ollama is running</li>}
                    {!healthStatus?.vectorstore_initialized && <li>• Database is initialized (run initialize_db.py)</li>}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input area */}
      <ChatInput
        onSendMessage={sendMessage}
        isLoading={isLoading}
        disabled={!isSystemReady}
      />
    </div>
  );
};

export default ChatContainer;
