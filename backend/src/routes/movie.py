from flask import Blueprint, request, jsonify
from auth import token_required
import db

movie_bp = Blueprint('movie', __name__, url_prefix='/movie')

@movie_bp.route('', methods=['GET'])
def get():
    pass