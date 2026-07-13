from flask_wtf import FlaskForm
from wtforms import (
    StringField, DateField, TextAreaField,
    SelectMultipleField, SubmitField, TelField, HiddenField
)
from wtforms.validators import (
    DataRequired, Email, Optional, Length
)
from wtforms.widgets import ListWidget, CheckboxInput
from flask_wtf.file import FileField, FileAllowed


class EditFullEntryForm(FlaskForm):
    # Contact / personal
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    maiden_name = StringField('Maiden Name', validators=[Optional()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = TelField('Phone Number', validators=[Optional()])

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
    marry_date = DateField('Marriage Date', validators=[Optional()])

    # Child
    child_first_name = StringField('Child First Name', validators=[Optional()])
    child_last_name = StringField('Child Last Name', validators=[Optional()])
    child_gender = StringField('Child Gender', validators=[Optional()])
    child_birthday = DateField('Child Birthday', validators=[Optional()])

    # Employment / education / other
    employer = StringField('Employer', validators=[Optional()])
    position = StringField('Position', validators=[Optional()])
    institution = StringField('Institution', validators=[Optional()])
    additional_updates = TextAreaField("Additional Updates", validators=[Optional()])

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
    class_note_text = TextAreaField('Class Note', validators=[Optional(), Length(max=300)])
    image = FileField('Image', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')])
    existing_image = HiddenField()

    submit = SubmitField('Save')
