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
        """
        Apply all fields submitted through EditAlumniUpdateEntryForm.

        This method changes the SQLAlchemy objects in memory.
        The route must call db.session.commit() afterward.
        """
        alumnus = self.alumnus

        if not alumnus:
            raise ValueError(
                f"AlumniUpdate {self.id} does not have an associated alumnus."
            )

        # Basic alumnus information
        alumnus.first_name = form.first_name.data or ""
        alumnus.last_name = form.last_name.data or ""
        alumnus.maiden_name = form.maiden_name.data or ""
        alumnus.email = form.email.data or ""
        alumnus.phone = form.phone.data or ""
        alumnus.phone_type = form.phone_type.data or None

        # Related information
        self._apply_geneva_education_edits(form)
        self._apply_address_edits(form)
        self._apply_family_edits(form)
        self._apply_child_edits(form)
        self._apply_employment_edits(form)
        self._apply_additional_education_edits(form)

        # Fields stored directly on AlumniUpdate
        self.update_types = form.update_types.data or []
        self.additional_updates = form.additional_updates.data or ""
        self.volunteer_choices = form.volunteer_choices.data or []
        self.other_volunteer = form.other_volunteer.data or ""

        return self


    def _apply_geneva_education_edits(self, form):
        """
        Add, update, or delete the alumnus's Geneva education record.

        AlumniGenevaEducation stores the selected degree levels and their
        corresponding graduation years in one related record.
        """
        alumnus = self.alumnus

        if not alumnus:
            raise ValueError(
                f"AlumniUpdate {self.id} does not have an associated alumnus."
            )

        selected_degrees = list(form.geneva_degrees.data or [])

        undergrad_year = (
            form.undergrad_year.data or ""
            if "Undergraduate" in selected_degrees
            else ""
        )

        graduate_year = (
            form.graduate_year.data or ""
            if "Graduate" in selected_degrees
            else ""
        )

        online_year = (
            form.online_year.data or ""
            if "Online Degree" in selected_degrees
            else ""
        )

        has_geneva_education_data = any([
            selected_degrees,
            undergrad_year,
            graduate_year,
            online_year,
        ])

        education = (
            alumnus.geneva_educations[0]
            if alumnus.geneva_educations
            else None
        )

        if not education and has_geneva_education_data:
            education = AlumniGenevaEducation()
            alumnus.geneva_educations.append(education)

        if not education:
            return

        # Remove the record entirely when all fields have been cleared.
        if not has_geneva_education_data:
            alumnus.geneva_educations.remove(education)
            return

        education.geneva_degrees = selected_degrees
        education.undergrad_year = undergrad_year
        education.graduate_year = graduate_year
        education.online_year = online_year


    def _apply_address_edits(self, form):
        """
        Update the alumnus's first address record or create one when needed.
        """
        alumnus = self.alumnus

        if not alumnus:
            return

        address_values = {
            "address_line1": form.address_line1.data or "",
            "address_line2": form.address_line2.data or "",
            "city": form.city.data or "",
            "state": form.state.data or "",
            "postal_code": form.postal_code.data or "",
            "country": form.country.data or "",
        }

        has_address_data = any(address_values.values())

        address = (
            alumnus.addresses[0]
            if alumnus.addresses
            else None
        )

        if not address and has_address_data:
            address = AlumniAddress()
            alumnus.addresses.append(address)

        if not address:
            return

        address.address_line1 = address_values["address_line1"]
        address.address_line2 = address_values["address_line2"]
        address.city = address_values["city"]
        address.state = address_values["state"]
        address.postal_code = address_values["postal_code"]
        address.country = address_values["country"]

    def _apply_family_edits(self, form):
        family = self.family_update

        selected_spouse_degrees = set(
            form.spouse_geneva_degrees.data or []
        )

        has_family_data = any([
            form.marital_status.data,
            form.spouse_name.data,
            form.marry_date.data,
            selected_spouse_degrees,
            form.spouse_undergrad_year.data,
            form.spouse_graduate_year.data,
            form.spouse_online_year.data,
        ])

        if not family and has_family_data:
            family = AlumniFamilyUpdate()
            self.family_update = family

        if not family:
            return

        family.marital_status = form.marital_status.data or ""
        family.spouse_name = form.spouse_name.data or ""
        family.marry_date = form.marry_date.data

        family.spouse_geneva_degrees = list(
            selected_spouse_degrees
        )

        family.spouse_undergrad_year = (
            (form.spouse_undergrad_year.data or "")
            if "Undergraduate" in selected_spouse_degrees
            else ""
        )

        family.spouse_graduate_year = (
            (form.spouse_graduate_year.data or "")
            if "Graduate" in selected_spouse_degrees
            else ""
        )

        family.spouse_online_year = (
            (form.spouse_online_year.data or "")
            if "Online Degree" in selected_spouse_degrees
            else ""
        )

    def _apply_child_edits(self, form):
        """
        Update the first child associated with the update or create one.

        Your current form contains only one set of child fields, so this method
        edits the first child record.
        """
        child_values = {
            "first_name": form.child_first_name.data or "",
            "last_name": form.child_last_name.data or "",
            "gender": form.child_gender.data or "",
            "birthday": form.child_birthday.data,
        }

        has_child_data = any([
            child_values["first_name"],
            child_values["last_name"],
            child_values["gender"],
            child_values["birthday"],
        ])

        child = self.children[0] if self.children else None

        if not child and has_child_data:
            child = AlumniChild()
            self.children.append(child)

        if not child:
            return

        child.first_name = child_values["first_name"]
        child.last_name = child_values["last_name"]
        child.gender = child_values["gender"]
        child.birthday = child_values["birthday"]


    def _apply_employment_edits(self, form):
        """
        Update the first employment record or create one.

        The form currently provides one employer, position, and start date.
        """
        employment_values = {
            "employer": form.employer.data or "",
            "position": form.position.data or "",
            "start_date": form.start_date.data,
        }

        has_employment_data = any([
            employment_values["employer"],
            employment_values["position"],
            employment_values["start_date"],
        ])

        employment = (
            self.employment_updates[0]
            if self.employment_updates
            else None
        )

        if not employment and has_employment_data:
            employment = AlumniEmploymentUpdate()
            self.employment_updates.append(employment)

        if not employment:
            return

        employment.employer = employment_values["employer"]
        employment.position = employment_values["position"]
        employment.start_date = employment_values["start_date"]


    def _apply_additional_education_edits(self, form):
        """
        Update the first non-Geneva education record or create one.
        """
        education_values = {
            "institution": form.additional_institution.data or "",
            "degree": form.additional_degree.data or "",
            "graduation_year": form.education_grad_year.data or "",
        }

        has_education_data = any(education_values.values())

        education = (
            self.education_updates[0]
            if self.education_updates
            else None
        )

        if not education and has_education_data:
            education = AlumniEducationUpdate()
            self.education_updates.append(education)

        if not education:
            return

        education.institution = education_values["institution"]
        education.degree = education_values["degree"]
        education.graduation_year = education_values["graduation_year"]


    def to_edit_alumni_update_modal_payload(self):
        """
        Return the AlumniUpdate and its related records as a JSON-safe
        dictionary for the edit modal.
        """
        alumnus = self.alumnus

        if not alumnus:
            return {
                "id": self.id,
            }

        # ---------------------------------------------------------
        # Geneva education
        # ---------------------------------------------------------
        geneva_education = (
            alumnus.geneva_educations[0]
            if alumnus.geneva_educations
            else None
        )

        geneva_degrees = (
            list(geneva_education.geneva_degrees or [])
            if geneva_education
            else []
        )

        # ---------------------------------------------------------
        # Address
        # ---------------------------------------------------------

        address = (
            alumnus.addresses[0]
            if alumnus.addresses
            else None
        )

        # ---------------------------------------------------------
        # Family and spouse
        # ---------------------------------------------------------

        family = self.family_update

        spouse_geneva_degrees = (
            family.spouse_geneva_degrees or []
            if family
            else []
        )

        # ---------------------------------------------------------
        # Child
        # ---------------------------------------------------------

        child = self.children[0] if self.children else None

        # ---------------------------------------------------------
        # Employment
        # ---------------------------------------------------------

        employment = (
            self.employment_updates[0]
            if self.employment_updates
            else None
        )

        # ---------------------------------------------------------
        # Additional education
        # ---------------------------------------------------------

        additional_education = (
            self.education_updates[0]
            if self.education_updates
            else None
        )

        # ---------------------------------------------------------
        # Helper for JSON-safe date values
        # ---------------------------------------------------------

        def format_date(value):
            if not value:
                return ""

            if hasattr(value, "isoformat"):
                return value.isoformat()

            return str(value)

        # ---------------------------------------------------------
        # Complete modal payload
        # ---------------------------------------------------------

        return {
            # Update identifier
            "id": self.id,

            # Basic alumnus information
            "first_name": alumnus.first_name or "",
            "last_name": alumnus.last_name or "",
            "maiden_name": alumnus.maiden_name or "",
            "email": alumnus.email or "",
            "phone": alumnus.phone or "",

            # If phone_type is an enum, .value makes it JSON-safe.
            "phone_type": (
                alumnus.phone_type.value
                if hasattr(alumnus.phone_type, "value")
                else alumnus.phone_type or ""
            ),

            # Alumnus Geneva education
            "geneva_degrees": geneva_degrees,

            "undergrad_year": (
                geneva_education.undergrad_year
                if geneva_education and geneva_education.undergrad_year
                else ""
            ),

            "graduate_year": (
                geneva_education.graduate_year
                if geneva_education and geneva_education.graduate_year
                else ""
            ),

            "online_year": (
                geneva_education.online_year
                if geneva_education and geneva_education.online_year
                else ""
            ),

            # Address
            "address_line1": (
                address.address_line1
                if address and address.address_line1
                else ""
            ),
            "address_line2": (
                address.address_line2
                if address and address.address_line2
                else ""
            ),
            "city": (
                address.city
                if address and address.city
                else ""
            ),
            "state": (
                address.state
                if address and address.state
                else ""
            ),
            "postal_code": (
                address.postal_code
                if address and address.postal_code
                else ""
            ),
            "country": (
                address.country
                if address and address.country
                else ""
            ),

            # Family
            "marital_status": (
                family.marital_status
                if family and family.marital_status
                else ""
            ),

            "spouse_name": (
                family.spouse_name
                if family and family.spouse_name
                else ""
            ),

            "marry_date": (
                format_date(family.marry_date)
                if family
                else ""
            ),

            "spouse_geneva_degrees": spouse_geneva_degrees,

            "spouse_undergrad_year": (
                family.spouse_undergrad_year
                if family and family.spouse_undergrad_year
                else ""
            ),

            "spouse_graduate_year": (
                family.spouse_graduate_year
                if family and family.spouse_graduate_year
                else ""
            ),

            "spouse_online_year": (
                family.spouse_online_year
                if family and family.spouse_online_year
                else ""
            ),

            # Child
            "child_first_name": (
                child.first_name
                if child and child.first_name
                else ""
            ),
            "child_last_name": (
                child.last_name
                if child and child.last_name
                else ""
            ),
            "child_gender": (
                child.gender
                if child and child.gender
                else ""
            ),
            "child_birthday": (
                format_date(child.birthday)
                if child
                else ""
            ),

            # Employment
            "employer": (
                employment.employer
                if employment and employment.employer
                else ""
            ),
            "position": (
                employment.position
                if employment and employment.position
                else ""
            ),
            "start_date": (
                format_date(employment.start_date)
                if employment
                else ""
            ),

            # Additional education
            "additional_institution": (
                additional_education.institution
                if (
                    additional_education
                    and additional_education.institution
                )
                else ""
            ),
            "additional_degree": (
                additional_education.degree
                if (
                    additional_education
                    and additional_education.degree
                )
                else ""
            ),
            "education_grad_year": (
                additional_education.graduation_year
                if (
                    additional_education
                    and additional_education.graduation_year
                )
                else ""
            ),

            # Update information
            "update_types": list(
                self.update_types or []
            ),
            "additional_updates": (
                self.additional_updates or ""
            ),

            # Volunteer information
            "volunteer_choices": list(
                self.volunteer_choices or []
            ),
            "other_volunteer": (
                self.other_volunteer or ""
            ),
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

    alumnus_id = db.Column(
        db.Integer,
        db.ForeignKey("alumni.id"),
        nullable=False,
    )

    geneva_degrees = db.Column(db.JSON, nullable=True)
    undergrad_year = db.Column(db.String(4))
    graduate_year = db.Column(db.String(4))
    online_year = db.Column(db.String(4))

    alumnus = db.relationship(
        "Alumni",
        back_populates="geneva_educations",
    )


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
        """
        Apply edits from the class-note edit modal.

        Geneva education records belong to the alumnus associated
        with this class note's AlumniUpdate.
        """
        update = self.alumni_update
        alumnus = update.alumnus if update else None

        if not update or not alumnus:
            raise ValueError(
                f"Class note {self.id} does not have an associated "
                "AlumniUpdate and Alumni record."
            )

        alumnus.first_name = form.first_name.data or ""
        alumnus.last_name = form.last_name.data or ""
        alumnus.maiden_name = form.maiden_name.data or ""

        update._apply_geneva_education_edits(form)

        self.nameplate = form.nameplate.data or ""
        self.class_note_text = form.class_note_text.data or ""

        if hasattr(form, "existing_image"):
            self.image_filename = (
                form.existing_image.data
                or self.image_filename
                or ""
            )

        return self
    
    def to_edit_class_note_modal_payload(self):
        """
        Return the data required to populate the class-note edit modal.
        """
        update = self.alumni_update
        alumnus = update.alumnus if update else None

        geneva_education = None

        if alumnus and alumnus.geneva_educations:
            geneva_education = alumnus.geneva_educations[0]

        geneva_degrees = (
            list(geneva_education.geneva_degrees or [])
            if geneva_education
            else []
        )

        return {
            "id": self.id,

            "first_name": (
                alumnus.first_name
                if alumnus and alumnus.first_name
                else ""
            ),

            "last_name": (
                alumnus.last_name
                if alumnus and alumnus.last_name
                else ""
            ),

            "maiden_name": (
                alumnus.maiden_name
                if alumnus and alumnus.maiden_name
                else ""
            ),

            "geneva_degrees": geneva_degrees,

            "undergrad_year": (
                geneva_education.undergrad_year
                if geneva_education and geneva_education.undergrad_year
                else ""
            ),

            "graduate_year": (
                geneva_education.graduate_year
                if geneva_education and geneva_education.graduate_year
                else ""
            ),

            "online_year": (
                geneva_education.online_year
                if geneva_education and geneva_education.online_year
                else ""
            ),

            "nameplate": self.nameplate or "",

            "class_note_text": self.class_note_text or "",

            "image_filename": self.image_filename or "",

            "existing_image": self.image_filename or "",

            "published": bool(self.published),
        }