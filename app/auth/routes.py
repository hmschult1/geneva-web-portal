from datetime import datetime, timezone

from flask import (
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from app.auth import auth_bp
from app.auth.forms import ChangePasswordForm, LoginForm
from app.auth.models import User
from app.extensions import db

from urllib.parse import urljoin, urlparse


def is_safe_redirect_url(target):
    """
    Only allow redirects to the same host as the current application.
    """

    if not target:
        return False

    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))

    return (
        redirect_url.scheme in {"http", "https"}
        and host_url.netloc == redirect_url.netloc
    )

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("app_portal.landing"))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.strip()

        user = User.query.filter_by(username=username).first()

        credentials_are_valid = (
            user is not None
            and user.is_enabled
            and user.check_password(form.password.data)
        )

        if not credentials_are_valid:
            flash("Invalid username or password.", "danger")
            return render_template(
                "auth/login.html",
                form=form,
            )

        login_user(user, remember=False)
        session.permanent = True

        user.last_login_at = datetime.now(timezone.utc)
        db.session.commit()

        flash("You have logged in successfully.", "success")

        next_page = request.args.get("next")

        if next_page and is_safe_redirect_url(next_page):
            return redirect(next_page)

        return redirect(url_for("app_portal.landing"))

    return render_template(
        "auth/login.html",
        form=form,
    )

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out. Thank you for using the Geneva App Portal!', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route("/session-timeout")
def session_timeout():
    flash(
        "Your session expired due to inactivity. Please sign in again.",
        "warning",
    )
    return redirect(url_for("auth.login"))

@auth_bp.route("/accounts", methods=["GET", "POST"])
@login_required
def accounts():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if not current_user.check_password(
            form.current_password.data
        ):
            flash(
                "Your current password is incorrect.",
                "danger",
            )
            return render_template(
                "auth/accounts.html",
                form=form,
            )

        if current_user.check_password(
            form.new_password.data
        ):
            flash(
                "Your new password must be different from your current password.",
                "danger",
            )
            return render_template(
                "auth/accounts.html",
                form=form,
            )

        current_user.set_password(
            form.new_password.data
        )

        db.session.commit()

        flash(
            "Your password was changed successfully.",
            "success",
        )

        return redirect(
            url_for("auth.accounts")
        )

    return render_template(
        "auth/accounts.html",
        form=form,
    )