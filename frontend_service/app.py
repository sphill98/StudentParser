from flask import Flask
from config.config import Config
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = Config.SECRET_KEY

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.FRONTEND_SERVICE_PORT, debug=True)
