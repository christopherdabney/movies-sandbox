import os
import re
import json
from anthropic import Anthropic
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from models import Movie, Member
from models.watchlist import Watchlist
from models.chat_message import ChatMessage
from sqlalchemy.orm import joinedload
from utils.movies import extract_filters
from utils.movies import get_allowable_ratings

ROLE_USER = 'user'  # move this to ChatMessage or elsewhere?

class RecommendationsService:
    """Handles Claude AI interaction and response processing"""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        
        # Setup Jinja environment for prompt templates
        template_dir = Path(__file__).resolve().parent.parent / 'templates' / 'prompts'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    def get(self, member_id, message):
        """
        Get movie recommendation from Claude
        
        Args:
            member_id: Member's ID for fetching watchlist
            message: Member's question/request
            
        Returns:
            dict: {
                'message': str,
                'recommendations': list of {title, year, id}
            }
        """
        # Gather members's watchlist
        watchlist_movies = self._get_watchlist(member_id)
        
        # Get available movies (with optional filtering)
        available_movies = self._get_available_movies(message, member_id)
        
        # Build system prompt with context included
        system_prompt = self._build_system_prompt(watchlist_movies, available_movies)
        
        # Fetch chat history
        ChatMessage.expire_all(member_id, with_commit=True)
        chat_history = self._get_chat_history(member_id)
        
        # Build messages array with history + current message
        messages = chat_history + [
            {"role": ROLE_USER, "content": message}
        ]
        
        # Call Claude API
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            system=system_prompt,
            messages=messages
        )
        
        # Parse response
        return self._parse_response(response.content[0].text)
    
    def _get_watchlist(self, member_id):
        """Fetch and format members's watchlist"""
        watchlist_items = Watchlist.query\
            .filter_by(member_id=member_id)\
            .options(joinedload(Watchlist.movie))\
            .all()
        
        return [
            f"{item.movie.title} ({item.movie.release_year}) - {item.movie.genre} - {item.status.value}"
            for item in watchlist_items
        ]
    
    def _get_available_movies(self, message, member_id):
        """Get available movies, optionally filtered by message"""
        filters = extract_filters(message)

        member = Member.query.get(member_id)
        allowed_ratings = get_allowable_ratings(member.calculate_age())

        # Build query with age filter
        MAX_FILMS = 100
        if filters['decades']:
            movies = Movie.find_by_filters(filters, limit=MAX_FILMS, allowed_ratings=allowed_ratings)
        else:
            movies = Movie.query.filter(Movie.rating.in_(allowed_ratings)).limit(MAX_FILMS).all()
    

        return [
            f"{m.title} ({m.release_year}) - {m.genre} - ID:{m.id}"
            for m in movies
        ]
    
    def _build_system_prompt(self, watchlist_movies, available_movies):
        """Build system prompt from template with context included"""
        template = self.jinja_env.get_template('system.jinja')
        return template.render(
            watchlist_movies=watchlist_movies,
            available_movies=available_movies,
            watchlist_count=len(watchlist_movies),
            available_count=len(available_movies)
        )
    
    def _get_chat_history(self, member_id):
        """
        Fetch recent chat history for the member (active messages only)
        
        Returns:
            list of message dicts with 'role' and 'content' keys
        """
        messages = ChatMessage.query\
            .filter_by(member_id=member_id, active=True)\
            .order_by(ChatMessage.created_at.asc())\
            .all()
        
        history = []
        for msg in messages:
            history.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return history
    
    def _parse_response(self, response_text):
        """
        Parse Claude's response as JSON
        
        Returns:
            dict with 'message' and 'recommendations' keys
        """
        # Try to extract JSON from response text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                return {
                    'message': parsed.get('message', ''),
                    'recommendations': parsed.get('recommendations', [])
                }
            except json.JSONDecodeError:
                pass
        
        # Fallback
        return {'message': response_text, 'recommendations': []}