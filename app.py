from flask import Flask
import sqlite3
import os
from flask_jwt_extended import JWTManager
from auth import auth_bp
from fetch import fetch_bp
from sync import sync_bp


app = Flask(__name__)
# Replace with a secure secret!
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

DB_FILE = 'app_database.db'
SCHEMA_FILE = 'schema.sql'


def initialize_database():
    if not os.path.exists(DB_FILE):
        print(
            f"Database {DB_FILE} not found. Creating and initializing schema.")
        conn = sqlite3.connect(DB_FILE)
        with open(SCHEMA_FILE, 'r') as f:
            sql_script = f.read()
        conn.executescript(sql_script)
        conn.commit()
        conn.close()
        print("Database and schema created successfully.")
    else:
        print(f"Database {DB_FILE} already exists. Skipping initialization.")


@app.route('/')
def home():
    return "App is running"


@app.route('/status', methods=['GET'])
def status():
    """
    Health check endpoint.
    If the app is running, it returns a 200 OK status with an empty body.
    Returns:
        _type_: _description_
    """
    return '', 200  # empty body, HTTP 200


app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(fetch_bp, url_prefix='/fetch')
app.register_blueprint(sync_bp, url_prefix='/sync')

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)
