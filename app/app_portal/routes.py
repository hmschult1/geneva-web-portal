from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.orm import selectinload
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.app_portal import app_portal_bp
from app.app_portal.forms import EditFullEntryForm
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


@app_portal_bp.route("/accounts", methods=["GET", "POST"])
@login_required
def accounts():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if not check_password_hash(
            current_user.password,
            form.current_password.data
        ):
            flash("Incorrect current password.", "danger")
        else:
            current_user.password = generate_password_hash(
                form.new_password.data
            )

            db.session.commit()

            flash(
                "Your password has been updated successfully.",
                "success"
            )

            return redirect(url_for("auth.accounts"))

    return render_template(
        "auth/accounts.html",
        form=form
    )


@app_portal_bp.route("/class-notes")
@login_required
def class_notes():
    entries = (
        AlumniClassNote.query
        .join(AlumniUpdate)
        .order_by(AlumniUpdate.submitted_at.desc())
        .all()
    )

    form = EditFullEntryForm()

    return render_template(
        "app_portal/class-notes.html",
        entries=entries,
        form=form
    )


@app_portal_bp.route("/updates")
@login_required
def updates():
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

    return render_template(
        "app_portal/updates.html",
        entries=entries,
        form=form
    )


@app_portal_bp.route(
    "/class-notes/<int:note_id>/edit",
    methods=["POST"]
)
@login_required
def edit_class_note(note_id):
    form = EditFullEntryForm()

    if form.validate_on_submit():
        note = AlumniClassNote.query.get_or_404(note_id)

        note.apply_edit_form(form)

        db.session.commit()

        flash("Entry updated successfully.", "success")
    else:
        flash(
            "There was an error submitting the form. "
            "Please check the fields.",
            "danger"
        )

    return redirect(url_for("app_portal.class_notes"))


@app_portal_bp.route("/memoriam")
@login_required
def memoriam():
    return render_template("app_portal/memoriam.html")