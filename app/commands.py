import click
from flask.cli import with_appcontext

from app.auth.models import User
from app.extensions import db


@click.command("create-user")
@click.option("--username", prompt="Username")
@click.option("--email", prompt="Email address")
@click.password_option(
    prompt="Password",
    confirmation_prompt=True,
)
@with_appcontext
def create_user_command(username, email, password):
    """Create a new admin login account."""

    username = username.strip()
    email = email.strip().lower()

    existing_user = User.query.filter(
        db.or_(
            User.username == username,
            User.email == email,
        )
    ).first()

    if existing_user:
        raise click.ClickException(
            "A user with that username or email already exists."
        )

    user = User(
        username=username,
        email=email,
        is_enabled=True,
    )

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    click.echo(f"User '{username}' was created successfully.")


@click.command("disable-user")
@click.argument("username")
@with_appcontext
def disable_user_command(username):
    """Disable an existing login account."""

    user = User.query.filter_by(username=username).first()

    if user is None:
        raise click.ClickException("User was not found.")

    user.is_enabled = False
    db.session.commit()

    click.echo(f"User '{username}' was disabled.")


@click.command("enable-user")
@click.argument("username")
@with_appcontext
def enable_user_command(username):
    """Enable an existing login account."""

    user = User.query.filter_by(username=username).first()

    if user is None:
        raise click.ClickException("User was not found.")

    user.is_enabled = True
    db.session.commit()

    click.echo(f"User '{username}' was enabled.")


@click.command("reset-user-password")
@click.argument("username")
@click.password_option(
    prompt="New password",
    confirmation_prompt=True,
)
@with_appcontext
def reset_user_password_command(username, password):
    """Reset the password for an existing account."""

    user = User.query.filter_by(username=username).first()

    if user is None:
        raise click.ClickException("User was not found.")

    user.set_password(password)
    db.session.commit()

    click.echo(f"Password reset for '{username}'.")