import logging
from flask import Flask, request
from config.config import Config
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log')

def create_app():
    app = Flask(__name__)
    app.secret_key = Config.SECRET_KEY

    @app.before_request
    def log_request_info():
        logging.info(f"IP: {request.remote_addr}, Path: {request.path}, Method: {request.method}")

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host=Config.FRONTEND_HOST, port=Config.FRONTEND_PORT, debug=True)
