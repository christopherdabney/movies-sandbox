from enum import Enum
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from models import Movie, Member
from models.watchlist import Watchlist
from models.chat_message import ChatMessage
from sqlalchemy.orm import joinedload
from utils.movies import extract_filters, get_allowable_ratings
from sqlalchemy.sql import func
from aiagent.claude import ClaudeClient

# Template directory constant
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / 'templates' / 'prompts'


class RecommendationTrigger(Enum):
    """Enum for recommendation trigger types"""
    CHATBOT_MESSAGE = "chatbot"
    RATING_UNLOCK = "unlock"
    WATCHLIST_QUEUED = "queued"
    WATCHLIST_SIMILAR = "watched"
    DATABASE_RANDOM = "fresh"


class RecommendationsService:
    """Handles movie recommendations via multiple triggers"""
    
    def __init__(self, member_id):
        """
        Initialize recommendations service for a specific member
        
        Args:
            member_id: Member's ID
        """
        self.member_id = member_id
        self.jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        self.claude_client = None  # Lazy loaded when AI needed
    
    def get(self, trigger, params=None):
        """
        Get recommendations based on trigger type
        
        Args:
            trigger: RecommendationTrigger value (string)
            params: Optional parameters dict for the trigger
            
        Returns:
            dict: {'message': str, 'recommendations': list}
        """
        if trigger == RecommendationTrigger.CHATBOT_MESSAGE:
            return self._get_chatbot(params)
        elif trigger == RecommendationTrigger.RATING_UNLOCK:
            return self._get_unlock(params)
        elif trigger == RecommendationTrigger.WATCHLIST_QUEUED:
            return self._get_queued()
        elif trigger == RecommendationTrigger.WATCHLIST_SIMILAR:
            return self._get_watched()
        elif trigger == RecommendationTrigger.DATABASE_RANDOM:
            return self._get_fresh()
        else:
            raise ValueError(f"Unknown trigger: {trigger}")
    
    def _get_chatbot(self, params):
        """Handle chatbot message recommendations with AI"""
        message = params.get('message')
        if not message:
            raise ValueError("message is required for chatbot trigger")
        
        # Gather context
        watchlist_movies = self._get_watchlist()
        available_movies = self._get_available_movies(message)
        
        # Build system prompt
        template = self.jinja_env.get_template('chatbot.jinja')
        context = template.render(
            watchlist_movies=watchlist_movies,
            available_movies=available_movies,
            watchlist_count=len(watchlist_movies),
            available_count=len(available_movies)
        )
        
        # Get chat history and build messages array
        ChatMessage.expire_all(self.member_id, with_commit=True)
        chat_history = self._get_chat_history()
        messages = chat_history + [{"role": "user", "content": message}]
        
        # Query Claude
        self._ensure_claude_client()
        self.claude_client.configure(context=context, message=messages)
        self.claude_client.query()
        
        return {
            'message': self.claude_client.response(),
            'recommendations': self.claude_client.movies()
        }
    
    def _get_unlock(self, params):
        """Handle newly unlocked rating recommendations (no AI)"""
        rating = params.get('rating')
        if not rating:
            raise ValueError("rating is required for unlock trigger")
        
        TOTAL_FILMS = 6
        # Get movies at the new rating only
        movies = Movie.query\
            .filter_by(rating=rating)\
            .order_by(func.random())\
            .limit(TOTAL_FILMS)\
            .all()
        
        recommendations = [
            {
                'id': m.id,
                'title': m.title,
                'year': m.release_year,
                'genre': m.genre,
                'reason': f'Newly unlocked {rating} rated movie'
            }
            for m in movies
        ]
        
        return {
            'message': '',
            'recommendations': recommendations
        }
    
    def _get_queued(self):
        """Return queued movies from watchlist (no AI)"""
        queued_items = Watchlist.query\
            .filter_by(member_id=self.member_id)\
            .filter(Watchlist.status == 'queued')\
            .options(joinedload(Watchlist.movie))\
            .all()
        
        recommendations = [
            {
                'id': item.movie.id,
                'title': item.movie.title,
                'year': item.movie.release_year,
                'genre': item.movie.genre,
                'reason': 'From your watchlist queue'
            }
            for item in queued_items
        ]
        
        return {
            'message': '',
            'recommendations': recommendations
        }
    
    def _get_watched(self):
        """Get recommendations similar to watched movies with AI"""
        # Get watched movies
        watched_items = Watchlist.query\
            .filter_by(member_id=self.member_id)\
            .filter(Watchlist.status == 'watched')\
            .options(joinedload(Watchlist.movie))\
            .all()
        
        watched_movies = [
            f"{item.movie.title} ({item.movie.release_year}) - {item.movie.genre}"
            for item in watched_items
        ]
        
        # Get available movies
        member = Member.query.get(self.member_id)
        allowed_ratings = get_allowable_ratings(member.age())
        available_movies_list = Movie.query\
            .filter(Movie.rating.in_(allowed_ratings))\
            .order_by(func.random())\
            .limit(100)\
            .all()
        
        available_movies = [
            f"{m.title} ({m.release_year}) - {m.genre} - ID:{m.id}"
            for m in available_movies_list
        ]
        
        # Build system prompt
        template = self.jinja_env.get_template('watched.jinja')
        context = template.render(
            watched_movies=watched_movies,
            available_movies=available_movies,
            watched_count=len(watched_movies),
            available_count=len(available_movies)
        )
        
        # Query Claude
        self._ensure_claude_client()
        message = "Based on my watched movies, recommend something I'd enjoy."
        self.claude_client.configure(context=context, message=message)
        self.claude_client.query()
        
        return {
            'message': self.claude_client.response(),
            'recommendations': self.claude_client.movies()
        }
    
    def _get_fresh(self):
        """Get random movies from database (no AI)"""
        member = Member.query.get(self.member_id)
        allowed_ratings = get_allowable_ratings(member.age())
        
        movies = Movie.query\
            .filter(Movie.rating.in_(allowed_ratings))\
            .order_by(func.random())\
            .limit(10)\
            .all()
        
        recommendations = [
            {
                'id': m.id,
                'title': m.title,
                'year': m.release_year,
                'genre': m.genre,
                'reason': 'Fresh pick from our collection'
            }
            for m in movies
        ]
        
        return {
            'message': '',
            'recommendations': recommendations
        }
    
    # Helper methods
    
    def _get_watchlist(self):
        """Fetch and format member's watchlist"""
        watchlist_items = Watchlist.query\
            .filter_by(member_id=self.member_id)\
            .options(joinedload(Watchlist.movie))\
            .all()
        
        # Check if status is enum or string
        return [
            f"{item.movie.title} ({item.movie.release_year}) - {item.movie.genre} - {item.status if hasattr(item.status, 'value') else item.status}"
            for item in watchlist_items
        ]
    
    def _get_available_movies(self, message):
        """Get available movies, optionally filtered by message"""
        filters = extract_filters(message)
        member = Member.query.get(self.member_id)
        allowed_ratings = get_allowable_ratings(member.age())
        
        MAX_FILMS = 100
        if filters['decades']:
            movies = Movie.find_by_filters(
                filters,
                limit=MAX_FILMS,
                allowed_ratings=allowed_ratings,
                order_by=func.random()
            )
        else:
            movies = Movie.query\
                .filter(Movie.rating.in_(allowed_ratings))\
                .order_by(func.random())\
                .limit(MAX_FILMS)\
                .all()
        
        return [
            f"{m.title} ({m.release_year}) - {m.genre} - ID:{m.id}"
            for m in movies
        ]
    
    def _get_chat_history(self):
        """Fetch recent chat history for the member"""
        messages = ChatMessage.query\
            .filter_by(member_id=self.member_id, active=True)\
            .order_by(ChatMessage.created_at.asc())\
            .all()
        
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
    
    def _ensure_claude_client(self):
        """Lazy load Claude client when needed"""
        if self.claude_client is None:
            self.claude_client = ClaudeClient()