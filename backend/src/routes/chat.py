from database import db
from flask import Blueprint, request, jsonify
from auth import token_required
from models import ChatMessage, Movie, Member
from services import RecommendationsService, RecommendationTrigger

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

ROLE_USER = 'user'  # move this to ChatMessage or elsewhere?

@chat_bp.route('/message', methods=['POST'])
@token_required
def post(member_id):
    data = request.get_json()
    message = data.get('message')
    
    if not message:
        return jsonify({'error': 'message is required'}), 400
    
    try:
        # Pre-flight cost check
        member = Member.query.get(member_id)
        if not member.has_discussion_power():
            return jsonify({
                'error': 'Insufficient discussion power',
                'remaining': member.remaining_discussion_power(),
            }), 429

        # Save member message
        chat_message = ChatMessage(member_id=member_id, role=ROLE_USER, content=message)
        db.session.add(chat_message)

        # Get recommendation from ChatService
        rs = RecommendationsService(member_id)
        result = rs.get(trigger=RecommendationTrigger.CHATBOT_MESSAGE, params={'message': message})
        serialized_movies = Movie.hydrate(result.get('recommendations', []))

        # Extract movie IDs from recommendations & Save assistant response
        movie_ids = [rec['id'] for rec in result.get('recommendations', [])]
        assistant_chat_message = ChatMessage(
            member_id=member_id,
            role='assistant',
            content=result['message'],
            recommended_movie_ids=movie_ids if movie_ids else None
        )
        db.session.add(assistant_chat_message)
        actual_cost = rs.claude_client.get_usage_cost()
        member.agent_usage = float(member.agent_usage) + actual_cost
        db.session.commit()

        return jsonify({
            'message': result['message'],
            'recommendations': serialized_movies,
            'power': member.discussion_power(),
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/history', methods=['GET'])
@token_required
def get(member_id):
    """Get chat history for the current member"""
    try:
        # checks whether older messages should be expired before querying chat
        ChatMessage.expire_all(member_id, with_commit=True)
        messages = ChatMessage.query\
            .filter_by(member_id=member_id)\
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
        member = Member.query.get(member_id)
        return jsonify({
            'messages': result,
            'count': len(result),
            'power': member.discussion_power(),
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/clear', methods=['DELETE'])
@token_required
def delete(member_id):
    """Delete all chat messages for the current member"""
    try:
        from flask import current_app
        ChatMessage.query.filter_by(member_id=member_id).delete()
        current_app.cache_manager.clear_chat_context(member_id)
        db.session.commit()
        
        return jsonify({
            'message': 'Chat history cleared'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500