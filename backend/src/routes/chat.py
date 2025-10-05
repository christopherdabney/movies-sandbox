from database import db
from flask import Blueprint, request, jsonify
from auth import token_required
from models import ChatMessage, Movie
from services import RecommendationsService

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

# Initialize recommendations service
recommendations_service = RecommendationsService()

@chat_bp.route('/message', methods=['POST'])
@token_required
def post(member_id):
    data = request.get_json()
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({'error': 'message is required'}), 400
    
    try:
        # Save user message
        user_chat_message = ChatMessage(
            user_id=member_id,
            role='user',
            content=user_message
        )
        db.session.add(user_chat_message)
        db.session.commit()

        # Get recommendation from ChatService
        result = recommendations_service.get(member_id, user_message)
        
        # Extract movie IDs from recommendations
        movie_ids = [rec['id'] for rec in result.get('recommendations', [])]
        
        # Save assistant response
        assistant_chat_message = ChatMessage(
            user_id=member_id,
            role='assistant',
            content=result['message'],
            recommended_movie_ids=movie_ids if movie_ids else None
        )
        db.session.add(assistant_chat_message)
        db.session.commit()

        return jsonify({
            'message': result['message'],
            'recommendations': result['recommendations']
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/history', methods=['GET'])
@token_required
def get(member_id):
    """Get chat history for the current user"""
    try:
        ChatMessage.expire_all(member_id, with_commit=True)

        messages = ChatMessage.query\
            .filter_by(user_id=member_id)\
            .order_by(ChatMessage.created_at.asc())\
            .all()
        
        # Hydrate messages with full movie data
        result = []
        for msg in messages:
            msg_dict = msg.to_dict()
            
            # If assistant message has movie IDs, fetch full movie data
            if msg.role == 'assistant' and msg.recommended_movie_ids:
                movies = Movie.query.filter(Movie.id.in_(msg.recommended_movie_ids)).all()
                msg_dict['recommendations'] = [m.to_dict() for m in movies]
            else:
                msg_dict['recommendations'] = []
            
            result.append(msg_dict)

        return jsonify({
            'messages': result,
            'count': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/clear', methods=['DELETE'])
@token_required
def delete(member_id):
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