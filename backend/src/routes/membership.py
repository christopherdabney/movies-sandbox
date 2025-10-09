from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.exc import IntegrityError
from auth import token_required, add_token, remove_token, hash_password, check_password
from database import db
from models import Member
from datetime import date

membership_bp = Blueprint('membership', __name__, url_prefix='/member')

@membership_bp.route('', methods=['GET'])
@token_required
def account(member_id):
    print('account endpoint called with', member_id)
    member = Member.query.get(member_id)
    if member:
        return jsonify(member.to_dict())
    return jsonify({'error': 'Member not found'}), 404

@membership_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    member = Member.query.filter_by(email=data.get('email')).first()
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    
    is_valid = check_password(data.get('password'), member.password_hash)
    if not is_valid:
        return jsonify({'error': 'Incorrect Login Info'}), 404
    
    return add_token(
        make_response(jsonify({'message': 'Member logged in'})), 
        member.id
    )

@membership_bp.route('/logout', methods=['POST'])
def logout():
    return remove_token(
        make_response(jsonify({'message': 'Logged out successfully'})))

@membership_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    # Parse date_of_birth from ISO format string (YYYY-MM-DD)
    date_of_birth = date.fromisoformat(data.get('dateOfBirth'))

    try:
        # Create new member using SQLAlchemy
        new_member = Member(
            email=data.get('email'),
            password_hash=hash_password(data.get('password')),
            first_name=data.get('firstName'),
            last_name=data.get('lastName'),
            date_of_birth=date_of_birth,
        )
        
        # Add and commit to database
        db.session.add(new_member)
        db.session.commit()
        
        return add_token(
            make_response(jsonify({'message': 'Member registered'})), 
            new_member.id
        )
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Duplicate Member record attempted'}), 409