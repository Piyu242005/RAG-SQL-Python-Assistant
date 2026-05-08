import React, { useState, useEffect, useRef } from 'react';
import { Send, Upload, FileText, Bot, User, Loader2, RefreshCw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const API_BASE = "http://localhost:8000/api";

function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: "Hello! I'm your Enterprise RAG Assistant. Upload a document or ask me anything." }
  ]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [uploading, setUploading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post(`${API_BASE}/documents/upload`, formData);
      setMessages(prev => [...prev, { role: 'assistant', text: `Document "${file.filename}" uploaded successfully. Indexing in background...` }]);
    } catch (error) {
      console.error("Upload failed", error);
      setMessages(prev => [...prev, { role: 'assistant', text: "Failed to upload document. Please try again." }]);
    } finally {
      setUploading(false);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isStreaming) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setMessages(prev => [...prev, { role: 'assistant', text: '', isStreaming: true }]);
    setIsStreaming(true);

    try {
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMsg, session_id: 'user_1' })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantText = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              if (data.text) {
                assistantText += data.text;
                setMessages(prev => {
                  const newMsgs = [...prev];
                  newMsgs[newMsgs.length - 1].text = assistantText;
                  return newMsgs;
                });
              }
              if (data.error) {
                 assistantText = "Error: " + data.error;
                 setMessages(prev => {
                  const newMsgs = [...prev];
                  newMsgs[newMsgs.length - 1].text = assistantText;
                  return newMsgs;
                });
              }
            } catch (e) {
              console.error("Error parsing SSE", e);
            }
          }
        }
      }
    } catch (error) {
      console.error("Streaming failed", error);
      setMessages(prev => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1].text = "Failed to connect to assistant.";
        return newMsgs;
      });
    } finally {
      setIsStreaming(false);
      setMessages(prev => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1].isStreaming = false;
        return newMsgs;
      });
    }
  };

  return (
    <div className="flex flex-col h-screen p-4 md:p-8 max-w-6xl mx-auto">
      {/* Header */}
      <header className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center shadow-lg shadow-primary/20">
            <Bot className="text-white" size={24} />
          </div>
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
            Enterprise RAG
          </h1>
        </div>
        
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer glass-card px-4 py-2 hover:bg-white/10 transition-colors">
            {uploading ? <Loader2 className="animate-spin text-primary" size={20} /> : <Upload className="text-primary" size={20} />}
            <span className="text-sm font-medium">Upload PDF</span>
            <input type="file" className="hidden" accept=".pdf" onChange={handleUpload} disabled={uploading} />
          </label>
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 glass-card mb-6 flex flex-col overflow-hidden relative">
        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth"
        >
          <AnimatePresence initial={false}>
            {messages.map((msg, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex gap-3 max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    msg.role === 'user' ? 'bg-primary' : 'bg-secondary'
                  }`}>
                    {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                  </div>
                  <div className={`px-4 py-3 rounded-2xl ${
                    msg.role === 'user' 
                      ? 'bg-primary/20 text-primary-50 rounded-tr-none' 
                      : 'bg-white/5 text-slate-200 rounded-tl-none border border-white/10'
                  }`}>
                    <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                    {msg.isStreaming && !msg.text && (
                      <div className="flex gap-1 mt-1">
                        <motion.div animate={{ opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 1 }} className="w-1.5 h-1.5 bg-slate-400 rounded-full" />
                        <motion.div animate={{ opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 1, delay: 0.2 }} className="w-1.5 h-1.5 bg-slate-400 rounded-full" />
                        <motion.div animate={{ opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 1, delay: 0.4 }} className="w-1.5 h-1.5 bg-slate-400 rounded-full" />
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-white/10 bg-white/5 backdrop-blur-md">
          <div className="relative flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask a question about your documents..."
              className="w-full glass-input pr-12"
              disabled={isStreaming}
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isStreaming}
              className={`absolute right-2 p-2 rounded-lg transition-all ${
                input.trim() && !isStreaming ? 'text-primary hover:bg-primary/10' : 'text-slate-500'
              }`}
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
