import bcrypt
import db

from db import DuplicateError
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Allow requests from React dev server
CORS(app, origins=['http://localhost:5173'])

@app.route('/member/<int:id>', methods=['GET'])
def get(id):
    record = db.get_user(id)
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
    is_valid = bcrypt.checkpw(data.get('password').encode('utf-8'), record['password_hash'])
    if not is_valid:
        return jsonify({'error': 'Incorrect Login Info'}), 404
    return jsonify({
        'id': record['id'],
        'email': record['email'],
        'firstName': record['first_name'],
        'lastName': record['last_name'],
    })

@app.route('/member', methods=['POST'])
def register():
    data = request.get_json()
    # Add validation check of the inputs.
    # Are all keys present?
    # Are datatypes reasonable?
    # Any extreme values to be concerned about?
    try:
        db.insert(
            data.get('email'),
            bcrypt.hashpw(data.get('password').encode('utf-8'), bcrypt.gensalt()),
            data.get('firstName'),
            data.get('lastName'),
        )
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
