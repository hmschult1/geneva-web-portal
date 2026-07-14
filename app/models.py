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


class AlumniAddress(db.Model):
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
    __tablename__ = "alumni_geneva_educations"

    id = db.Column(db.Integer, primary_key=True)
    alumnus_id = db.Column(db.Integer, db.ForeignKey("alumni.id"), nullable=False)
    degree_level = db.Column(db.String(50))
    degree = db.Column(db.String(150))
    graduation_year = db.Column(db.String(4))

    alumnus = db.relationship("Alumni", back_populates="geneva_educations")


class AlumniFamilyUpdate(db.Model):
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
    __tablename__ = "alumni_employment_updates"

    id = db.Column(db.Integer, primary_key=True)
    alumni_update_id = db.Column(db.Integer, db.ForeignKey("alumni_updates.id"), nullable=False)
    employer = db.Column(db.String(150))
    position = db.Column(db.String(150))
    start_date = db.Column(db.Date)

    alumni_update = db.relationship("AlumniUpdate", back_populates="employment_updates")


class AlumniEducationUpdate(db.Model):
    __tablename__ = "alumni_education_updates"

    id = db.Column(db.Integer, primary_key=True)
    alumni_update_id = db.Column(db.Integer, db.ForeignKey("alumni_updates.id"), nullable=False)
    institution = db.Column(db.String(150))
    degree = db.Column(db.String(150))
    graduation_year = db.Column(db.String(4))

    alumni_update = db.relationship("AlumniUpdate", back_populates="education_updates")


class AlumniClassNote(db.Model):
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

    def apply_edit_form(self, form):
        update = self.alumni_update
        alumnus = update.alumnus if update else None

        if not update or not alumnus:
            return self

        self.viewed = True

        alumnus.first_name = form.first_name.data or ""
        alumnus.last_name = form.last_name.data or ""
        alumnus.maiden_name = form.maiden_name.data or ""
        alumnus.email = form.email.data or ""
        alumnus.phone = form.phone.data or ""
        alumnus.phone_type = form.phone_type.data or None

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

        address = alumnus.addresses[0] if alumnus.addresses else None
        if address is None:
            address = AlumniAddress(alumnus_id=alumnus.id)
            alumnus.addresses.append(address)

        address.address_line1 = form.address_line1.data or ""
        address.address_line2 = form.address_line2.data or ""
        address.city = form.city.data or ""
        address.state = form.state.data or ""
        address.postal_code = form.postal_code.data or ""
        address.country = form.country.data or ""

        family_update = update.family_update
        if family_update is None:
            family_update = AlumniFamilyUpdate(alumni_update_id=update.id)
            update.family_update = family_update

        family_update.marital_status = form.marital_status.data or ""
        family_update.spouse_name = form.spouse_name.data or ""
        family_update.spouse_undergrad_year = form.spouse_grad_year.data or "" if form.spouse_degree_type.data == "Undegraduate" else family_update.spouse_undergrad_year
        family_update.spouse_graduate_year = form.spouse_grad_year.data or "" if form.spouse_degree_type.data == "Graduate" else family_update.spouse_graduate_year
        family_update.spouse_online_year = form.spouse_grad_year.data or "" if form.spouse_degree_type.data == "Online Degree" else family_update.spouse_online_year
        family_update.marry_date = form.marry_date.data

        employment_update = update.employment_updates[0] if update.employment_updates else None
        if employment_update is None:
            employment_update = AlumniEmploymentUpdate(alumni_update_id=update.id)
            update.employment_updates.append(employment_update)

        employment_update.employer = form.employer.data or ""
        employment_update.position = form.position.data or ""

        education_update = update.education_updates[0] if update.education_updates else None
        if education_update is None:
            education_update = AlumniEducationUpdate(alumni_update_id=update.id)
            update.education_updates.append(education_update)

        education_update.institution = form.institution.data or ""
        education_update.graduation_year = form.education_grad_year.data or ""

        child = update.children[0] if update.children else None
        if child is None:
            child = AlumniChild(alumni_update_id=update.id)
            update.children.append(child)

        child.first_name = form.child_first_name.data or ""
        child.last_name = form.child_last_name.data or ""
        child.gender = form.child_gender.data or ""
        child.birthday = form.child_birthday.data

        update.additional_updates = form.additional_updates.data or ""
        update.volunteer_choices = form.volunteer_choices.data or []
        update.other_volunteer = form.other_volunteer.data or ""

        self.nameplate = form.nameplate.data or ""
        self.class_note_text = form.class_note_text.data or ""
        self.image_filename = form.existing_image.data or self.image_filename or ""

        return self

    def to_edit_modal_payload(self):
        update = self.alumni_update
        alumnus = update.alumnus if update else None
        address = alumnus.addresses[0] if alumnus and alumnus.addresses else None
        family_update = update.family_update if update else None
        employment_update = update.employment_updates[0] if update and update.employment_updates else None
        education_update = update.education_updates[0] if update and update.education_updates else None
        child = update.children[0] if update and update.children else None

        return {
            "id": self.id,
            "first_name": alumnus.first_name if alumnus else "",
            "last_name": alumnus.last_name if alumnus else "",
            "maiden_name": alumnus.maiden_name if alumnus else "",
            "email": alumnus.email if alumnus else "",
            "phone": alumnus.phone if alumnus else "",
            "phone_type": alumnus.phone_type.value if alumnus and alumnus.phone_type else "",
            "grad_year": (
                alumnus.geneva_educations[0].graduation_year if alumnus and alumnus.geneva_educations else ""
            ),
            "grad_degree_type": (
                alumnus.geneva_educations[0].degree_level if alumnus and alumnus.geneva_educations else ""
            ),
            "address_line1": address.address_line1 if address else "",
            "address_line2": address.address_line2 if address else "",
            "city": address.city if address else "",
            "state": address.state if address else "",
            "postal_code": address.postal_code if address else "",
            "country": address.country if address else "",
            "marital_status": family_update.marital_status if family_update else "",
            "spouse_name": family_update.spouse_name if family_update else "",
            "spouse_grad_year": family_update.spouse_graduate_year if family_update else "",
            "spouse_degree_type": (
                "Undegraduate"
                if family_update and family_update.spouse_undergrad_year
                else "Graduate"
                if family_update and family_update.spouse_graduate_year
                else "Online Degree"
                if family_update and family_update.spouse_online_year
                else ""
            ),
            "marry_date": family_update.marry_date.strftime("%Y-%m-%d") if family_update and family_update.marry_date else "",
            "employer": employment_update.employer if employment_update else "",
            "position": employment_update.position if employment_update else "",
            "institution": education_update.institution if education_update else "",
            "education_grad_year": education_update.graduation_year if education_update else "",
            "additional_updates": update.additional_updates if update else "",
            "volunteer_choices": update.volunteer_choices or [],
            "other_volunteer": update.other_volunteer if update else "",
            "nameplate": self.nameplate or "",
            "class_note_text": self.class_note_text or "",
            "image_filename": self.image_filename or "",
            "existing_image": self.image_filename or "",
            "child_first_name": child.first_name if child else "",
            "child_last_name": child.last_name if child else "",
            "child_gender": child.gender if child else "",
            "child_birthday": child.birthday.strftime("%Y-%m-%d") if child and child.birthday else "",
        }
