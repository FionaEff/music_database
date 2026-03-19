from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Length
from app import db
import sqlalchemy as sa


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")


class AddAlbumForm(FlaskForm):
    album_name = StringField("Album Name", validators=[DataRequired(), Length(max=64)])

    existing_artist = SelectField("Choose an artist", coerce=int)
    new_artist = StringField("Artist", validators=[Length(max=128)])

    existing_genre = SelectField("Choose a genre", coerce=int)
    new_genre = StringField("Genre", validators=[Length(max=32)])

    year = IntegerField("Year")
    label = StringField("Label", validators=[Length(max=64)])

    format = SelectField(
        "Format",
        choices=[("vinyl", "Vinyl"), ("cd", "CD"), ("digital", "Digital")],
        validators=[DataRequired()],
    )

    discogs_id = IntegerField("Discogs ID")
    notes = StringField("Notes (Optional)", validators=[Length(max=256)])

    submit = SubmitField("Add Album")

    def _validate_choice_or_input(self, select_field, text_field, field_name):
        existing = select_field.data != 0
        new = bool(text_field.data and text_field.data.strip())

        if not existing and not new:
            text_field.errors.append(
                f"Select an existing {field_name} or enter a new one."
            )
            return False

        if existing and new:
            text_field.error.append(
                f"Select an existing {field_name} or enter a new one, not both."
            )
            return False

        return True

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        valid = True

        valid &= self._validate_choice_or_input(
            self.existing_artist, self.new_artist, "artist"
        )

        valid &= self._validate_choice_or_input(
            self.existing_genre, self.new_genre, "genre"
        )

        return valid


class EditArtistForm(FlaskForm):
    name = StringField("Artist Name", validators=[DataRequired(), Length(max=128)])
    country = StringField("Country", validators=[Length(max=64)])
    year_of_founding = IntegerField("Year of Founding")
    notes = StringField("Notes", validators=[Length(max=256)])
    submit = SubmitField("Save Changes")
