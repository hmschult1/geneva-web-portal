from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.auth.forms import ChangePasswordForm
from app.app_portal.forms import EditFullEntryForm
from app.models import AlumniClassNote, AlumniUpdate
from app import db
from sqlalchemy.orm import selectinload

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# DASHBOARD ROUTES
@dashboard_bp.route('/')
@login_required
def dashboard_home():
    updates = AlumniUpdate.query.order_by(AlumniUpdate.submitted_at.desc()).all()
    return render_template('admin_panel/landing.html', updates=updates)

@dashboard_bp.route('/accounts', methods=['GET', 'POST'])
@login_required
def dashboard_accounts():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if not check_password_hash(current_user.password, form.current_password.data):
            flash('Incorrect current password.', 'danger')
        else:
            current_user.password = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated successfully.', 'success')
            return redirect(url_for('dashboard.dashboard_accounts'))

    return render_template('admin_panel/accounts.html', form=form)

@dashboard_bp.route('/class-notes')
@login_required
def dashboard_AlumniClassNotes():
    entries = (
        AlumniClassNote.query.join(AlumniUpdate)
        .order_by(AlumniUpdate.submitted_at.desc())
        .all()
    )
    form = EditFullEntryForm()
    return render_template('admin_panel/class-notes.html', entries=entries, form=form)


@dashboard_bp.route('/updates')
@login_required
def dashboard_updates():
    entries = (
        AlumniUpdate.query
        .options(
            selectinload(AlumniUpdate.alumnus),
            selectinload(AlumniUpdate.family_update),
            selectinload(AlumniUpdate.children),
            selectinload(AlumniUpdate.employment_updates),
            selectinload(AlumniUpdate.education_updates),
            selectinload(AlumniUpdate.class_note),
        )
        .order_by(AlumniUpdate.submitted_at.desc())
        .all()
    )
    form = EditFullEntryForm()
    return render_template('admin_panel/updates.html', entries=entries, form=form)


@dashboard_bp.route('/class-notes/<int:note_id>/edit', methods=['POST'])
@login_required
def edit_class_note(note_id):
    form = EditFullEntryForm()

    if form.validate_on_submit():
        note = AlumniClassNote.query.get_or_404(note_id)
        note.apply_edit_form(form)
        db.session.commit()
        flash('Entry updated successfully.', 'success')
    else:
        flash('There was an error submitting the form. Please check the fields.', 'danger')

    return redirect(url_for('dashboard.dashboard_AlumniClassNotes'))


@dashboard_bp.route('/memoriam')
@login_required
def dashboard_memoriam():
    return render_template('admin_panel/memoriam.html')