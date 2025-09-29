from flask import Blueprint, request, jsonify
from auth import token_required
from models import Movie

movies_bp = Blueprint('movies', __name__, url_prefix='/movies')

@movies_bp.route('', methods=['GET'])
def get():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 20, type=int)
    offset = (page - 1) * per_page
    
    # Manual LIMIT/OFFSET with SQLAlchemy
    movies = Movie.query.offset(offset).limit(per_page).all()
    total_count = Movie.query.count()
    
    return jsonify({
        'movies': [movie.to_dict() for movie in movies],
        'page': page,
        'per_page': per_page,
        'total_count': total_count,
        'total_pages': (total_count + per_page - 1) // per_page
    })
