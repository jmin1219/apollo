'use client';

import { getCurrentUser } from '@/lib/auth';
import { User } from '@/types';
import { useEffect, useState, useRef } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface MessageResponse {
  role: string;
  content: string;
}

export default function ChatPage() {
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const [user, setUser] = useState<User | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoadingConversation, setIsLoadingConversation] = useState(true);

  // Auth check
  useEffect(() => {
    async function loadUser() {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
      } catch (error: unknown) {
        // TypeScript infers unknown automatically
        console.error('Failed to load user:', error);
        const userId = localStorage.getItem('userId') || '';
        setUser({ id: userId, email: '' } as User);
      }
    }
    loadUser();
  }, []);

  // Load las conversation on mount
  useEffect(() => {
    async function loadLastConversation() {
      if (!user) return;

      try {
        const token = localStorage.getItem('JWT_AUTH_TOKEN');

        const res = await fetch(`${API_BASE}/conversations?limit=1`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!res.ok) {
          setIsLoadingConversation(false);
          return;
        }

        const conversations = await res.json();

        if (conversations.length > 0) {
          const lastConversation = conversations[0];
          setConversationId(lastConversation.id);

          // Fetch messages for this conversation
          const messagesRes = await fetch(`${API_BASE}/conversations/${lastConversation.id}`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });

          if (messagesRes.ok) {
            const data = await messagesRes.json();
            const loadedMessages: Message[] = data.messages.map((msg: MessageResponse) => ({
              role: msg.role,
              content: msg.content,
            }));
            setMessages(loadedMessages);
          }
        }

        setIsLoadingConversation(false);
      } catch (error) {
        console.error('Error loading last conversation:', error);
        setIsLoadingConversation(false);
      }
    }

    loadLastConversation();
  }, [user]); // Run when user loads

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    // Store the input before clearing
    const userInput = input.trim();

    // Add user message to chat
    const userMessage: Message = {
      role: 'user',
      content: userInput,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);

    try {
      let currentConversationId = conversationId;

      if (!currentConversationId) {
        // This is the first message, create a new conversation
        const token = localStorage.getItem('JWT_AUTH_TOKEN');
        const createRes = await fetch(`${API_BASE}/conversations`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ title: null }), // Will auto-generate from first message
        });

        if (createRes.ok) {
          const newConversation = await createRes.json();
          currentConversationId = newConversation.id;
          setConversationId(currentConversationId);
        }
      }

      // Prepare conversation history (last 10 messages only to avoid token limits)
      const conversationHistory = messages
        .filter((m) => m.role === 'user' || m.role === 'assistant')
        .filter((m) => m.content.trim().length > 0)
        .map((m) => ({ role: m.role, content: m.content }))
        .slice(-10); // Only send last 10 messages

      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('JWT_AUTH_TOKEN')}`,
        },
        body: JSON.stringify({
          message: userInput,
          conversation_id: currentConversationId, // Add conversation_id!
          conversation_history: conversationHistory,
        }),
      });

      if (!response.ok || !response.body) {
        throw new Error('Network response was not ok');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let assistantContent = '';

      const assistantMessage: Message = { role: 'assistant', content: '' };
      setMessages((prev) => [...prev, assistantMessage]);

      let isDone = false;
      let timeout: NodeJS.Timeout | null = null;

      // Set a 30 second timeout in case stream never completes
      timeout = setTimeout(() => {
        if (!isDone) {
          console.error('Stream timeout - forcing completion');
          setIsStreaming(false);
        }
      }, 30000);

      while (true) {
        if (isDone) {
          if (timeout) clearTimeout(timeout);
          break;
        }

        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const json = JSON.parse(line.slice(6));
            if (json.type === 'chunk') {
              assistantContent += json.content;
            } else if (json.type === 'progress') {
              // Show progress message but don't add to content
              setMessages((prev) => {
                const lastMessage = prev[prev.length - 1];
                if (lastMessage && lastMessage.role === 'assistant') {
                  return [...prev.slice(0, -1), { ...lastMessage, content: json.content }];
                }
                return prev;
              });
            } else if (json.type === 'done') {
              isDone = true;
              if (timeout) clearTimeout(timeout);
              break;
            } else if (json.type === 'error') {
              isDone = true;
              if (timeout) clearTimeout(timeout);
              console.error('Stream error:', json.content);
              break;
            }

            // Update the last assistant message
            setMessages((prev) => {
              const lastMessage = prev[prev.length - 1];
              if (lastMessage && lastMessage.role === 'assistant') {
                return [...prev.slice(0, -1), { ...lastMessage, content: assistantContent }];
              }
              return prev;
            });
          }
        }
      }

      setIsStreaming(false);
    } catch (error) {
      console.error('Chat error:', error);
      setIsStreaming(false);

      // Show error message
      const errorMessage: Message = {
        role: 'assistant',
        content:
          'Sorry, something went wrong. The action may have completed - try refreshing the page.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  }

  if (!user) {
    return <div className="flex min-h-screen items-center justify-center">Loading...</div>;
  }

  function handleNewConversation() {
    setConversationId(null);
    setMessages([]);
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold">APOLLO Chat</h1>
          <div className="flex gap-4 items-center">
            <button
              onClick={handleNewConversation}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              + New Chat
            </button>
            <a href="/dashboard" className="text-sm text-gray-600 hover:text-gray-900">
              ← Dashboard
            </a>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-gray-200 text-gray-900'
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}
          {isStreaming && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-lg px-4 py-2">
                <p className="text-gray-400">●●●</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="bg-white border-t px-6 py-4">
        <form onSubmit={sendMessage} className="max-w-4xl mx-auto">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isStreaming}
              placeholder="Ask APOLLO anything..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />
            <button
              type="submit"
              disabled={isStreaming || !input.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {isStreaming ? 'Sending...' : 'Send'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
