from flask import render_template, flash, redirect, url_for
from flask import current_app, flash, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_required
from sqlalchemy.orm import selectinload

from app import db
from app.app_portal import app_portal_bp
from app.app_portal.forms import EditAlumniUpdateEntryForm, EditClassNoteEntryForm
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
    update = AlumniUpdate.query.get_or_404(edit_id)
    form = EditAlumniUpdateEntryForm()

    if not form.validate_on_submit():
        current_app.logger.error(
            "Alumni update validation errors for update %s: %s",
            edit_id,
            form.errors,
        )

        flash(
            f"There was an error submitting your edits: {form.errors}",
            "danger",
        )

        return redirect(url_for("app_portal.alumni_updates"))

    try:
        update.apply_alumni_update_edit(form)
        db.session.commit()

        flash("Entry updated successfully.", "success")

    except SQLAlchemyError:
        db.session.rollback()

        current_app.logger.exception(
            "Database error while updating AlumniUpdate %s.",
            edit_id,
        )

        flash(
            "The entry could not be saved because of a database error.",
            "danger",
        )

    except (AttributeError, ValueError):
        db.session.rollback()

        current_app.logger.exception(
            "Model configuration error while updating AlumniUpdate %s.",
            edit_id,
        )

        flash(
            "The entry could not be saved because a related record "
            "is not configured correctly.",
            "danger",
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
    note = AlumniClassNote.query.get_or_404(edit_id)
    form = EditClassNoteEntryForm()

    if not form.validate_on_submit():
        current_app.logger.error(
            "Alumni update validation errors for update %s: %s",
            edit_id,
            form.errors,
        )

        flash(
            f"There was an error submitting your edits: {form.errors}",
            "danger",
        )

        return redirect(url_for("app_portal.class_notes"))

    try:
        note.apply_class_note_edit(form)
        db.session.commit()

        flash("Entry updated successfully.", "success")

    except SQLAlchemyError:
        db.session.rollback()

        current_app.logger.exception(
            "Database error while updating ClassNote %s.",
            edit_id,
        )

        flash(
            "The entry could not be saved because of a database error.",
            "danger",
        )

    except (AttributeError, ValueError):
        db.session.rollback()

        current_app.logger.exception(
            "Model configuration error while updating ClassNote %s.",
            edit_id,
        )

        flash(
            "The entry could not be saved because a related record "
            "is not configured correctly.",
            "danger",
        )

    return redirect(url_for("app_portal.class_notes"))


@app_portal_bp.route("/memoriam")
@login_required
def memoriam():
    return render_template("app_portal/memoriam.html")