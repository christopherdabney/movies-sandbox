import os

from database import db

from flask import Blueprint, request, jsonify
from anthropic import Anthropic
from auth import token_required
from models import Movie, ChatMessage
from models.watchlist import Watchlist
from sqlalchemy.orm import joinedload
from prompts import SYSTEM_PROMPT, build_movie_context
from utils.movie_filter import extract_filters, get_filtered_movies

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

# Initialize Anthropic client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@chat_bp.route('/message', methods=['POST'])
@token_required
def send_message(member_id):
    data = request.get_json()
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({'error': 'message is required'}), 400
    
    try:
        # Save user message to database
        user_chat_message = ChatMessage(
            user_id=member_id,
            role='user',
            content=user_message
        )
        db.session.add(user_chat_message)
        db.session.commit()

        # Get user's watchlist
        watchlist_items = Watchlist.query\
            .filter_by(user_id=member_id)\
            .options(joinedload(Watchlist.movie))\
            .all()
        
        watchlist_movies = [
            f"{item.movie.title} ({item.movie.release_year}) - {item.movie.genre} - {item.status}"
            for item in watchlist_items
        ]

        # available_movies = Movie.query.limit(100).all()
        
        # Extract filters from user message
        filters = extract_filters(user_message)

        # DEBUG: Print what filters were detected
        print(f"🔍 Filters detected: {filters}")
        print(f"📊 Fetching movies with filters: genres={filters['genres']}, decades={filters['decades']}")
        
        # Get filtered movies (or all if no filters detected)
        if filters['genres'] or filters['decades']:
            available_movies = get_filtered_movies(filters, limit=100)
            filter_note = f" (filtered by: {', '.join(filters['genres']) if filters['genres'] else ''} {filters['decades'] if filters['decades'] else ''})"
        else:
            available_movies = Movie.query.limit(100).all()
            filter_note = ""

        print('filter_node')
        print(filter_note)

        # Get a sample of available movies (limit to 100)
        
        available_list = [
            f"{m.title} ({m.release_year}) - {m.genre}"
            for m in available_movies
        ]
        
        # Build context using helper function
        context = build_movie_context(watchlist_movies, available_list)
        
        # Send a message to Claude API with movie context
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"{context}\n\nUser question: {user_message}"}
            ]
        )
        
        assistant_message = response.content[0].text
        
        # Save assistant response to database
        assistant_chat_message = ChatMessage(
            user_id=member_id,
            role='assistant',
            content=assistant_message
        )
        db.session.add(assistant_chat_message)
        db.session.commit()

        return jsonify({
            'message': assistant_message
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/history', methods=['GET'])
@token_required
def get_history(member_id):
    """Get chat history for the current user"""
    try:
        messages = ChatMessage.query\
            .filter_by(user_id=member_id)\
            .order_by(ChatMessage.created_at.asc())\
            .all()
        
        return jsonify({
            'messages': [msg.to_dict() for msg in messages],
            'count': len(messages)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/clear', methods=['DELETE'])
@token_required
def clear_history(member_id):
    """Delete all chat messages for the current user"""
    try:
        ChatMessage.query.filter_by(user_id=member_id).delete()
        db.session.commit()
        
        return jsonify({
            'message': 'Chat history cleared'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500