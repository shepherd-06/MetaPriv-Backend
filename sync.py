from flask import Blueprint, request, jsonify
import sqlite3


sync_bp = Blueprint('sync', __name__)

DB_FILE = 'app_database.db'

"""
We use this file to synch the app database with the server database.
"""


@sync_bp.route('/user', methods=['POST'])
def sync_user():
    data = request.get_json()
    required_fields = ['id', 'username', 'password',
                       'created_at', 'updated_at', 'last_login']

    # Check all required fields are present
    if not all(field in data for field in required_fields):
        return jsonify(message='Missing required user fields'), 400

    user_id = data['id']
    username = data['username']
    password = data['password']  # Already hashed, no bcrypt work here
    created_at = data['created_at']
    updated_at = data['updated_at']
    last_login = data['last_login']

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (id, username, password, created_at, updated_at, last_login)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, password, created_at, updated_at, last_login))
        conn.commit()
        conn.close()
        return jsonify(message='User synced successfully'), 201
    except sqlite3.IntegrityError as e:
        return jsonify(message='Failed to sync user: integrity error', error=str(e)), 409
    except Exception as e:
        return jsonify(message='Failed to sync user: server error', error=str(e)), 500


@sync_bp.route('/videos', methods=['POST'])
def sync_videos():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify(message='Request body must be a list of video objects'), 400

    inserted_app_ids = []

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        for video in data:
            required_fields = ['app_id', 'post_URL', 'page_URL', 'keyword', 'user_id',
                               'liked', 'time', 'screenshot_name', 'watched_at']

            if not all(field in video for field in required_fields):
                continue  # Skip if missing fields

            try:
                cursor.execute('''
                    INSERT INTO videos (app_id, post_URL, page_URL, keyword, user_id, liked, time, screenshot_name, watched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    video['app_id'],
                    video['post_URL'],
                    video['page_URL'],
                    video['keyword'],
                    video['user_id'],
                    int(video['liked']),  # Ensure boolean is stored as integer
                    video['time'],
                    video['screenshot_name'],
                    video['watched_at']
                ))
                inserted_app_ids.append(video['app_id'])
            except sqlite3.IntegrityError:
                continue  # Skip duplicates or integrity errors

        conn.commit()
        conn.close()

        return jsonify(message='Videos synced successfully', inserted_app_ids=inserted_app_ids), 201

    except Exception as e:
        return jsonify(message='Failed to sync videos: server error', error=str(e)), 500


@sync_bp.route('/keywords', methods=['POST'])
def sync_keywords():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify(message='Request body must be a list of keyword objects'), 400

    inserted_app_ids = []

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        for keyword in data:
            required_fields = ['app_id', 'user_id',
                               'text', 'created_at', 'is_active']

            if not all(field in keyword for field in required_fields):
                continue  # Skip if missing fields

            try:
                cursor.execute('''
                    INSERT INTO keywords (app_id, user_id, text, created_at, is_active)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    keyword['app_id'],
                    keyword['user_id'],
                    keyword['text'],
                    keyword['created_at'],
                    # Ensure boolean is stored as integer (0/1)
                    int(keyword['is_active'])
                ))
                inserted_app_ids.append(keyword['app_id'])
            except sqlite3.IntegrityError:
                continue  # Skip duplicates or integrity errors

        conn.commit()
        conn.close()

        return jsonify(message='Keywords synced successfully', inserted_app_ids=inserted_app_ids), 201

    except Exception as e:
        return jsonify(message='Failed to sync keywords: server error', error=str(e)), 500


@sync_bp.route('/pages', methods=['POST'])
def sync_pages():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify(message='Request body must be a list of page objects'), 400

    inserted_app_ids = []

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        for page in data:
            required_fields = ['app_id', 'keyword_id',
                               'page_url', 'is_liked', 'created_at', 'updated_at']

            if not all(field in page for field in required_fields):
                continue  # Skip if missing fields

            try:
                cursor.execute('''
                    INSERT INTO pages (app_id, keyword_id, page_url, is_liked, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    page['app_id'],
                    page['keyword_id'],
                    page['page_url'],
                    # Ensure boolean is stored as integer (0/1)
                    int(page['is_liked']),
                    page['created_at'],
                    page['updated_at']
                ))
                inserted_app_ids.append(page['app_id'])
            except sqlite3.IntegrityError:
                continue  # Skip duplicates or integrity errors

        conn.commit()
        conn.close()

        return jsonify(message='Pages synced successfully', inserted_app_ids=inserted_app_ids), 201

    except Exception as e:
        return jsonify(message='Failed to sync pages: server error', error=str(e)), 500
