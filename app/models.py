import datetime
import enum

from app import db


# Alumni submission data lives in these models. Staff/admin access is handled
# separately by the auth user model and is not created from or attached to
# each alumni submission.

class PhoneType(enum.Enum):
    MOBILE = "mobile"
    HOME = "home"


class Alumni(db.Model):
    __bind_key__ = "alumni"
    __tablename__ = "alumni"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    maiden_name = db.Column(db.String(100))
    pref_salutation = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    phone_type = db.Column(db.Enum(PhoneType), nullable=True)

    addresses = db.relationship(
        "AlumniAddress",
        back_populates="alumnus",
        cascade="all, delete-orphan",
    )
    geneva_educations = db.relationship(
        "AlumniGenevaEducation",
        back_populates="alumnus",
        cascade="all, delete-orphan",
    )
    updates = db.relationship(
        "AlumniUpdate",
        back_populates="alumnus",
        cascade="all, delete-orphan",
    )


class AlumniUpdate(db.Model):
    __bind_key__ = "alumni"
    __tablename__ = "alumni_updates"

    id = db.Column(db.Integer, primary_key=True)
    alumnus_id = db.Column(db.Integer, db.ForeignKey("alumni.id"), nullable=False)
    submitted_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )
    update_types = db.Column(db.JSON, nullable=True)
    wants_class_note = db.Column(db.Boolean, default=False)
    additional_updates = db.Column(db.Text)
    volunteer_choices = db.Column(db.JSON, nullable=True)
    other_volunteer = db.Column(db.Text)
    viewed = db.Column(db.Boolean, default=False)

    alumnus = db.relationship("Alumni", back_populates="updates")
    family_update = db.relationship(
        "AlumniFamilyUpdate",
        back_populates="alumni_update",
        uselist=False,
        cascade="all, delete-orphan",
    )
    children = db.relationship(
        "AlumniChild",
        back_populates="alumni_update",
        cascade="all, delete-orphan",
    )
    employment_updates = db.relationship(
        "AlumniEmploymentUpdate",
        back_populates="alumni_update",
        cascade="all, delete-orphan",
    )
    education_updates = db.relationship(
        "AlumniEducationUpdate",
        back_populates="alumni_update",
        cascade="all, delete-orphan",
    )
    class_note = db.relationship(
        "AlumniClassNote",
        back_populates="alumni_update",
        uselist=False,
        cascade="all, delete-orphan",
    )
    
    def apply_alumni_update_edit(self, form):
        alumnus = self.alumnus

        if not alumnus:
            return self

        self.viewed = True

        alumnus.first_name = form.first_name.data or ""
        alumnus.last_name = form.last_name.data or ""
        alumnus.maiden_name = form.maiden_name.data or ""

        if alumnus.geneva_educations:
            education = alumnus.geneva_educations[0]
            education.degree_level = form.grad_degree_type.data or ""
            education.graduation_year = form.grad_year.data or ""
        else:
            alumnus.geneva_educations.append(
                AlumniGenevaEducation(
                    degree_level=form.grad_degree_type.data or "",
                    graduation_year=form.grad_year.data or "",
                )
            )

        self.update_types = form.update_types.data or []
        self.additional_updates = form.additional_updates.data or ""
        self.volunteer_choices = form.volunteer_choices.data or []
        self.other_volunteer = form.other_volunteer.data or ""

        return self


    def to_edit_alumni_update_modal_payload(self):
        alumnus = self.alumnus

        return {
            "id": self.id,
            "first_name": alumnus.first_name if alumnus else "",
            "last_name": alumnus.last_name if alumnus else "",
            "maiden_name": alumnus.maiden_name if alumnus else "",
            "grad_year": (
            alumnus.geneva_educations[0].graduation_year
            if alumnus and alumnus.geneva_educations
            else ""
            ),
            "grad_degree_type": (
                alumnus.geneva_educations[0].degree_level
                if alumnus and alumnus.geneva_educations
                else ""
            ),
            "update_types": self.update_types or [],
            "additional_updates": self.additional_updates or "",
            "volunteer_choices": self.volunteer_choices or [],
            "other_volunteer": self.other_volunteer or "",
        }

class AlumniAddress(db.Model):
    __bind_key__ = "alumni"
    __tablename__ = "alumni_addresses"

    id = db.Column(db.Integer, primary_key=True)
    alumnus_id = db.Column(db.Integer, db.ForeignKey("alumni.id"), nullable=False)
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))

    alumnus = db.relationship("Alumni", back_populates="addresses")


class AlumniGenevaEducation(db.Model):
    __bind_key__ = "alumni"
    __tablename__ = "alumni_geneva_educations"

    id = db.Column(db.Integer, primary_key=True)
    alumnus_id = db.Column(db.Integer, db.ForeignKey("alumni.id"), nullable=False)
    degree_level = db.Column(db.String(50))
    graduation_year = db.Column(db.String(4))

    alumnus = db.relationship("Alumni", back_populates="geneva_educations")


class AlumniFamilyUpdate(db.Model):
    __bind_key__ = "alumni"
    __tablename__ = "alumni_family_updates"

    id = db.Column(db.Integer, primary_key=True)
    alumni_update_id = db.Column(
        db.Integer,
        db.ForeignKey("alumni_updates.id"),
        nullable=False,
        unique=True,
    )
    marital_status = db.Column(db.String(20))
    spouse_name = db.Column(db.String(150))
    is_spouse_geneva_grad = db.Column(db.Boolean, default=False)
    spouse_geneva_degrees = db.Column(db.JSON, nullable=True)
    spouse_undergrad_year = db.Column(db.String(4))
    spouse_graduate_year = db.Column(db.String(4))
    spouse_online_year = db.Column(db.String(4))
    marry_date = db.Column(db.Date)

    alumni_update = db.relationship("AlumniUpdate", back_populates="family_update")


class AlumniChild(db.Model):
    __bind_key__ = "alumni"
    __tablename__ = "alumni_children"

    id = db.Column(db.Integer, primary_key=True)
    alumni_update_id = db.Column(db.Integer, db.ForeignKey("alumni_updates.id"), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    birthday = db.Column(db.Date)

    alumni_update = db.relationship("AlumniUpdate", back_populates="children")

    def __repr__(self):
        return f"<AlumniChild {self.first_name} {self.last_name} ({self.gender})>"


class AlumniEmploymentUpdate(db.Model):
    __bind_key__ = "alumni"
    __tablename__ = "alumni_employment_updates"

    id = db.Column(db.Integer, primary_key=True)
    alumni_update_id = db.Column(db.Integer, db.ForeignKey("alumni_updates.id"), nullable=False)
    employer = db.Column(db.String(150))
    position = db.Column(db.String(150))
    start_date = db.Column(db.Date)

    alumni_update = db.relationship("AlumniUpdate", back_populates="employment_updates")


class AlumniEducationUpdate(db.Model):
    __bind_key__ = "alumni"
    __tablename__ = "alumni_education_updates"

    id = db.Column(db.Integer, primary_key=True)
    alumni_update_id = db.Column(db.Integer, db.ForeignKey("alumni_updates.id"), nullable=False)
    institution = db.Column(db.String(150))
    degree = db.Column(db.String(150))
    graduation_year = db.Column(db.String(4))

    alumni_update = db.relationship("AlumniUpdate", back_populates="education_updates")


class AlumniClassNote(db.Model):
    __bind_key__ = "alumni"
    __tablename__ = "alumni_class_notes"

    id = db.Column(db.Integer, primary_key=True)
    alumni_update_id = db.Column(
        db.Integer,
        db.ForeignKey("alumni_updates.id"),
        nullable=False,
        unique=True,
    )
    nameplate = db.Column(db.String(255), default="", nullable=True)
    class_note_text = db.Column(db.Text)
    image_filename = db.Column(db.String(255))
    published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime(timezone=True))

    alumni_update = db.relationship("AlumniUpdate", back_populates="class_note")

    def apply_class_note_edit(self, form):
        update = self.alumni_update
        alumnus = update.alumnus if update else None

        if not update or not alumnus:
            return self

        self.viewed = True

        alumnus.first_name = form.first_name.data or ""
        alumnus.last_name = form.last_name.data or ""
        alumnus.maiden_name = form.maiden_name.data or ""

        if alumnus.geneva_educations:
            education = alumnus.geneva_educations[0]
            education.degree_level = form.grad_degree_type.data or ""
            education.graduation_year = form.grad_year.data or ""
        else:
            alumnus.geneva_educations.append(
                AlumniGenevaEducation(
                    alumnus_id=alumnus.id,
                    degree_level=form.grad_degree_type.data or "",
                    graduation_year=form.grad_year.data or "",
                )
            )

        self.nameplate = form.nameplate.data or ""
        self.class_note_text = form.class_note_text.data or ""
        self.image_filename = form.existing_image.data or self.image_filename or ""

        return self

    def to_edit_class_note_modal_payload(self):
        update = self.alumni_update
        alumnus = update.alumnus if update else None

        return {
            "id": self.id,
            "first_name": alumnus.first_name if alumnus else "",
            "last_name": alumnus.last_name if alumnus else "",
            "grad_year": (
                alumnus.geneva_educations[0].graduation_year if alumnus and alumnus.geneva_educations else ""
            ),
            "grad_degree_type": (
                alumnus.geneva_educations[0].degree_level if alumnus and alumnus.geneva_educations else ""
            ),
            "nameplate": self.nameplate or "",
            "class_note_text": self.class_note_text or "",
            "image_filename": self.image_filename or "",
            "existing_image": self.image_filename or "",
        }
