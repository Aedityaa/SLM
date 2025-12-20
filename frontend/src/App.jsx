import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, User, Bot } from 'lucide-react';
import Snowfall from 'react-snowfall';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    // Clear backend memory on page load
    fetch('http://localhost:8000/reset', { method: 'POST' }).catch(console.error);
  }, []);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    
    const currentInput = input;
    setInput('');
    setIsLoading(true);

    try {
      // Standard JSON Call
      const response = await fetch('http://localhost:8000/solve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          problem: currentInput,
          max_tokens: 2048,
          temperature: 0.7
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      const aiResponse = { role: 'assistant', content: data.response };
      setMessages(prev => [...prev, aiResponse]);

    } catch (error) {
      console.error('API Error:', error);
      const errorResponse = { role: 'assistant', content: `Error: ${error.message}` };
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

  return (
    <div className="flex w-full h-screen bg-[#0a0a0f] text-slate-100 overflow-hidden font-sans selection:bg-cyan-500/30">
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-indigo-600/20 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-cyan-600/10 blur-[120px]" />
        <Snowfall color="rgba(255, 255, 255, 0.15)" snowflakeCount={60} style={{ width: '100%', height: '100%' }} />
      </div>

      <div className="flex-1 flex flex-col h-full relative z-10 w-full">
        <div className="h-16 flex items-center justify-between px-6 border-b border-white/5 bg-[#0a0a0f]/50 backdrop-blur-md">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-indigo-500 to-cyan-500 p-2 rounded-lg">
                <Sparkles className="text-white" size={20} />
              </div>
              <h1 className="font-bold text-lg bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                SLM Assistant
              </h1>
            </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 lg:p-8 space-y-6 scroll-smooth custom-scrollbar">
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((message, index) => (
              <div key={index} className={`flex gap-4 w-full ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center border border-white/10">
                    <Bot size={18} className="text-white" />
                  </div>
                )}
                
                <div className={`relative px-5 py-3.5 rounded-2xl max-w-[85%] lg:max-w-[75%] leading-relaxed shadow-md ${
                  message.role === 'user' ? 'bg-gradient-to-br from-indigo-600 to-cyan-600 text-white rounded-br-sm' : 'bg-[#1a1d2d] border border-white/5 text-slate-200 rounded-bl-sm'
                }`}>
                  <div className="text-sm lg:text-base overflow-hidden">
                    <ReactMarkdown 
                        remarkPlugins={[remarkMath]} 
                        rehypePlugins={[rehypeKatex]}
                        components={{
                            code: ({node, inline, className, children, ...props}) => (
                                <code className={`${className} ${inline ? 'bg-black/20 rounded px-1' : 'block bg-black/30 p-2 rounded my-2 overflow-x-auto'}`} {...props}>
                                    {children}
                                </code>
                            )
                        }}
                    >
                      {message.content}
                    </ReactMarkdown>
                  </div>
                </div>

                {message.role === 'user' && (
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-slate-700 to-slate-600 flex items-center justify-center border border-white/10">
                    <User size={18} className="text-slate-200" />
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
               <div className="flex gap-4 w-full justify-start animate-pulse">
                 <div className="flex-shrink-0 w-10 h-10 rounded-full bg-indigo-600/50" />
                 <div className="px-5 py-4 rounded-2xl bg-[#1a1d2d] border border-white/5 flex items-center gap-1.5">
                   <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" />
                   <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce delay-100" />
                   <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce delay-200" />
                 </div>
               </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        <div className="p-4 lg:p-6 bg-[#0a0a0f]/80 backdrop-blur-xl border-t border-white/5">
          <div className="max-w-4xl mx-auto">
            <div className="relative flex items-end gap-2 p-2 rounded-2xl bg-[#131620] border border-white/10 shadow-xl focus-within:border-indigo-500/50 transition-all">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Ask a math problem..."
                className="w-full bg-transparent text-slate-200 placeholder-slate-500 text-sm lg:text-base px-4 py-3 min-h-[50px] max-h-[150px] outline-none resize-none custom-scrollbar"
                rows={1}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className="mb-1.5 mr-1.5 p-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-cyan-500 hover:from-indigo-400 hover:to-cyan-400 text-white disabled:opacity-40 disabled:cursor-not-allowed transform active:scale-95 transition-all"
              >
                <Send size={18} strokeWidth={2.5} />
              </button>
            </div>
          </div>
        </div>
      </div>
       <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background-color: rgba(255, 255, 255, 0.1); border-radius: 20px; }
      `}</style>
    </div>
  );
}