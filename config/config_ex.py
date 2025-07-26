# config_ex.py
import os

class Config:
    PARSING_SERVICE_PORT = 'PARSING_SERVICE_PORT'
    FRONTEND_SERVICE_PORT = 'FRONTEND_SERVICE_PORT'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'YOUR_SECRET_KEY'
    UPLOAD_FOLDER = 'uploads'