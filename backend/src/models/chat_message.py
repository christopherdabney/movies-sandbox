from database import db
from datetime import datetime

class ChatMessage(db.Model):
    __tablename__ = 'chat_message'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('member.id', ondelete='CASCADE'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    member = db.relationship('Member', backref='chat_messages')
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'userId': self.user_id,
            'role': self.role,
            'content': self.content,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<ChatMessage user_id={self.user_id} role={self.role}>'
