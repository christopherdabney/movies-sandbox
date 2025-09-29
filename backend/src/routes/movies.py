from flask import Blueprint, request, jsonify
from auth import token_optional
from models import Movie
from models.watchlist import Watchlist
from sqlalchemy import and_

movies_bp = Blueprint('movies', __name__, url_prefix='/movies')

@movies_bp.route('', methods=['GET'])
@token_optional
def get(member_id=None):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 20, type=int)
    offset = (page - 1) * per_page
    
    # Manual LIMIT/OFFSET with SQLAlchemy
    movies_list = []
    if member_id:
        # Query movies with LEFT JOIN to watchlist
        movies_query = Movie.query\
            .outerjoin(Watchlist, and_(
                Watchlist.movie_id == Movie.id,
                Watchlist.user_id == member_id
            ))\
            .add_columns(Watchlist.id.isnot(None).label('in_watchlist'))\
            .limit(per_page)\
            .offset(offset)\
            .all()

        for movie, in_watchlist in movies_query:
            movie_dict = movie.to_dict()
            movie_dict['inWatchlist'] = in_watchlist
            movies_list.append(movie_dict)

        total_count = Movie.query.count()
    else:
        movies = Movie.query.offset(offset).limit(per_page).all()
        total_count = Movie.query.count()
        movies_list = [movie.to_dict() for movie in movies]

    return jsonify({
        'movies': movies_list,
        'page': page,
        'per_page': per_page,
        'total_count': total_count,
        'total_pages': (total_count + per_page - 1) // per_page
    })
