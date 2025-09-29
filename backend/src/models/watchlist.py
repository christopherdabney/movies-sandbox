from database import db
from datetime import datetime
from enum import Enum

class WatchlistStatus(str, Enum):
    QUEUED = 'queued'
    WATCHED = 'watched'

class Watchlist(db.Model):
    __tablename__ = 'watchlist'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('member.id', ondelete='CASCADE'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.Enum(WatchlistStatus), default=WatchlistStatus.QUEUED, nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    watched_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    member = db.relationship('Member', backref='watchlist_items')
    movie = db.relationship('Movie', backref='watchlist_entries')
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'userId': self.user_id,
            'movieId': self.movie_id,
            'status': self.status,
            'addedAt': self.added_at.isoformat() if self.added_at else None,
            'watchedAt': self.watched_at.isoformat() if self.watched_at else None,
        }
    
    def __repr__(self):
        return f'<Watchlist user_id={self.user_id} movie_id={self.movie_id} status={self.status}>'