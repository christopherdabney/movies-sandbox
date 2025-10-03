import { useState, useEffect } from 'react';
import ConfirmDialog from './ConfirmDialog';
import { API_ENDPOINTS } from '../constants/api';
import '../styles/ChatWidget.css';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Array<{role: 'user' | 'assistant', content: string}>>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);

  const handleClearChat = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.CHAT.CLEAR, {
        method: 'DELETE',
        credentials: 'include',
      });
      
      if (response.ok) {
        setMessages([]);
        setHistoryLoaded(false);
      }
    } catch (error) {
      console.error('Error clearing chat:', error);
    } finally {
      setShowClearConfirm(false);
    }
  };

  // Clear chat on logout
  useEffect(() => {
    const handleLogout = () => {
      setMessages([]);
      setHistoryLoaded(false);
      setIsOpen(false);
    };

    window.addEventListener('user-logout', handleLogout);
    return () => window.removeEventListener('user-logout', handleLogout);
  }, []);

  // Load chat history when widget opens
  useEffect(() => {
    if (isOpen && !historyLoaded) {
      loadChatHistory();
    }
  }, [isOpen]);

  const loadChatHistory = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.CHAT.HISTORY, {
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages.map((msg: any) => ({
          role: msg.role,
          content: msg.content
        })));
      }
      setHistoryLoaded(true);
    } catch (error) {
      console.error('Error loading chat history:', error);
      setHistoryLoaded(true);
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    
    // Add user message to chat
    const userMessage = { role: 'user' as const, content: inputMessage };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    
    try {
      const response = await fetch(API_ENDPOINTS.CHAT.MESSAGE, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputMessage }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to get response');
      }
      
      const data = await response.json();
      
      // Add Claude's response to chat
      const assistantMessage = { role: 'assistant' as const, content: data.message };
      setMessages(prev => [...prev, assistantMessage]);
      
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = { 
        role: 'assistant' as const, 
        content: 'Sorry, I encountered an error. Please try again.' 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating chat button */}
      <button className="chat-button" onClick={toggleChat}>
        💬
      </button>

      {/* Chat window */}
      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <h3>Movie Chat</h3>
            <div className="chat-header-actions">
              {messages.length > 0 && (
              <button 
                onClick={() => setShowClearConfirm(true)} 
                className="clear-chat-btn" 
                title="Clear chat history"
              >
                🗑️
              </button>
              )}
              <button onClick={toggleChat}>✕</button>
            </div>
          </div>
                    
          <div className="chat-messages">
            {messages.length === 0 ? (
              <div className="chat-welcome">
                👋 Hi! Ask me for movie recommendations!
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div key={idx} className={`chat-message ${msg.role}`}>
                  {msg.content}
                </div>
              ))
            )}
            {isLoading && <div className="chat-loading">Claude is thinking...</div>}
          </div>

          <div className="chat-input">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask for a movie recommendation..."
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            />
            <button onClick={handleSendMessage}>Send</button>
          </div>
        </div>
      )}
      {showClearConfirm && (
        <ConfirmDialog
          message="Are you sure you want to clear your chat history? This cannot be undone."
          onConfirm={handleClearChat}
          onCancel={() => setShowClearConfirm(false)}
        />
      )}
    </>
  );
};

export default ChatWidget;