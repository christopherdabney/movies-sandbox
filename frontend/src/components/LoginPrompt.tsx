import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/LoginPrompt.css';

interface LoginPromptProps {
  onClose: () => void;
}

const LoginPrompt: React.FC<LoginPromptProps> = ({ onClose }) => {
  const navigate = useNavigate();

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h2>Sign in to save movies</h2>
        <p>Create an account to build your watchlist</p>
        <div className="modal-actions">
          <button onClick={() => navigate('/login')} className="modal-btn primary">
            Log In
          </button>
          <button onClick={() => navigate('/register')} className="modal-btn secondary">
            Create Account
          </button>
          <button onClick={onClose} className="modal-btn cancel">
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginPrompt;