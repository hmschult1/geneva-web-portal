from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import ( 
    generate_password_hash, 
    check_password_hash
)

from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    __bind_key__ = "auth"
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False,
        index=True,
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    is_enabled = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    last_login_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    def set_password(self, password):
        """Hash and store a new password."""

        if not password:
            raise ValueError("Password cannot be empty.")

        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Return True when the submitted password is correct."""

        if not password or not self.password_hash:
            return False

        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        """
        Flask-Login uses this property to determine whether the account
        is permitted to log in.
        """
        return self.is_enabled

    def __repr__(self):
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id):
    """
    Reload a user from the ID stored in the Flask session.
    """

    try:
        numeric_user_id = int(user_id)
    except (TypeError, ValueError):
        return None

    return db.session.get(User, numeric_user_id)
