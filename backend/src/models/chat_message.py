from database import db
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime, timedelta
from config import Config

class ChatMessage(db.Model):
    __tablename__ = 'chat_message'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id', ondelete='CASCADE'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    recommended_movie_ids = db.Column(ARRAY(db.Integer), nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True, server_default='true')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    member = db.relationship('Member', backref='chat_messages')
    
    @classmethod
    def complete_exchange(cls, member_id):
        """Mark all active messages as inactive for a given member"""
        cls.query.filter_by(member_id=member_id, active=True).update({'active': False})

    @classmethod
    def expire_all(cls, member_id, with_commit=False):
        expiry_time = datetime.utcnow() - timedelta(minutes=Config.CHAT_EXPIRY_MINUTES)
        cls.query\
            .filter_by(member_id=member_id, active=True)\
            .filter(cls.created_at < expiry_time)\
            .update({'active': False})
        if with_commit:
            db.session.commit()

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'memberId': self.member_id,
            'role': self.role,
            'content': self.content,
            'recommendedMovieIds': self.recommended_movie_ids if self.recommended_movie_ids else [],
            'active': self.active,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<ChatMessage member_id={self.member_id} role={self.role}>'
