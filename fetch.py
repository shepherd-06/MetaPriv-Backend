from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import sqlite3


fetch_bp = Blueprint('fetch', __name__)

DB_FILE = 'app_database.db'


@fetch_bp.route('/active', methods=['GET'])
@jwt_required()
def fetch_active_pages():
    user_app_id = get_jwt_identity()

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # this SQL is not correct.
        cursor.execute('''
            SELECT p.page_url
            FROM pages p
            JOIN keywords k ON p.keyword_id = k.app_id AND p.is_liked = 1
            WHERE k.user_id = ? AND k.is_active = 1 
        ''', (user_app_id,))
        rows = cursor.fetchall()
        conn.close()
        page_urls = [row[0] for row in rows]

        return jsonify(page_urls=page_urls), 200

    except Exception as e:
        return jsonify(message='Failed to fetch active pages', error=str(e)), 500
