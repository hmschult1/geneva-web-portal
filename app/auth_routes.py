import os

from flask import Blueprint, render_template, redirect, flash, url_for, session
from flask_login import login_user, logout_user, login_required

from app.auth_forms import LoginForm


class DummyUser:
    id = 0
    is_authenticated = True
    is_active = True
    is_anonymous = False

    def get_id(self):
        return str(self.id)


DUMMY_STAFF_USER = {
    "email": os.environ.get("DUMMY_STAFF_EMAIL", "staff@example.com"),
    "password": os.environ.get("DUMMY_STAFF_PASSWORD", "changeme123"),
}

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        if email == DUMMY_STAFF_USER["email"] and password == DUMMY_STAFF_USER["password"]:
            dummy_user = DummyUser()
            login_user(dummy_user, remember=False)
            return redirect(url_for('dashboard.dashboard_home'))

        flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out. Thank you for using the Geneva Web Portal!', 'info')
    return redirect(url_for('auth.login'))