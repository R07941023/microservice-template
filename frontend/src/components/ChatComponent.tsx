'use client';

import { useState, FormEvent, useRef, useEffect } from 'react';
import { chatTexts } from '@/constants/text';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatComponent() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage, { role: 'assistant', content: '' }]);
    setInput('');

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ prompt: input }),
      });

      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        const chunk = decoder.decode(value, { stream: true });
        
        setMessages(prev => {
          const lastMessage = prev[prev.length - 1];
          const updatedLastMessage = { ...lastMessage, content: lastMessage.content + chunk };
          return [...prev.slice(0, -1), updatedLastMessage];
        });
      }
    } catch (error) {
      console.error("Error fetching streaming data:", error);
      setMessages(prev => {
          const lastMessage = prev[prev.length - 1];
          const updatedLastMessage = { ...lastMessage, content: chatTexts.connectionError };
          return [...prev.slice(0, -1), updatedLastMessage];
      });
    }
  };

  return (
    <div className="fixed bottom-8 right-8 z-[1000]">
      {/* Chat Window */}
      <div
        className={`w-[370px] h-[500px] bg-white border border-gray-200 rounded-xl shadow-lg flex flex-col overflow-hidden transition-all duration-300 ease-out origin-bottom-right ${isOpen ? 'opacity-100 scale-100' : 'opacity-0 scale-95 pointer-events-none'}`}>
        <div className="p-4 bg-gray-50 text-gray-800 flex justify-between items-center border-b border-gray-200">
          <h2 className="font-semibold text-lg">{chatTexts.headerTitle}</h2>
          <button onClick={() => setIsOpen(false)} className="text-2xl text-gray-500 hover:text-gray-800">&times;</button>
        </div>
        <div className="flex-1 p-4 overflow-y-auto flex flex-col gap-3 bg-white">
          {messages.map((msg, index) => (
            <div key={index} className={`flex max-w-[85%] ${msg.role === 'user' ? 'self-end' : 'self-start'}`}>
              <div className={`py-2 px-4 rounded-2xl whitespace-pre-wrap break-words ${msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}`}>
                {msg.content}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        <form onSubmit={handleSubmit} className="flex p-4 border-t border-gray-200 bg-gray-50">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={chatTexts.inputPlaceholder}
            className="flex-1 py-2 px-3 rounded-lg border border-gray-300 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button type="submit" className="ml-2 py-2 px-4 rounded-lg border-none bg-blue-500 text-white cursor-pointer hover:bg-blue-600 disabled:bg-blue-300">
            {chatTexts.sendButton}
          </button>
        </form>
      </div>

      {/* Chat Bubble */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`w-16 h-16 bg-blue-500 text-white rounded-full flex justify-center items-center shadow-lg cursor-pointer transition-all duration-300 ease-out hover:scale-110 ${isOpen ? 'scale-0 opacity-0' : 'scale-100 opacity-100'}`}>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-8 h-8">
          <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>
        </svg>
      </button>
    </div>
  );
}
