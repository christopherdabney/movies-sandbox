import os
from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.exc import IntegrityError
from auth import token_required, add_token, remove_token, hash_password, check_password
from database import db
from models import Member
from datetime import date
from utils.movies import get_rating, AGE_UNLOCK_ALL
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

membership_bp = Blueprint('membership', __name__, url_prefix='/member')

@membership_bp.route('', methods=['GET'])
@token_required
def get(member_id):
    member = Member.query.get(member_id)
    if member:
        member_dict = member.to_dict()
        age = member.age()
        member_dict['rating'] = get_rating(age) if age < AGE_UNLOCK_ALL else 'ALL'
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

        # After user is created in DB
        message = Mail(
            from_email='noreply@dabneystudios.com',
            to_emails=data.get('email'),
            subject='Welcome to our Movie Recommendations App!',
            html_content='Thanks for joining us!'
        )

        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(f"Email sent: {response.status_code}")
        except Exception as e:
            print(f"Error sending email: {e}")

        return add_token(
            make_response(jsonify({'message': 'Member registered'})), 
            new_member.id
        )
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Duplicate Member record attempted'}), 409