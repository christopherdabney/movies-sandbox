from flask import Blueprint, request, jsonify
from database import db
from models.watchlist import Watchlist, WatchlistStatus
from models.movie import Movie
from auth import token_required
from datetime import datetime

watchlist_bp = Blueprint('watchlist', __name__, url_prefix='/watchlist')

@watchlist_bp.route('', methods=['POST'])
@token_required
def post(member_id):
    """Add a movie to user's watchlist"""
    data = request.get_json()
    movie_id = data.get('movieId')
    
    if not movie_id:
        return jsonify({'error': 'movieId is required'}), 400
    
    # Check if movie exists
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({'error': 'Movie not found'}), 404
    
    # Check if already in watchlist
    existing = Watchlist.query.filter_by(
        user_id=member_id,
        movie_id=movie_id
    ).first()
    
    if existing:
        return jsonify({'error': 'Movie already in watchlist'}), 409
    
    # Add to watchlist
    watchlist_item = Watchlist(
        user_id=member_id,
        movie_id=movie_id
    )
    
    db.session.add(watchlist_item)
    db.session.commit()
    
    return jsonify({
        'message': 'Movie added to watchlist',
        'watchlist': watchlist_item.to_dict()
    }), 201


@watchlist_bp.route('', methods=['GET'])
@token_required
def get(member_id):
    """Get user's watchlist with optional status filter"""
    status_filter = request.args.get('status')  # Optional: ?status=queued or ?status=watched
    
    query = Watchlist.query.filter_by(user_id=member_id)
    
    # Apply status filter if provided
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    watchlist_items = query.all()
    
    # Get movie details for each watchlist item
    results = []
    for item in watchlist_items:
        movie = Movie.query.get(item.movie_id)
        if movie:
            result = item.to_dict()
            result['movie'] = movie.to_dict()
            results.append(result)
    
    return jsonify({
        'watchlist': results,
        'count': len(results)
    }), 200

@watchlist_bp.route('/<int:movie_id>', methods=['DELETE'])
@token_required
def delete(member_id, movie_id):
    """Remove a movie from user's watchlist"""
    watchlist_item = Watchlist.query.filter_by(
        user_id=member_id,
        movie_id=movie_id
    ).first()
    
    if not watchlist_item:
        return jsonify({'error': 'Movie not in watchlist'}), 404
    
    db.session.delete(watchlist_item)
    db.session.commit()
    
    return jsonify({
        'message': 'Movie removed from watchlist',
        'movieId': movie_id
    }), 200

@watchlist_bp.route('/<int:movie_id>', methods=['PUT'])
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
        user_id=member_id,
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