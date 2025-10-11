from flask import Blueprint, request, jsonify
from database import db
from models.chat_message import ChatMessage
from models.watchlist import Watchlist, WatchlistStatus
from models.member import Member
from sqlalchemy.orm import joinedload
from models.movie import Movie
from auth import token_required
from datetime import datetime
from utils.movies import get_allowable_ratings

watchlist_bp = Blueprint('watchlist', __name__, url_prefix='/watchlist')

@watchlist_bp.route('', methods=['POST'])
@token_required
def post(member_id):
    """Add a movie to members's watchlist"""
    data = request.get_json()
    movie_id = data.get('movieId')
    
    if not movie_id:
        return jsonify({'error': 'movieId is required'}), 400
    
    # Check if movie exists
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({'error': 'Movie not found'}), 404
    
    member = Member.query.get(member_id)
    allowed_ratings = get_allowable_ratings(member.calculate_age())
    if not movie.rating in allowed_ratings:
        return jsonify({'error': 'Movie not found'}), 404

    # Check if already in watchlist
    existing = Watchlist.query.filter_by(member_id=member_id, movie_id=movie_id).first()
    if existing:
        return jsonify({'error': 'Movie already in watchlist'}), 409
    
    try:
        # Add movie to watch list
        watchlist_item = Watchlist(member_id=member_id, movie_id=movie_id)
        db.session.add(watchlist_item)
        
        # Complete chat exchange within same transaction
        ChatMessage.complete_exchange(member_id)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Movie added to watchlist',
            'watchlist': watchlist_item.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@watchlist_bp.route('', methods=['GET'])
@token_required
def get(member_id):
    """Get member's watchlist with optional status filter"""
    status_filter = request.args.get('status')
    
    query = Watchlist.query\
        .filter_by(member_id=member_id)\
        .options(joinedload(Watchlist.movie))  # Eager load the movie relationship
    
    # Apply status filter if provided
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    watchlist_items = query.all()
    
    results = []
    for item in watchlist_items:
        result = item.to_dict()
        result['movie'] = item.movie.to_dict()
        results.append(result)
    
    return jsonify({
        'watchlist': results,
        'count': len(results)
    }), 200


@watchlist_bp.route('/<int:movie_id>', methods=['DELETE'])
@token_required
def delete(member_id, movie_id):
    """Remove a movie from member's watchlist"""
    watchlist_item = Watchlist.query.filter_by(
        member_id=member_id,
        movie_id=movie_id
    ).first()
    
    if not watchlist_item:
        return jsonify({'error': 'Movie not in watchlist'}), 404
    
    try:
        # delete move from watch list
        db.session.delete(watchlist_item)
        
        # Complete chat exchange within same transaction
        ChatMessage.complete_exchange(member_id)
        
        db.session.commit()
        
        return jsonify({'message': 'Movie removed from watchlist'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@watchlist_bp.route('/<int:movie_id>', methods=['PATCH'])
@token_required
def update(member_id, movie_id):
    """Update watchlist item status (mark as watched/queued)"""
    data = request.get_json()
    status = data.get('status')
    
    if not status:
        return jsonify({'error': 'status is required'}), 400
    
    # Validate status using enum
    if status not in [s.value for s in WatchlistStatus]:
        return jsonify({'error': f'Invalid status. Must be one of: {[s.value for s in WatchlistStatus]}'}), 400
    
    watchlist_item = Watchlist.query.filter_by(
        member_id=member_id,
        movie_id=movie_id
    ).first()
    
    if not watchlist_item:
        return jsonify({'error': 'Movie not in watchlist'}), 404
    
    # Update status
    watchlist_item.status = status
    
    # Set watched_at timestamp if marking as watched
    if status == WatchlistStatus.WATCHED.value:
        watchlist_item.watched_at = datetime.utcnow()
    else:
        # Clear watched_at if changing back to queued
        watchlist_item.watched_at = None
    
    db.session.commit()
    
    return jsonify({
        'message': 'Watchlist status updated',
        'watchlist': watchlist_item.to_dict()
    }), 200

@watchlist_bp.route('/overview', methods=['GET'])
@token_required
def overview(member_id):
    """
    total = Watchlist.query.filter_by(member_id=member_id).count()

    watched = Watchlist.query.filter_by(member_id=member_id, status=WatchlistFilterValue.WATCHED).count()
    queued = Watchlist.query.filter_by(member_id=member_id, status=WatchlistFilterValue.QUEUED).count()

    items = Watchlist.query.filter_by(member_id=member_id).all()

    total = len(items)
    watched = sum(1 for i in items if i.status == WatchlistFilterValue.WATCHED)
    queued = sum(1 for i in items if i.status == WatchlistFilterValue.QUEUED)
    """
    statuses = db.session.query(Watchlist.status).filter_by(member_id=member_id).all()
    return jsonify({
        'watchlist': {
            'total': len(statuses),
            'watched': sum(1 for (s,) in statuses if s == 'watched'),
            'queued': sum(1 for (s,) in statuses if s == 'queued'),
        },
        'recommendations': []
    }), 200