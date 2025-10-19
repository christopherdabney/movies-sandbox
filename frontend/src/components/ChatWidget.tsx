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

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatWindowRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  const { account } = useSelector((state: RootState) => state.account);
  const [showLoginPrompt, setShowLoginPrompt] = useState(false);

  const [discussionPower, setDiscussionPower] = useState<{
    percentage: number;
    remaining: number;
    used: number;
    limit: number;
  } | null>(null);

  useEffect(() => {
    const handleWatchlistChange = () => {
      loadChatHistory();
    };
    
    window.addEventListener('watchlist-changed', handleWatchlistChange);
    return () => window.removeEventListener('watchlist-changed', handleWatchlistChange);
  }, []);

  useEffect(() => {
    if (isOpen && messages.length > 0) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [isOpen, messages]);

  useEffect(() => {
    if (isHovering) {
      const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
      document.body.style.overflow = 'hidden';
      document.body.style.paddingRight = `${scrollbarWidth}px`;
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

  useEffect(() => {
    const messagesContainer = messagesContainerRef.current;
    if (!messagesContainer) return;

    const handleWheel = (e: WheelEvent) => {
      const { scrollTop, scrollHeight, clientHeight } = messagesContainer;
      const isAtTop = scrollTop === 0;
      const isAtBottom = scrollTop + clientHeight >= scrollHeight;

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

  useEffect(() => {
    const handleLogout = () => {
      setMessages([]);
      setHistoryLoaded(false);
      setIsOpen(false);
    };

    window.addEventListener('user-logout', handleLogout);
    return () => window.removeEventListener('user-logout', handleLogout);
  }, []);

  useEffect(() => {
    console.log('Load history effect triggered:', { isOpen, historyLoaded, verified: account?.verified });
    if (isOpen && !historyLoaded && account?.verified) {
      console.log('Calling loadChatHistory()');
      loadChatHistory();
    }
  }, [isOpen, historyLoaded, account]);

  const loadChatHistory = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.CHAT.HISTORY, {
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages.map((msg: any) => ({
          role: msg.role,
          content: msg.content,
          recommendations: msg.recommendations || [],
          active: msg.active
        })));
        
        if (data.power) {
          setDiscussionPower({
            percentage: data.power.percentage,
            remaining: data.power.remaining
          });
        }
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
      setIsHovering(false);
    }
  };

  const isOutOfPower = discussionPower ? discussionPower.used > discussionPower.limit : false;

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isOutOfPower) return;
    
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

      if (response.status === 429) {
        const errorData = await response.json();
        const errorMessage = { 
          role: 'assistant' as const, 
          content: errorData.error || 'Insufficient discussion power to send message.' 
        };
        setMessages(prev => [...prev, errorMessage]);
        setIsLoading(false);
        return;
      }
      
      if (!response.ok) {
        throw new Error('Failed to get response');
      }
      
      const data = await response.json();
      
      const assistantMessage = { 
        role: 'assistant' as const, 
        content: data.message,
        recommendations: data.recommendations || []
      };
      setMessages(prev => [...prev, assistantMessage]);
      
      if (data.power) {
        setDiscussionPower({
          percentage: data.power.percentage,
          remaining: data.power.remaining,
          used: data.power.used,
          limit: data.power.limit
        });
      }
      
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
          
          {discussionPower && (
            <div className="discussion-power-container">
              <div className="discussion-power-bar">
                <div 
                  className="discussion-power-fill"
                  style={{ width: `${discussionPower.percentage}%` }}
                />
              </div>
              <div className="discussion-power-label">
                Discussion Power: ${discussionPower.remaining.toFixed(3)} remaining
              </div>
            </div>
          )}
                    
          {account && !account.verified ? (
            <div className="chat-verification-required">
              <h3>Email Verification Required</h3>
              <p>Please verify your email to use the chatbot.</p>
              <p>AI features are restricted to verified users only.</p>
              <button 
                onClick={async () => {
                  const response = await fetch(API_ENDPOINTS.MEMBER.RESEND, {
                    method: 'POST',
                    credentials: 'include'
                  });
                  if (response.ok) alert('Verification email sent!');
                }}
                className="resend-verification-btn"
              >
                Resend Verification Email
              </button>
            </div>
          ) : (
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
          )}

          {account?.verified && !showClearConfirm && (
            <div className="chat-input">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder={isOutOfPower ? "Discussion power depleted - no more messages available" : "Ask for a movie recommendation..."}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey && !isOutOfPower) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                rows={2}
                disabled={isOutOfPower}
              />
              <div className="chat-input-buttons">
                <button 
                  onClick={handleSendMessage} 
                  className="send-btn"
                  disabled={isOutOfPower || !inputMessage.trim()}
                >
                  Send
                </button>
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