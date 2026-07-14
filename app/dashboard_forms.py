from flask_wtf import FlaskForm
from wtforms import (
    StringField, DateField, TextAreaField,
    SelectMultipleField, SubmitField, TelField, HiddenField, SelectField
)

from app import db
from wtforms.validators import (
    DataRequired, Email, Optional, Length
)
from wtforms.widgets import ListWidget, CheckboxInput
from flask_wtf.file import FileField, FileAllowed


def get_degree_type_choices():
    candidates = [
        ("degree_types", "degree_type"),
        ("degree_types", "name"),
        ("degree_types", "type"),
        ("degree_types", "degree"),
        ("alumni_geneva_educations", "degree_level"),
        ("alumni_geneva_educations", "degree"),
    ]

    for table_name, column_name in candidates:
        try:
            query = db.text(f"SELECT DISTINCT {column_name} FROM {table_name}")
            rows = db.session.execute(query).fetchall()
            choices = [(row[0], row[0]) for row in rows if row and row[0]]
            if choices:
                return choices
        except Exception:
            continue

    return []


class EditFullEntryForm(FlaskForm):
    # Contact / personal
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    maiden_name = StringField('Maiden Name', validators=[Optional()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = TelField('Phone Number', validators=[Optional()])
    phone_type = SelectField('Phone Type', choices=[('mobile', 'Mobile'), ('home', 'Home')], validators=[Optional()])
    grad_year = StringField('Geneva Grad Year', validators=[Optional()])
    grad_degree_type = SelectField('Geneva Degree Type', choices=get_degree_type_choices, validators=[Optional()])

    # Address
    address_line1 = StringField('Street Address (Line 1)', validators=[Optional()])
    address_line2 = StringField('Street Address (Line 2)', validators=[Optional()])
    city = StringField('City', validators=[Optional()])
    state = StringField('State / Region', validators=[Optional()])
    postal_code = StringField('Postal / ZIP Code', validators=[Optional()])
    country = StringField('Country', validators=[Optional()])

    # Family
    marital_status = StringField('Marital Status', validators=[Optional()])
    spouse_name = StringField("Spouse's Name", validators=[Optional()])
    spouse_grad_year = StringField('Spouse GenevaGrad Year', validators=[Optional()])
    spouse_degree_type = SelectField('Spouse Geneva Degree Type', choices=get_degree_type_choices, validators=[Optional()])
    marry_date = DateField('Marriage Date', validators=[Optional()])

    # Child
    child_first_name = StringField('Child First Name', validators=[Optional()])
    child_last_name = StringField('Child Last Name', validators=[Optional()])
    child_gender = StringField('Child Gender', validators=[Optional()])
    child_birthday = DateField('Child Birthday', validators=[Optional()])

    # Employment
    employer = StringField('Employer', validators=[Optional()])
    position = StringField('Position', validators=[Optional()])
    start_date = DateField('Start Date', validators=[Optional()])
    
    # Additional Education
    additional_institution = StringField('Additional Education: Institution', validators=[Optional()])
    additional_degree = StringField('Additional Education: Degree Earned', validators=[Optional()])
    education_grad_year = StringField('Additional Education: Grad Year', validators=[Optional()])
    
    # Life Achievements / Updates
    additional_updates = TextAreaField("Life Achievements", validators=[Optional()])

    # Volunteer
    volunteer_choices = SelectMultipleField(
        "Volunteer Opportunities",
        choices=[
            ('Help with admissions in my area', "Help with admissions in my area"),
            ('Speak to current students', "Speak to current students"),
            ('Serve on my class reunion committee', "Serve on my class reunion committee"),
            ('Host an alumni event', "Host an alumni event"),
            ('Other', "Other"),
        ],
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=True),
        validators=[Optional()]
    )
    other_volunteer = TextAreaField('Other Volunteer Ideas', validators=[Optional()])

    # Class note
    nameplate = StringField('Nameplate', validators=[Optional()])
    class_note_text = TextAreaField('Class Note', validators=[Optional(), Length(max=300)])
    image = FileField('Image', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')])
    existing_image = HiddenField()

    submit = SubmitField('Save')
