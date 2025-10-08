import { useState, useEffect, useRef } from 'react';
import { API_ENDPOINTS } from '../constants/api';
import MovieRecommendationTile from './MovieRecommendationTile';
import { useSelector } from 'react-redux';
import LoginPrompt from './LoginPrompt';
import type { RootState } from '../store/store';
import type { Movie } from '../types';
import '../styles/ChatWidget.css';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Array<{
    role: 'user' | 'assistant', 
    content: string,
    recommendations?: Array<Movie & {reason?: string}>
  }>>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  
  const [isHovering, setIsHovering] = useState(false);

  // Add ref for messages container
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatWindowRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  const { account } = useSelector((state: RootState) => state.account);
  const [showLoginPrompt, setShowLoginPrompt] = useState(false);

  useEffect(() => {
    const handleWatchlistChange = () => {
      loadChatHistory();
    };
    
    window.addEventListener('watchlist-changed', handleWatchlistChange);
    return () => window.removeEventListener('watchlist-changed', handleWatchlistChange);
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    // Only scroll if opening the chat and there are messages
    if (isOpen && messages.length > 0) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [isOpen, messages]);

  // Prevent background scroll when hovering over chat
useEffect(() => {
  if (isHovering) {
    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
    document.body.style.overflow = 'hidden';
    document.body.style.paddingRight = `${scrollbarWidth}px`;
    // Also shift the chat widget
    if (chatWindowRef.current) {
      chatWindowRef.current.style.right = `${20 + scrollbarWidth}px`;
    }
  } else {
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
    if (chatWindowRef.current) {
      chatWindowRef.current.style.right = '20px';
    }
  }
  return () => {
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
    if (chatWindowRef.current) {
      chatWindowRef.current.style.right = '20px';
    }
  };
}, [isHovering]);

  // Prevent scroll propagation from messages container
  useEffect(() => {
    const messagesContainer = messagesContainerRef.current;
    if (!messagesContainer) return;

    const handleWheel = (e: WheelEvent) => {
      const { scrollTop, scrollHeight, clientHeight } = messagesContainer;
      const isAtTop = scrollTop === 0;
      const isAtBottom = scrollTop + clientHeight >= scrollHeight;

      // Prevent scroll propagation in all cases
      if ((e.deltaY < 0 && isAtTop) || (e.deltaY > 0 && isAtBottom) || (!isAtTop && !isAtBottom)) {
        e.stopPropagation();
      }
    };

    messagesContainer.addEventListener('wheel', handleWheel, { passive: true });
    
    return () => {
      messagesContainer.removeEventListener('wheel', handleWheel);
    };
  }, [isOpen]);

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

  const handleCancelClear = () => {
    setShowClearConfirm(false);
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
        console.log('Chat history:', data.messages);
        setMessages(data.messages.map((msg: any) => ({
          role: msg.role,
          content: msg.content,
          recommendations: msg.recommendations || [],
          active: msg.active
        })));
      }
      setHistoryLoaded(true);
    } catch (error) {
      console.error('Error loading chat history:', error);
      setHistoryLoaded(true);
    }
  };

  const toggleChat = () => {
    if (!account) {
      setShowLoginPrompt(true);
      return;
    }
    if (showClearConfirm) {
      setShowClearConfirm(false);
    }
    setIsOpen(!isOpen);
    if (isOpen) {
      // Closing chat, ensure scroll lock is reset
      setIsHovering(false);
    }
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
      const assistantMessage = { 
        role: 'assistant' as const, 
        content: data.message,
        recommendations: data.recommendations || []
      };
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
      {/* Chat window */}
      {isOpen && (
        <div 
          className="chat-window" 
          ref={chatWindowRef}
          onMouseEnter={() => setIsHovering(true)}
          onMouseLeave={() => setIsHovering(false)}
        >
          <div className="chat-header">
            <h3>Movie Chat</h3>
            <div className="chat-header-actions">
              <button onClick={toggleChat} title="Minimize">−</button>
            </div>
          </div>
                    
          <div className="chat-messages" ref={messagesContainerRef}>
            {showClearConfirm ? (
              <div className="chat-confirm">
                <p>Are you sure you want to clear your chat history? This cannot be undone.</p>
                <div className="chat-confirm-actions">
                  <button onClick={handleCancelClear} className="confirm-cancel-btn">
                    Cancel
                  </button>
                  <button onClick={handleClearChat} className="confirm-delete-btn">
                    Delete
                  </button>
                </div>
              </div>
            ) : (
              <>
                {messages.length === 0 ? (
                  <div className="chat-welcome">
                    👋 Hi! Ask me for movie recommendations!
                  </div>
                ) : (
                  messages.map((msg, idx) => (
                    <div key={idx}>
                      <div className={`chat-message ${msg.role}${msg.active === false ? ' inactive' : ''}`}>
                        {msg.content}
                      </div>
                      {msg.role === 'assistant' && msg.recommendations && msg.recommendations.length > 0 && (
                        <div className="recommendations-container">
                          {msg.recommendations.map((movie) => (
                            <MovieRecommendationTile 
                              key={movie.id} 
                              movie={movie}
                              reason={movie.reason}
                            />
                          ))}
                        </div>
                      )}
                    </div>
                  ))
                )}
                {isLoading && <div className="chat-loading">Claude is thinking...</div>}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {!showClearConfirm && (
            <div className="chat-input">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask for a movie recommendation..."
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                rows={2}
              />
              <div className="chat-input-buttons">
                <button onClick={handleSendMessage} className="send-btn">Send</button>
                {messages.length > 0 && (
                  <button 
                    onClick={() => setShowClearConfirm(true)} 
                    className="clear-chat-btn"
                    title="Clear chat history"
                  >
                    Clear
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      )}
      {!isOpen && !showLoginPrompt && (
        <button className="chat-button" onClick={toggleChat}>
          💬
        </button>
      )}
      {showLoginPrompt && (
        <LoginPrompt onClose={() => setShowLoginPrompt(false)} />
      )}
    </>
  );
};

export default ChatWidget;