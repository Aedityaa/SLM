import React, { useState, useRef, useEffect } from 'react';
import { Send, Menu, Plus, Sparkles, User, Bot, X, MessageSquare, ChevronRight, AlertCircle } from 'lucide-react';
import Snowfall from 'react-snowfall';

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your Math Solving SLM agent. I can help with equations, calculus, or algebra. How can I help you today?'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    // 1. Add User Message to UI
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input; // Store for the API call
    setInput(''); // Clear input immediately
    setIsLoading(true);

    // Reset textarea height
    if (textareaRef.current) textareaRef.current.style.height = 'auto';

    try {
      // 2. Make API Call to your Python Server
      const response = await fetch('http://localhost:8000/solve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          problem: currentInput,
          max_tokens: 512,
          temperature: 0.7
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      // 3. Format the response (Solution + Final Answer)
      // We combine them to display nicely in the chat bubble
      const formattedResponse = `${data.solution}\n\n**Final Answer:**\n${data.final_answer}`;

      const aiResponse = {
        role: 'assistant',
        content: formattedResponse
      };
      
      setMessages(prev => [...prev, aiResponse]);

    } catch (error) {
      console.error('API Error:', error);
      
      const errorResponse = {
        role: 'assistant',
        content: `Error: Could not connect to the server. Please ensure your Python backend is running on port 8000.\n\nDetails: ${error.message}`
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const startNewChat = () => {
    setMessages([{ role: 'assistant', content: 'Hello! I\'m your AI assistant. How can I help you today?' }]);
    setSidebarOpen(false);
  };

  return (
    <div className="flex w-full h-screen bg-[#0a0a0f] text-slate-100 overflow-hidden font-sans selection:bg-cyan-500/30">
      
      {/* Background Elements */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-indigo-600/20 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-cyan-600/10 blur-[120px]" />
        <Snowfall
          color="rgba(255, 255, 255, 0.15)"
          snowflakeCount={60}
          style={{ width: '100%', height: '100%' }}
        />
      </div>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden transition-opacity duration-300"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed lg:static inset-y-0 left-0 z-50 w-72 bg-[#0f111a]/80 backdrop-blur-xl border-r border-white/5 transform transition-transform duration-300 ease-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="flex flex-col h-full p-4">
          <div className="flex items-center justify-between lg:justify-center mb-8 px-2">
             <div className="flex items-center gap-2 lg:hidden">
                <Sparkles className="text-cyan-400" size={20} />
                <span className="font-bold text-lg tracking-tight">SLM Agent</span>
             </div>
             <button onClick={() => setSidebarOpen(false)} className="lg:hidden p-1 text-slate-400 hover:text-white">
                <X size={20} />
             </button>
          </div>

          <button
            onClick={startNewChat}
            className="group flex items-center justify-center gap-3 px-4 py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-semibold transition-all duration-200 shadow-lg shadow-indigo-500/25 hover:shadow-cyan-500/40 transform hover:-translate-y-0.5"
          >
            <Plus size={20} className="group-hover:rotate-90 transition-transform duration-300" />
            <span>New Chat</span>
          </button>

          <div className="mt-8 mb-4 px-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Recent
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
            {/* Example History Item */}
            <div className="group flex items-center gap-3 px-4 py-3 rounded-lg bg-white/5 border border-white/5 text-slate-300 hover:bg-white/10 hover:border-white/10 cursor-pointer transition-all">
              <MessageSquare size={16} className="text-cyan-400" />
              <span className="text-sm truncate">Calculus Problem #1</span>
              <ChevronRight size={14} className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity text-slate-400" />
            </div>
          </div>

          <div className="mt-auto pt-6 border-t border-white/5">
            <div className="bg-gradient-to-b from-white/5 to-transparent rounded-xl p-4 border border-white/5">
                <div className="text-[10px] text-cyan-400 font-bold uppercase tracking-widest mb-3">Dev Team</div>
                <div className="space-y-2">
                {[
                    { name: 'Prakhar Gupta', role: 'Lead' },
                    { name: 'Ansh Agarwal', role: 'AI Eng' },
                    { name: 'Aditya Parate', role: 'Frontend' }
                ].map((dev, i) => (
                    <div key={i} className="flex items-center justify-between text-xs group">
                        <span className="text-slate-300 group-hover:text-white transition-colors">{dev.name}</span>
                    </div>
                ))}
                </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-full relative z-10 w-full">
        
        {/* Header */}
        <div className="h-16 flex items-center justify-between px-4 lg:px-6 border-b border-white/5 bg-[#0a0a0f]/50 backdrop-blur-md w-full">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg hover:bg-white/5 text-slate-300 transition-colors"
            >
              <Menu size={24} />
            </button>
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-indigo-500 to-cyan-500 p-2 rounded-lg shadow-lg shadow-indigo-500/20">
                <Sparkles className="text-white" size={20} />
              </div>
              <div>
                <h1 className="font-bold text-lg bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                  SLM Assistant
                </h1>
                <div className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    <p className="text-[10px] text-slate-400 font-medium uppercase tracking-wide">Model Active</p>
                </div>
              </div>
            </div>
          </div>
          <div className="hidden sm:block">
            <span className="px-3 py-1 rounded-full bg-white/5 border border-white/5 text-xs text-slate-400 font-mono">
              v2.1.0-beta
            </span>
          </div>
        </div>

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-4 lg:p-8 space-y-6 scroll-smooth custom-scrollbar w-full">
          <div className="max-w-6xl mx-auto space-y-6 w-full">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-4 w-full ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                } animate-in fade-in slide-in-from-bottom-4 duration-500`}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0 w-8 h-8 lg:w-10 lg:h-10 rounded-full bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/30 border border-white/10">
                    <Bot size={18} className="text-white" />
                  </div>
                )}
                
                <div
                  className={`relative px-5 py-3.5 rounded-2xl max-w-[85%] lg:max-w-[75%] leading-relaxed shadow-md ${
                    message.role === 'user'
                      ? 'bg-gradient-to-br from-indigo-600 to-cyan-600 text-white rounded-br-sm'
                      : 'bg-[#1a1d2d] border border-white/5 text-slate-200 rounded-bl-sm'
                  }`}
                >
                  <p className="whitespace-pre-wrap text-sm lg:text-base">{message.content}</p>
                </div>

                {message.role === 'user' && (
                  <div className="flex-shrink-0 w-8 h-8 lg:w-10 lg:h-10 rounded-full bg-gradient-to-br from-slate-700 to-slate-600 flex items-center justify-center shadow-lg border border-white/10">
                    <User size={18} className="text-slate-200" />
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="flex gap-4 w-full justify-start animate-pulse">
                <div className="flex-shrink-0 w-8 h-8 lg:w-10 lg:h-10 rounded-full bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center opacity-70">
                  <Bot size={18} className="text-white" />
                </div>
                <div className="px-5 py-4 rounded-2xl bg-[#1a1d2d] border border-white/5 rounded-bl-sm flex items-center gap-1.5">
                  <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                  <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                  <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} className="h-4" />
          </div>
        </div>

        {/* Input Area */}
        <div className="p-4 lg:p-6 bg-[#0a0a0f]/80 backdrop-blur-xl border-t border-white/5 w-full">
          <div className="max-w-6xl mx-auto relative w-full">
            <div className="relative flex items-end gap-2 p-2 rounded-2xl bg-[#131620] border border-white/10 shadow-xl shadow-black/20 focus-within:border-indigo-500/50 focus-within:ring-1 focus-within:ring-indigo-500/30 transition-all duration-300">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Ask a math problem (e.g., 4x + 5 = 25)..."
                className="w-full bg-transparent text-slate-200 placeholder-slate-500 text-sm lg:text-base px-4 py-3 min-h-[50px] max-h-[150px] outline-none resize-none custom-scrollbar"
                rows={1}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className="mb-1.5 mr-1.5 p-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-cyan-500 hover:from-indigo-400 hover:to-cyan-400 text-white shadow-lg shadow-indigo-500/20 disabled:opacity-40 disabled:shadow-none disabled:cursor-not-allowed transform active:scale-95 transition-all duration-200"
              >
                <Send size={18} strokeWidth={2.5} />
              </button>
            </div>
            <p className="text-[10px] text-slate-500 text-center mt-3 font-medium">
              Powered by Custom SLM • Accuracy may vary based on model training
            </p>
          </div>
        </div>

      </div>
      
      {/* Utility Styles */}
      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background-color: rgba(255, 255, 255, 0.1);
          border-radius: 20px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background-color: rgba(255, 255, 255, 0.2);
        }
      `}</style>
    </div>
  );
}