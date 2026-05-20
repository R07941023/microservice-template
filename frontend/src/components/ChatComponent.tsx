'use client';

import { useRef, useEffect, useState, useCallback, FormEvent } from 'react';
import { useChat } from '@ai-sdk/react';
import { TextStreamChatTransport } from 'ai';
import { useAuth } from '@/context/AuthContext';
import Image from 'next/image';
import { X, ArrowUp, Square, Copy, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

export default function ChatComponent() {
  const { token } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { messages, sendMessage, status, stop } = useChat({
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

  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 200) + 'px';
  }, [input]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    sendMessage({ text: input });
    setInput('');
  };

  const copyToClipboard = useCallback(async (text: string, id: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!input.trim() || isLoading) return;
      sendMessage({ text: input });
      setInput('');
    }
  };

  return (
    <div className="fixed bottom-8 right-8 z-[1000] flex flex-col items-end gap-3">
      {/* Chat Window */}
      <div
        className={`w-[700px] bg-white border border-gray-200 rounded-2xl shadow-2xl flex flex-col overflow-hidden transition-all duration-300 ease-out origin-bottom-right ${
          isOpen ? 'opacity-100 scale-100 h-[600px]' : 'opacity-0 scale-95 pointer-events-none h-0'
        }`}>
        <div className="flex items-center justify-between px-5 py-3 border-b border-gray-200 bg-white">
          <div className="flex items-center gap-2">
            <Image src="/maplestory-icon.png" alt="logo" width={28} height={28} className="rounded-full" />
            <span className="font-semibold text-gray-900 text-sm">MapleAI</span>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            className="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-md hover:bg-gray-100"
          >
            <X size={16} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-6 bg-white">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full gap-3 text-center">
              <Image src="/maplestory-icon.png" alt="logo" width={56} height={56} className="rounded-full" />
              <p className="text-gray-500 text-sm">How can I help you today?</p>
            </div>
          )}

          {messages.map((msg) => {
            const text = msg.parts.filter((p) => p.type === 'text').map((p) => p.text ?? '').join('');
            const isUser = msg.role === 'user';
            return (
              <div key={msg.id} className={`flex gap-3 items-start ${isUser ? 'justify-end' : 'justify-start'}`}>
                {!isUser && (
                  <Image src="/maplestory-icon.png" alt="assistant" width={28} height={28} className="rounded-full flex-shrink-0" />
                )}
                <div className={`group relative max-w-[85%] ${isUser ? 'order-1' : ''}`}>
                  {isUser ? (
                    <div className="bg-gray-100 text-gray-900 rounded-3xl px-4 py-2.5 text-sm whitespace-pre-wrap break-words">
                      {text}
                    </div>
                  ) : (
                    <div className="text-gray-900 text-sm leading-relaxed">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm, remarkMath]}
                        rehypePlugins={[rehypeKatex]}
                        components={{
                          p({ children }) { return <p className="mb-3 last:mb-0">{children}</p>; },
                          ul({ children }) { return <ul className="list-disc pl-5 mb-3 space-y-1">{children}</ul>; },
                          ol({ children }) { return <ol className="list-decimal pl-5 mb-3 space-y-1">{children}</ol>; },
                          li({ children }) { return <li className="text-sm">{children}</li>; },
                          h1({ children }) { return <h1 className="text-xl font-bold mb-3 mt-4">{children}</h1>; },
                          h2({ children }) { return <h2 className="text-lg font-bold mb-2 mt-3">{children}</h2>; },
                          h3({ children }) { return <h3 className="text-base font-semibold mb-2 mt-3">{children}</h3>; },
                          blockquote({ children }) {
                            return <blockquote className="border-l-4 border-gray-300 pl-4 my-3 text-gray-600 italic">{children}</blockquote>;
                          },
                          table({ children }) {
                            return <div className="overflow-x-auto my-4"><table className="min-w-full border-collapse border border-gray-200 text-sm">{children}</table></div>;
                          },
                          th({ children }) {
                            return <th className="border border-gray-200 bg-gray-50 px-3 py-2 text-left font-semibold text-gray-700">{children}</th>;
                          },
                          td({ children }) {
                            return <td className="border border-gray-200 px-3 py-2 text-gray-700">{children}</td>;
                          },
                          a({ href, children }) {
                            return <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{children}</a>;
                          },
                          strong({ children }) { return <strong className="font-semibold">{children}</strong>; },
                          hr() { return <hr className="my-4 border-gray-200" />; },
                          code({ className, children }) {
                            const match = /language-(\w+)/.exec(className || '');
                            return match ? (
                              <div className="relative my-4 rounded-xl overflow-hidden border border-gray-200">
                                <div className="flex items-center justify-between px-4 py-2 bg-gray-800 text-gray-300 text-xs">
                                  <span className="font-mono">{match[1]}</span>
                                  <CopyCodeButton code={String(children).replace(/\n$/, '')} />
                                </div>
                                <pre className="bg-gray-900 text-gray-100 px-4 py-3 text-[13px] font-mono overflow-x-auto leading-relaxed">
                                  <code>{children}</code>
                                </pre>
                              </div>
                            ) : (
                              <code className="bg-gray-100 text-gray-800 rounded px-1.5 py-0.5 text-[13px] font-mono">{children}</code>
                            );
                          },
                        }}
                      >
                        {text}
                      </ReactMarkdown>
                      <button
                        onClick={() => copyToClipboard(text, msg.id)}
                        className="mt-1 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600"
                      >
                        {copiedId === msg.id ? <><Check size={12} />Copied</> : <><Copy size={12} />Copy</>}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {isLoading && (
            <div className="flex gap-3 items-start justify-start">
              <Image src="/maplestory-icon.png" alt="assistant" width={28} height={28} className="rounded-full flex-shrink-0" />
              <div className="flex items-center gap-1 pt-2">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
        <div className="px-4 pb-4 pt-2 bg-white border-t border-gray-100">
          <form
            onSubmit={handleSubmit}
            className="relative flex items-end gap-2 bg-gray-100 rounded-2xl px-4 py-3"
          >
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question..."
              rows={1}
              className="flex-1 bg-transparent text-gray-900 text-sm placeholder-gray-500 resize-none focus:outline-none max-h-[200px] overflow-y-auto leading-relaxed"
            />
            {isLoading ? (
              <button
                type="button"
                onClick={stop}
                className="flex-shrink-0 w-8 h-8 bg-black text-white rounded-full flex items-center justify-center hover:bg-gray-800 transition-colors"
              >
                <Square size={12} fill="currentColor" />
              </button>
            ) : (
              <button
                type="submit"
                disabled={!input.trim()}
                className="flex-shrink-0 w-8 h-8 bg-black text-white rounded-full flex items-center justify-center hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                <ArrowUp size={16} strokeWidth={2.5} />
              </button>
            )}
          </form>
          <p className="text-center text-[11px] text-gray-400 mt-2">
            LLM can make mistakes. Check important info.
          </p>
        </div>
      </div>

      {/* Chat Bubble */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`w-14 h-14 rounded-full overflow-hidden shadow-lg cursor-pointer transition-all duration-300 ease-out hover:scale-110 ${
          isOpen ? 'scale-0 opacity-0' : 'scale-100 opacity-100'
        }`}
      >
        <Image src="/maplestory-icon.png" alt="open chat" width={56} height={56} />
      </button>
    </div>
  );
}


function CopyCodeButton({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="flex items-center gap-1 text-gray-400 hover:text-gray-200 transition-colors text-xs"
    >
      {copied ? <><Check size={12} />Copied</> : <><Copy size={12} />Copy code</>}
    </button>
  );
}
