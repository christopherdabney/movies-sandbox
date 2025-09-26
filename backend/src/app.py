import db

from auth import (
    token_required, 
    add_token, 
    remove_token, 
    hash_password, 
    check_password,
)
from db import DuplicateError
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)

# Allow requests from React dev server
CORS(app, origins=['http://localhost:5173'], supports_credentials=True)

@app.route('/member/account', methods=['GET'])
@token_required
def account(member_id):
    record = db.get_user(member_id)
    if record:
        return jsonify({
            'id': record['id'],
            'email': record['email'],
            'firstName': record['first_name'],
            'lastName': record['last_name'],
        })
    return jsonify({'error': 'Member not found'}), 404

@app.route('/member/login', methods=['POST'])
def login():
    data = request.get_json()
    record = db.login(data.get('email'))
    if not record:
        return jsonify({'error': 'Member not found'}), 404
    is_valid = check_password(data.get('password'), record['password_hash'])
    if not is_valid:
        return jsonify({'error': 'Incorrect Login Info'}), 404
    return add_token(
        make_response(jsonify({'message': 'Member logged in'})), 
        record['id']
    )

@app.route('/member/logout', methods=['POST'])
def logout():
    return remove_token(
        make_response(jsonify({'message': 'Logged out successfully'})))

@app.route('/member', methods=['POST'])
def register():
    data = request.get_json()
    # Add validation check of the inputs.
    # Are all keys present?
    # Are datatypes reasonable?
    # Any extreme values to be concerned about?
    try:
        result = db.insert(
            data.get('email'),
            hash_password(data.get('password')),
            data.get('firstName'),
            data.get('lastName'),
        )
        # Update the response object with an auth token as well as 
        # the account data
        return jsonify({'message': 'Member registered'}), 201
    except DuplicateError as e:
        return jsonify({'error': str(e)}), 409

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found or invalid parameter format'}), 404

@app.route('/')
def status():
    return "200 OK"

if __name__ == '__main__':
    app.run(debug=True)
