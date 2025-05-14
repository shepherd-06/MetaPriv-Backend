from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
import sqlite3
import bcrypt
from flask_jwt_extended import verify_jwt_in_request, get_jwt


auth_bp = Blueprint('auth', __name__)

DB_FILE = 'app_database.db'


@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify(msg='Username and password required'), 400

    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT app_id, password FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        app_id, stored_hashed_password = result
        stored_hashed_password = stored_hashed_password.encode('utf-8')
        password_bytes = password.encode('utf-8')

        if bcrypt.checkpw(password_bytes, stored_hashed_password):
            access_token = create_access_token(identity=app_id)
            refresh_token = create_refresh_token(identity=app_id)
            return jsonify(user_id=app_id,
                           access_token=access_token,
                           refresh_token=refresh_token,
                           username=username), 200

        else:
            return jsonify(message='Incorrect password'), 401
    else:
        return jsonify(message='Incorrect Password'), 404


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        user_app_id = get_jwt_identity()
        new_access_token = create_access_token(identity=user_app_id)
        return jsonify(access_token=new_access_token), 200
    except Exception as e:
        return jsonify(message='Failed to refresh token', error=str(e)), 500
