"""Application factory and extension initialization."""

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(override=True)

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from config import Config

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    from app.auth_models import User

    return User(int(user_id))


def create_app(config_class=Config):
    """Create and configure the Flask application."""

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)

    # Import models so Flask-Migrate can discover them
    from app import auth_models

    # Register blueprints
    from app.auth_routes import auth_bp
    from app.dashboard_routes import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    return app