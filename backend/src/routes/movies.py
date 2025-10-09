from flask import Blueprint, request, jsonify
from auth import token_optional
from models import Movie
from models.watchlist import Watchlist
from models.member import Member
from utils.movies import get_allowable_ratings
from sqlalchemy import and_

movies_bp = Blueprint('movies', __name__, url_prefix='/movies')

@movies_bp.route('', methods=['GET'])
@token_optional
def list(member_id=None):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 20, type=int)
    offset = (page - 1) * per_page
    search = request.args.get('search', '', type=str)  # Add this
    genre = request.args.get('genre', '', type=str)

    # Build base query
    query = Movie.query
    
    if search:
        query = query.filter(Movie.title.ilike(f'%{search}%'))
    if genre:
        query = query.filter(Movie.genre == genre)

    # Manual LIMIT/OFFSET with SQLAlchemy
    movies_list = []
    if member_id:
        member = Member.query.get(member_id)
        age = member.calculate_age()
        query = query.filter(Movie.rating.in_(
            get_allowable_ratings(age))
        )

        # Query movies with LEFT JOIN to watchlist
        movies_query = query\
            .outerjoin(Watchlist, and_(
                Watchlist.movie_id == Movie.id,
                Watchlist.member_id == member_id
            ))\
            .add_columns(Watchlist.id.isnot(None).label('in_watchlist'))\
            .limit(per_page)\
            .offset(offset)\
            .all()

        for movie, in_watchlist in movies_query:
            movie_dict = movie.to_dict()
            movie_dict['inWatchlist'] = in_watchlist
            movies_list.append(movie_dict)

        total_count = query.count()
    else:
        movies = query.offset(offset).limit(per_page).all()
        total_count = Movie.query.count()
        movies_list = [movie.to_dict() for movie in movies]

    return jsonify({
        'movies': movies_list,
        'page': page,
        'per_page': per_page,
        'total_count': total_count,
        'total_pages': (total_count + per_page - 1) // per_page
    })

@movies_bp.route('/<int:id>', methods=['GET'])
@token_optional
def get(id, member_id=None):
    if member_id:
        # Query with watchlist data
        result = Movie.query\
            .outerjoin(Watchlist, and_(
                Watchlist.movie_id == Movie.id,
                Watchlist.member_id == member_id
            ))\
            .add_columns(
                Watchlist.id.isnot(None).label('in_watchlist'),
                Watchlist.status
            )\
            .filter(Movie.id == id)\
            .first()
        
        if not result:
            return jsonify({'error': 'Movie not found'}), 404
        
        movie, in_watchlist, status = result
        movie_dict = movie.to_dict()
        movie_dict['inWatchlist'] = in_watchlist
        if status:
            movie_dict['watchlistStatus'] = status.value
        
        return jsonify(movie_dict)
    else:
        # No auth - just return movie
        movie = Movie.query.get(id)
        if not movie:
            return jsonify({'error': 'Movie not found'}), 404
        return jsonify(movie.to_dict())

@movies_bp.route('/genres', methods=['GET'])
def genres():
    genres = Movie.query\
        .with_entities(Movie.genre)\
        .distinct()\
        .order_by(Movie.genre)\
        .all()
    
    return jsonify({
        'genres': [g[0] for g in genres if g[0]]  # Filter out None values
    })