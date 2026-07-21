from flask import Flask

from config import Config
from app.extensions import (
    csrf,
    db,
    login_manager,
)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    # Flask-Login configuration
    login_manager.login_view = "auth.login"
    login_manager.login_message = (
        "Please log in to access the Geneva App Portal."
    )
    login_manager.login_message_category = "info"
    login_manager.session_protection = "strong"

    # Import models so SQLAlchemy knows about every table.
    #
    # Alumni models use:
    #     __bind_key__ = "alumni"
    #
    # User uses:
    #     __bind_key__ = "auth"
    from app.models import (
        Alumni,
        AlumniUpdate,
        AlumniClassNote,
    )
    from app.auth.models import User

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.app_portal.routes import app_portal_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(app_portal_bp)

    # Register manual user-management commands
    from app.commands import (
        create_user_command,
        disable_user_command,
        enable_user_command,
        reset_user_password_command,
    )

    app.cli.add_command(create_user_command)
    app.cli.add_command(disable_user_command)
    app.cli.add_command(enable_user_command)
    app.cli.add_command(reset_user_password_command)

    return app