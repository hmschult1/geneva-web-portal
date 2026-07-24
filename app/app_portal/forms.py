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


GENEVA_DEGREE_CHOICES = [
    ("Undergraduate", "Undergraduate"),
    ("Graduate", "Graduate"),
    ("Online Degree", "Online Degree"),
]

class EditClassNoteEntryForm(FlaskForm):
    # Contact / personal
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    maiden_name = StringField('Maiden Name', validators=[Optional()])
    geneva_degrees = SelectMultipleField(
        "Geneva Degree(s)",
        choices=GENEVA_DEGREE_CHOICES,
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=False),
        validators=[Optional()],
    )

    undergrad_year = StringField(
        "Undergraduate Graduation Year",
        validators=[Optional()],
    )

    graduate_year = StringField(
        "Graduate Graduation Year",
        validators=[Optional()],
    )

    online_year = StringField(
        "Online Graduation Year",
        validators=[Optional()],
    )
    
    # Class note
    nameplate = StringField('Nameplate', validators=[Optional()])
    class_note_text = TextAreaField('Class Note', validators=[Optional(), Length(max=300)])
    image = FileField('Image', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')])
    existing_image = HiddenField()
    
    submit = SubmitField('Save')

class EditAlumniUpdateEntryForm(FlaskForm):
    # Contact / personal
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    maiden_name = StringField('Maiden Name', validators=[Optional()])
    email = StringField('Email Address', validators=[Optional(), Email()])
    phone = TelField('Phone Number', validators=[Optional()])
    phone_type = SelectField('Phone Type', choices=[('mobile', 'Mobile'), ('home', 'Home')], validators=[Optional()])
    geneva_degrees = SelectMultipleField(
            "Geneva Degree(s)",
            choices=GENEVA_DEGREE_CHOICES,
            option_widget=CheckboxInput(),
            widget=ListWidget(prefix_label=False),
            validators=[Optional()],
        )
    
    undergrad_year = StringField(
            "Undergraduate Graduation Year",
            validators=[Optional()],
        )
    
    graduate_year = StringField(
            "Graduate Graduation Year",
            validators=[Optional()],
        )
    
    online_year = StringField(
            "Online Graduation Year",
            validators=[Optional()],
        )
    update_types = SelectMultipleField(
        "What information would you like to share with the College?",
        choices=[
            ('Contact Information', "Contact Information"),
            ('Birth Announcement(s)', "Birth Announcement(s)"),
            ('Family Update', "Family Update"),
            ('Employment Update', "Employment Update"),
            ('Additional Education', "Additional Education"),
            ('Life Achievements', "Life Achievement(s)"),
        ],
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=True),
        validators=[Optional()]
    )

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
    spouse_geneva_degrees = SelectMultipleField(
            "Spouse's Geneva Degree(s)",
            choices=GENEVA_DEGREE_CHOICES,
            option_widget=CheckboxInput(),
            widget=ListWidget(prefix_label=False),
            validators=[Optional()],
        )
    spouse_undergrad_year = StringField(
            "Undergraduate Graduation Year",
            validators=[Optional()],
        )
    
    spouse_graduate_year = StringField(
            "Graduate Graduation Year",
            validators=[Optional()],
        )
    
    spouse_online_year = StringField(
            "Online Graduation Year",
            validators=[Optional()],
        )
    marry_date = DateField('Marriage Date', validators=[Optional()])

    # Children
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

    submit = SubmitField('Save')
