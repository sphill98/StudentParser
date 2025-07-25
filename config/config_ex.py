# config_ex.py
import os

class Config:
    PARSING_SERVICE_PORT = 'PORT1'
    FRONTEND_SERVICE_PORT = 'PORT2'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'YOUR_SECRET_KEY'
    UPLOAD_FOLDER = 'uploads'