# config_ex.py
import os

class Config:
    # Service configurations
    FRONTEND_HOST = os.getenv('FRONTEND_HOST', '127.0.0.1')
    FRONTEND_PORT = int(os.getenv('FRONTEND_PORT', YOUR_PORT1))

    PARSING_HOST = os.getenv('PARSING_HOST', '127.0.0.1')
    PARSING_PORT = int(os.getenv('PARSING_PORT', YOUR_PORT2))

    AUTH_HOST = os.getenv('AUTH_HOST', '127.0.0.1')
    AUTH_PORT = int(os.getenv('AUTH_PORT', YOUR_PORT3))

    # Secret key for JWT
    SECRET_KEY = os.getenv('SECRET_KEY', 'YOUR_SECRET_KEY')

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'YOUR_DB_LINK')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = 'uploads'