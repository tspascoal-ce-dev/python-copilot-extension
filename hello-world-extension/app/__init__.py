from flask import Flask
from app.auth.oauth import oauth_bp
from app.routes.agent import agent_bp
import logging

def create_app():
    app = Flask(__name__)

    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    
    # Register blueprints
    app.register_blueprint(oauth_bp)
    app.register_blueprint(agent_bp)

    return app