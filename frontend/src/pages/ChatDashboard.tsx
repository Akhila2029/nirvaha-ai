import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Plus, History, LogOut, User, Sparkles, Loader2, Menu, X, Trash2 } from 'lucide-react';
import api from '../lib/api';
import ChatBubble from '../components/chat/ChatBubble';
import { cn } from '../lib/utils';

const ChatDashboard = () => {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const resp = await api.post('/chat', {
        message: input
      });
      
      setMessages((prev) => [...prev, { role: 'assistant', content: resp.data.response }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'assistant', content: "I'm sorry, I'm having trouble connecting right now. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  const startNewChat = () => {
    setMessages([]);
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <AnimatePresence mode="wait">
        {isSidebarOpen && (
          <motion.aside
            initial={{ x: -300 }}
            animate={{ x: 0 }}
            exit={{ x: -300 }}
            className="w-80 h-full glass border-r border-slate-200 flex flex-col z-20"
          >
            <div className="p-6 flex justify-between items-center">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-white font-bold">N</div>
                <span className="text-xl font-bold tracking-tight">Nirvaha</span>
              </div>
              <button 
                onClick={() => setIsSidebarOpen(false)}
                className="p-1 hover:bg-slate-100 rounded-lg transition-colors md:hidden"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <button
              onClick={startNewChat}
              className="mx-4 mb-6 p-4 border border-dashed border-primary/30 rounded-2xl flex items-center justify-center gap-2 hover:bg-primary/5 transition-all group"
            >
              <Plus className="w-5 h-5 text-primary group-hover:scale-110 transition-transform" />
              <span className="font-semibold text-primary">New Sanctuary</span>
            </button>

            <div className="flex-1 overflow-y-auto px-4 space-y-2 custom-scrollbar">
              <div className="flex flex-col items-center justify-center p-8 text-center opacity-30">
                <Sparkles className="w-8 h-8 mb-2" />
                <p className="text-xs font-medium">Session history is currently local.</p>
              </div>
            </div>

            <div className="p-6 border-t border-slate-200">
              <p className="text-[10px] text-muted-foreground uppercase tracking-widest text-center px-4 font-bold">
                Nirvaha Minimal RAG
              </p>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col relative min-w-0">
        {!isSidebarOpen && (
          <button 
            onClick={() => setIsSidebarOpen(true)}
            className="absolute top-6 left-6 p-2 bg-white shadow-lg border border-slate-200 rounded-xl z-10 hover:scale-105 transition-all"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 md:p-10 space-y-2">
          <div className="max-w-4xl mx-auto flex flex-col h-full">
            {messages.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center text-center opacity-50">
                <div className="w-20 h-20 bg-primary/5 rounded-full flex items-center justify-center mb-6">
                  <Sparkles className="w-10 h-10 text-primary" />
                </div>
                <h2 className="text-3xl font-bold mb-2">Welcome to Your Sanctuary</h2>
                <p className="max-w-sm">I'm here to listen without judgment. How are you feeling today?</p>
              </div>
            ) : (
              <>
                {messages.map((m, i) => (
                  <ChatBubble key={i} role={m.role} content={m.content} />
                ))}
                {loading && (
                  <div className="flex justify-start mb-4">
                    <div className="glass px-6 py-4 rounded-[1.5rem] rounded-tl-none border border-slate-200 flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin text-primary" />
                      <span className="text-sm text-muted-foreground">Nirvaha is thinking...</span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>
        </div>

        {/* Input Area */}
        <div className="p-6 md:p-10">
          <div className="max-w-4xl mx-auto">
            <form 
              onSubmit={handleSendMessage}
              className="glass p-2 pl-6 rounded-3xl border border-slate-200 flex items-center gap-2 shadow-2xl shadow-primary/5"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Share what's on your mind..."
                className="flex-1 bg-transparent py-4 outline-none text-base"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={!input.trim() || loading}
                className="p-4 bg-primary text-white rounded-2xl disabled:opacity-50 hover:shadow-lg transition-all active:scale-95"
              >
                <Send className="w-5 h-5" />
              </button>
            </form>
            <p className="text-center text-[10px] text-muted-foreground mt-4 uppercase tracking-[0.2em] font-bold">
              Nirvaha is an AI companion and does not provide medical advice.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ChatDashboard;
