from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.orm import selectinload
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.app_portal import app_portal_bp
from app.app_portal.forms import EditAlumniUpdateEntryForm, EditClassNoteEntryForm
from app.auth.forms import ChangePasswordForm
from app.models import AlumniClassNote, AlumniUpdate


# APP PORTAL ROUTES

@app_portal_bp.route("/")
@login_required
def landing():
    updates = (
        AlumniUpdate.query
        .order_by(AlumniUpdate.submitted_at.desc())
        .all()
    )

    return render_template(
        "app_portal/landing.html",
        updates=updates
    )

# ALUMNI UPDATE ROUTES
@app_portal_bp.route("/updates")
@login_required
def alumni_updates():
    entries = (
        AlumniUpdate.query
        .options(
            selectinload(AlumniUpdate.alumnus),
            selectinload(AlumniUpdate.family_update),
            selectinload(AlumniUpdate.children),
            selectinload(AlumniUpdate.employment_updates),
            selectinload(AlumniUpdate.education_updates),
        )
        .order_by(AlumniUpdate.submitted_at.desc())
        .all()
    )

    form = EditAlumniUpdateEntryForm()

    return render_template(
        "app_portal/updates.html",
        entries=entries,
        form=form
    )
    
@app_portal_bp.route(
    "/alumni-updates/<int:edit_id>/edit",
    methods=["POST"]
)    
    
@login_required
def edit_alumni_updates(edit_id):
    form = EditAlumniUpdateEntryForm()

    if form.validate_on_submit():
        update = AlumniUpdate.query.get_or_404(edit_id)

        update.apply_alumni_update_edit(form)

        db.session.commit()

        flash("Entry updated successfully.", "success")
    else:
        flash(
            "There was an error submitting your edits. "
            "Please check the fields.",
            "danger"
        )

    return redirect(url_for("app_portal.alumni_updates"))    
    
# CLASS NOTES ROUTES
@app_portal_bp.route("/class-notes")
@login_required
def class_notes():
    entries = (
        AlumniClassNote.query
        .join(AlumniUpdate)
        .order_by(AlumniUpdate.submitted_at.desc())
        .all()
    )

    form = EditClassNoteEntryForm()

    return render_template(
        "app_portal/class-notes.html",
        entries=entries,
        form=form
    )

@app_portal_bp.route(
    "/class-notes/<int:edit_id>/edit",
    methods=["POST"]
)

@login_required
def edit_class_note(edit_id):
    form = EditClassNoteEntryForm()

    if form.validate_on_submit():
        note = AlumniClassNote.query.get_or_404(edit_id)

        note.apply_class_note_edit(form)

        db.session.commit()

        flash("Entry updated successfully.", "success")
    else:
        flash(
            "There was an error submitting your edits. "
            "Please check the fields.",
            "danger"
        )

    return redirect(url_for("app_portal.class_notes"))


@app_portal_bp.route("/memoriam")
@login_required
def memoriam():
    return render_template("app_portal/memoriam.html")