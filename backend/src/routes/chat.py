from database import db
from flask import Blueprint, request, jsonify
from auth import token_required
from models import Movie, ChatMessage
from models.watchlist import Watchlist
from sqlalchemy.orm import joinedload
from services.chat_service import ChatService

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

# Initialize chat service
chat_service = ChatService()

@chat_bp.route('/message', methods=['POST'])
@token_required
def send_message(member_id):
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
        result = chat_service.get_recommendation(member_id, user_message)
        
        # Save assistant response
        assistant_chat_message = ChatMessage(
            user_id=member_id,
            role='assistant',
            content=result['message']
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