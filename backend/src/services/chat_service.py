import os
import json
from anthropic import Anthropic
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from models import Movie
from models.watchlist import Watchlist
from sqlalchemy.orm import joinedload

class ChatService:
    """Handles Claude AI interaction and response processing"""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        
        # Setup Jinja environment for prompt templates
        template_dir = Path(__file__).resolve().parent.parent / 'templates' / 'prompts'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    def get_recommendation(self, member_id, user_message):
        """
        Get movie recommendation from Claude
        
        Args:
            member_id: User's ID for fetching watchlist
            user_message: User's question/request
            
        Returns:
            dict: {
                'message': str,
                'recommendations': list of {title, year, id}
            }
        """
        # Gather user's watchlist
        watchlist_movies = self._get_watchlist(member_id)
        
        # Get available movies (with optional filtering)
        available_movies = self._get_available_movies(user_message)
        
        # Build context from templates
        system_prompt = self._build_system_prompt()
        context = self._build_context(watchlist_movies, available_movies)
        
        # Call Claude API
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"{context}\n\nUser question: {user_message}"}
            ]
        )
        
        # Parse response
        return self._parse_response(response.content[0].text)
    
    def _get_watchlist(self, member_id):
        """Fetch and format user's watchlist"""
        watchlist_items = Watchlist.query\
            .filter_by(user_id=member_id)\
            .options(joinedload(Watchlist.movie))\
            .all()
        
        return [
            f"{item.movie.title} ({item.movie.release_year}) - {item.movie.genre} - {item.status}"
            for item in watchlist_items
        ]
    
    def _get_available_movies(self, user_message):
        """Get available movies, optionally filtered by user message"""
        filters = Movie.extract_filters(user_message)
        
        if filters['decades']:
            movies = Movie.find_by_filters(filters, limit=100)
        else:
            movies = Movie.query.limit(100).all()
        
        return [
            f"{m.title} ({m.release_year}) - {m.genre} - ID:{m.id}"
            for m in movies
        ]
    
    def _build_system_prompt(self):
        """Build system prompt from template"""
        template = self.jinja_env.get_template('system.jinja')
        return template.render()
    
    def _build_context(self, watchlist_movies, available_movies):
        """Build movie context from template"""
        template = self.jinja_env.get_template('context.jinja')
        return template.render(
            watchlist_movies=watchlist_movies,
            available_movies=available_movies,
            watchlist_count=len(watchlist_movies),
            available_count=len(available_movies)
        )
    
    def _parse_response(self, response_text):
        """
        Parse Claude's response as JSON
        
        Returns:
            dict with 'message' and 'recommendations' keys
        """
        try:
            parsed = json.loads(response_text)
            return {
                'message': parsed.get('message', response_text),
                'recommendations': parsed.get('recommendations', [])
            }
        except json.JSONDecodeError:
            # Fallback if Claude doesn't return JSON
            print("⚠️ Claude did not return valid JSON, using raw text")
            return {
                'message': response_text,
                'recommendations': []
            }