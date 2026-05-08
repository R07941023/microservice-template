'use client';

import { useRef, useEffect, useState, FormEvent } from 'react';
import { useChat } from '@ai-sdk/react';
import { TextStreamChatTransport } from 'ai';
import { chatTexts } from '@/constants/text';
import { useAuth } from '@/context/AuthContext';

export default function ChatComponent() {
  const { token } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { messages, sendMessage, status, error } = useChat({
    transport: new TextStreamChatTransport({
      api: '/api/chat',
      headers: (): Record<string, string> => (token ? { Authorization: `Bearer ${token}` } : {}),
    }),
  });

  const isLoading = status === 'submitted' || status === 'streaming';

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    sendMessage({ text: input });
    setInput('');
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
          {messages.map((msg) => (
            <div key={msg.id} className={`flex max-w-[85%] ${msg.role === 'user' ? 'self-end' : 'self-start'}`}>
              <div className={`py-2 px-4 rounded-2xl whitespace-pre-wrap break-words ${msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}`}>
                {msg.parts
                  .filter((part) => part.type === 'text')
                  .map((part, i) => (
                    <span key={i}>{part.text}</span>
                  ))}
              </div>
            </div>
          ))}
          {error && (
            <div className="self-start max-w-[85%]">
              <div className="py-2 px-4 rounded-2xl bg-gray-200 text-gray-800">
                {chatTexts.connectionError}
              </div>
            </div>
          )}
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
          <button
            type="submit"
            disabled={isLoading}
            className="ml-2 py-2 px-4 rounded-lg border-none bg-blue-500 text-white cursor-pointer hover:bg-blue-600 disabled:bg-blue-300"
          >
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
