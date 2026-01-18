import React, { useState, useRef, useEffect } from 'react';
import { api } from '../api/client';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export const FloatingAICopilot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: '👋 **Welcome to NEXUS AI Copilot!**\n\nI\'m your personal guide to the entire NEXUS Command Center. I have deep knowledge of all 7 systems and can help you:\n\n**📚 Learn & Navigate:**\n• "How do I use GPSS?"\n• "Show me how to create a project"\n• "What can VERTEX do?"\n• "Walk me through RFP analysis"\n\n**⚡ Take Action:**\n• "Add contact: John Doe john@email.com"\n• "Create opportunity for new RFP"\n• "Generate invoice from project"\n• "Find opportunities in California"\n\n**🤔 Get Advice:**\n• "What\'s my best workflow for government contracts?"\n• "How do I track my pipeline?"\n• "Should I use GPSS or DDCSS for this client?"\n\nJust ask me anything - I\'m here to help! 🚀',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize session ID and load previous conversation
  useEffect(() => {
    const initSession = () => {
      // Check if there's an active session in localStorage
      const existingSessionId = localStorage.getItem('nexus_ai_session_id');
      const sessionTimestamp = localStorage.getItem('nexus_ai_session_timestamp');
      
      // If session is older than 24 hours, start new session
      const isSessionExpired = sessionTimestamp && 
        (Date.now() - parseInt(sessionTimestamp)) > 24 * 60 * 60 * 1000;
      
      if (existingSessionId && !isSessionExpired) {
        setSessionId(existingSessionId);
        // Load previous conversation
        loadConversation(existingSessionId);
      } else {
        // Generate new session ID
        const newSessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        setSessionId(newSessionId);
        localStorage.setItem('nexus_ai_session_id', newSessionId);
        localStorage.setItem('nexus_ai_session_timestamp', Date.now().toString());
      }
    };

    initSession();
  }, []);

  // Load conversation from Airtable
  const loadConversation = async (sessionId: string) => {
    try {
      const response = await api.getConversation(sessionId);
      if (response.success && response.conversation.messages) {
        const loadedMessages = response.conversation.messages.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }));
        setMessages(loadedMessages);
      }
    } catch (error) {
      console.log('No previous conversation found or error loading:', error);
      // Keep default welcome message if no previous conversation
    }
  };

  // Save conversation to Airtable
  const saveConversation = async (updatedMessages: Message[]) => {
    if (!sessionId) return;
    
    setIsSaving(true);
    try {
      const conversationData = {
        sessionId,
        messages: updatedMessages.map(msg => ({
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp.toISOString()
        })),
        systemContext: 'General', // Could be dynamic based on current view
      };

      await api.updateConversation(sessionId, conversationData);
    } catch (error) {
      console.error('Error saving conversation:', error);
      // Don't show error to user, just log it
    } finally {
      setIsSaving(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    const updatedMessagesWithUser = [...messages, userMessage];
    setMessages(updatedMessagesWithUser);
    setInput('');
    setIsLoading(true);

    try {
      // Call the general AI chat endpoint
      const response = await api.aiChat(input, sessionId);

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response || 'I apologize, but I encountered an issue processing your request. Please try again.',
        timestamp: new Date()
      };

      const finalMessages = [...updatedMessagesWithUser, assistantMessage];
      setMessages(finalMessages);
      
      // Save conversation to Airtable
      await saveConversation(finalMessages);
    } catch (error) {
      console.error('AI Copilot error:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'I apologize, but I\'m having trouble connecting right now. Please make sure the backend server is running.',
        timestamp: new Date()
      };
      const finalMessages = [...updatedMessagesWithUser, errorMessage];
      setMessages(finalMessages);
      
      // Save conversation even with error
      await saveConversation(finalMessages);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 bg-gradient-to-br from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-full p-4 shadow-2xl hover:shadow-blue-500/50 transition-all duration-300 hover:scale-110 group"
        title="AI Copilot"
      >
        <div className="relative">
          <span className="text-2xl">🤖</span>
          {!isOpen && (
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
          )}
        </div>
        
        {/* Tooltip */}
        <div className="absolute bottom-full right-0 mb-2 px-3 py-1 bg-gray-900 text-white text-xs rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
          AI Copilot
        </div>
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-50 w-96 h-[600px] bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-fadeIn">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="text-2xl">🤖</div>
              <div>
                <h3 className="font-bold text-white">NEXUS AI Copilot</h3>
                <p className="text-xs text-blue-100">
                  {isSaving ? '💾 Saving...' : '✓ Auto-saved'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  if (window.confirm('Start a new conversation? Current conversation will be saved.')) {
                    const newSessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
                    setSessionId(newSessionId);
                    localStorage.setItem('nexus_ai_session_id', newSessionId);
                    localStorage.setItem('nexus_ai_session_timestamp', Date.now().toString());
                    setMessages([{
                      role: 'assistant',
                      content: '👋 **Welcome to NEXUS AI Copilot!**\n\nI\'m your personal guide to the entire NEXUS Command Center. I have deep knowledge of all 7 systems and can help you:\n\n**📚 Learn & Navigate:**\n• "How do I use GPSS?"\n• "Show me how to create a project"\n• "What can VERTEX do?"\n• "Walk me through RFP analysis"\n\n**⚡ Take Action:**\n• "Add contact: John Doe john@email.com"\n• "Create opportunity for new RFP"\n• "Generate invoice from project"\n• "Find opportunities in California"\n\n**🤔 Get Advice:**\n• "What\'s my best workflow for government contracts?"\n• "How do I track my pipeline?"\n• "Should I use GPSS or DDCSS for this client?"\n\nJust ask me anything - I\'m here to help! 🚀',
                      timestamp: new Date()
                    }]);
                  }
                }}
                className="text-white hover:bg-white/20 rounded-lg p-1 transition-all"
                title="New Conversation"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white hover:bg-white/20 rounded-lg p-1 transition-all"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-100 border border-gray-700'
                  }`}
                >
                  <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                  <div
                    className={`text-xs mt-1 ${
                      msg.role === 'user' ? 'text-blue-200' : 'text-gray-500'
                    }`}
                  >
                    {formatTime(msg.timestamp)}
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-800 border border-gray-700 rounded-lg p-3">
                  <div className="flex gap-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-700 bg-gray-800">
            <div className="flex gap-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything..."
                className="flex-1 bg-gray-900 text-white border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                rows={2}
                disabled={isLoading}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg px-4 py-2 font-semibold transition-all"
              >
                {isLoading ? '...' : '→'}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">Press Enter to send, Shift+Enter for new line</p>
          </div>
        </div>
      )}
    </>
  );
};
