

from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.exc import IntegrityError
from auth import (
    token_required, 
    add_token, 
    remove_token, 
    hash_password, 
    check_password,
    send_verification_email,
)
from database import db
from models import Member
from datetime import date, datetime
from utils.movies import get_rating, AGE_UNLOCK_ALL


membership_bp = Blueprint('membership', __name__, url_prefix='/member')

@membership_bp.route('', methods=['GET'])
@token_required
def get(member_id):
    member = Member.query.get(member_id)
    if member:
        member_dict = member.to_dict()
        age = member.age()
        member_dict['rating'] = get_rating(age) if age < AGE_UNLOCK_ALL else 'ALL'
        print(member_dict)
        return jsonify(member_dict)
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
def post():
    data = request.get_json()
    # Parse date_of_birth from ISO format string (YYYY-MM-DD)
    date_of_birth = date.fromisoformat(data.get('dateOfBirth'))

    try:
        # Create new member using SQLAlchemy
        member = Member(
            email=data.get('email'),
            password_hash=hash_password(data.get('password')),
            first_name=data.get('firstName'),
            last_name=data.get('lastName'),
            date_of_birth=date_of_birth,
        )

        send_verification_email(member)

        # Add and commit to database
        db.session.add(member)
        db.session.commit()

        return add_token(
            make_response(jsonify({'message': 'Member registered'})), 
            member.id
        )
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Duplicate Member record attempted'}), 409

@membership_bp.route('/resend-verification', methods=['POST'])
@token_required
def resend_verification(member_id):
    member = Member.query.get(member_id)
    if member:
        # Generate new token, send email
        send_verification_email(member)
        db.session.commit()
        return jsonify({'message': 'Verification link resent'})
    return jsonify({'error': 'Member not found'}), 404

@membership_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    member = Member.query.filter_by(verification_token=token).first()

    if not member:
        return jsonify({'error': 'Invalid verification token'}), 400

    # Check if token expired
    if member.token_expires_at < datetime.utcnow():
        return jsonify({'error': 'Verification token has expired'}), 400

    # Check if already verified
    if member.email_verified:
        return jsonify({'message': 'Email already verified'}), 200

    # Mark as verified
    member.email_verified = True
    member.verification_token = None
    member.token_expires_at = None

    db.session.commit()
    return jsonify({'message': 'Email verified successfully'}), 200