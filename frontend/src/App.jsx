import React, { useState, useEffect } from 'react';
import ChatContainer from './components/ChatContainer';
import { getHealthStatus } from './services/api';
import { Loader2 } from 'lucide-react';

function App() {
  const [healthStatus, setHealthStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check health status on mount
    const checkHealth = async () => {
      try {
        const status = await getHealthStatus();
        setHealthStatus(status);
      } catch (error) {
        console.error('Failed to check health:', error);
        setHealthStatus({ status: 'error' });
      } finally {
        setLoading(false);
      }
    };

    checkHealth();

    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-primary-500 animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Loading RAG System...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-slate-900">
      <ChatContainer healthStatus={healthStatus} />
    </div>
  );
}

export default App;
