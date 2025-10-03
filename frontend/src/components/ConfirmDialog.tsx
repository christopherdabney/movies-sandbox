import React from 'react';
import '../styles/ConfirmDialog.css';

interface ConfirmDialogProps {
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

const ConfirmDialog: React.FC<ConfirmDialogProps> = ({ message, onConfirm, onCancel }) => {
  return (
    <div className="confirm-overlay" onClick={onCancel}>
      <div className="confirm-dialog" onClick={(e) => e.stopPropagation()}>
        <p>{message}</p>
        <div className="confirm-actions">
          <button onClick={onCancel} className="confirm-btn cancel">
            Cancel
          </button>
          <button onClick={onConfirm} className="confirm-btn confirm">
            Clear Chat
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmDialog;