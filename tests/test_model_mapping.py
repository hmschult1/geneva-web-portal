import datetime
from types import SimpleNamespace

from app.dashboard_forms import get_degree_type_choices
from app.models import (
    Alumni,
    AlumniAddress,
    AlumniChild,
    AlumniClassNote,
    AlumniEducationUpdate,
    AlumniEmploymentUpdate,
    AlumniFamilyUpdate,
    AlumniUpdate,
)


def test_class_note_modal_payload_maps_submission_fields():
    alumnus = Alumni(
        first_name="Jane",
        last_name="Doe",
        maiden_name="Smith",
        pref_salutation="Dr.",
        email="jane@example.com",
        phone="555-1234",
    )
    address = AlumniAddress(
        address_line1="1 Main St",
        address_line2="Apt 2",
        city="Beaver Falls",
        state="PA",
        postal_code="15010",
        country="USA",
    )
    family_update = AlumniFamilyUpdate(
        marital_status="Married",
        spouse_name="John Doe",
        marry_date=datetime.date(2000, 1, 15),
    )
    employment_update = AlumniEmploymentUpdate(
        employer="Geneva College",
        position="Administrator",
    )
    education_update = AlumniEducationUpdate(
        institution="Geneva College",
        degree="BS",
        graduation_year="2000",
    )
    child = AlumniChild(
        first_name="Molly",
        last_name="Doe",
        gender="F",
        birthday=datetime.date(2020, 5, 1),
    )
    update = AlumniUpdate(
        additional_updates="Working on a new project",
        volunteer_choices=["Speak to current students"],
        other_volunteer="Would love to mentor",
    )
    note = AlumniClassNote(
        class_note_text="A wonderful update",
        image_filename="photo.jpg",
        published=True,
    )

    alumnus.addresses = [address]
    update.alumnus = alumnus
    update.family_update = family_update
    update.employment_updates = [employment_update]
    update.education_updates = [education_update]
    update.children = [child]
    note.alumni_update = update

    payload = note.to_edit_modal_payload()

    assert payload["first_name"] == "Jane"
    assert payload["last_name"] == "Doe"
    assert payload["email"] == "jane@example.com"
    assert payload["phone"] == "555-1234"
    assert payload["address_line1"] == "1 Main St"
    assert payload["marital_status"] == "Married"
    assert payload["employer"] == "Geneva College"
    assert payload["institution"] == "Geneva College"
    assert payload["volunteer_choices"] == ["Speak to current students"]
    assert payload["class_note_text"] == "A wonderful update"
    assert payload["image_filename"] == "photo.jpg"


def test_degree_type_choices_are_loaded_from_geneva_education_column(monkeypatch):
    class FakeQueryResult:
        def __init__(self, values):
            self._values = values

        def fetchall(self):
            return [(value,) for value in self._values]

    class FakeSession:
        def execute(self, *args, **kwargs):
            return FakeQueryResult(["undegraduate", "graduate", "online degree", "Other"])

    monkeypatch.setattr("app.dashboard_forms.db.session", FakeSession())

    assert get_degree_type_choices() == [
        ("undegraduate", "undegraduate"),
        ("graduate", "graduate"),
        ("online degree", "online degree"),
    ]


def test_class_note_apply_edit_form_updates_related_models():
    alumnus = Alumni(first_name="Jane", last_name="Doe", email="jane@example.com")
    update = AlumniUpdate(additional_updates="", volunteer_choices=[])
    update.alumnus = alumnus
    note = AlumniClassNote(class_note_text="Old note")
    note.alumni_update = update

    form = SimpleNamespace(
        first_name=SimpleNamespace(data="Janet"),
        last_name=SimpleNamespace(data="Doe"),
        maiden_name=SimpleNamespace(data="Smith"),
        email=SimpleNamespace(data="janet@example.com"),
        phone=SimpleNamespace(data="555-0000"),
        address_line1=SimpleNamespace(data="2 Main St"),
        address_line2=SimpleNamespace(data=""),
        city=SimpleNamespace(data="Beaver Falls"),
        state=SimpleNamespace(data="PA"),
        postal_code=SimpleNamespace(data="15010"),
        country=SimpleNamespace(data="USA"),
        marital_status=SimpleNamespace(data="Married"),
        spouse_name=SimpleNamespace(data="John"),
        marry_date=SimpleNamespace(data=datetime.date(2001, 2, 3)),
        employer=SimpleNamespace(data="Geneva College"),
        position=SimpleNamespace(data="Director"),
        institution=SimpleNamespace(data="Geneva College"),
        additional_updates=SimpleNamespace(data="Updated life details"),
        volunteer_choices=SimpleNamespace(data=["Speak to current students"]),
        other_volunteer=SimpleNamespace(data="Mentoring"),
        child_first_name=SimpleNamespace(data="Molly"),
        child_last_name=SimpleNamespace(data="Doe"),
        child_gender=SimpleNamespace(data="F"),
        child_birthday=SimpleNamespace(data=datetime.date(2020, 4, 1)),
        class_note_text=SimpleNamespace(data="Updated note"),
        existing_image=SimpleNamespace(data="updated.jpg"),
    )

    note.apply_edit_form(form)

    assert alumnus.first_name == "Janet"
    assert alumnus.email == "janet@example.com"
    assert alumnus.addresses[0].address_line1 == "2 Main St"
    assert update.family_update.marital_status == "Married"
    assert update.employment_updates[0].employer == "Geneva College"
    assert update.education_updates[0].institution == "Geneva College"
    assert update.children[0].first_name == "Molly"
    assert update.volunteer_choices == ["Speak to current students"]
    assert note.class_note_text == "Updated note"
    assert note.image_filename == "updated.jpg"
