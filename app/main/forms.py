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
    new_genre = StringField("Genre", validators=Length(max=32))

    year = IntegerField("Year")
    label = StringField("Label", validators=[Length(min=0, max=64)])

    format = SelectField(
        "Format",
        choices=[("vinyl", "Vinyl"), ("cd", "CD"), ("digital", "Digital")],
        validators=[DataRequired()],
    )

    discogs_id = IntegerField("Discogs ID")
    notes = StringField("Notes (Optional)", validators=[Length(max=256)])

    submit = SubmitField("Add Album")

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        valid = True

        # Artist validation
        if self.artist.data == 0 and not self.new_artist.data:
            self.new_artist.errors.append(
                "Select an existing artist or enter a new one."
            )
            valid = False

        if self.artist.data != 0 and not self.new_artist.data:
            self.new_artist.errors.append(
                "Select an existing artist or enter a new one, not both."
            )
            valid = False

        # Genre validation
        if self.genre.data == 0 and not self.new_genre.data:
            self.new_genre.errors.append("Select an existing genre or enter a new one.")
            valid = False

        if self.genre.data != 0 and not self.new_genre.data:
            self.new_genre.errors.append(
                "Select an existing genre or enter a new one, not both."
            )
            valid = False

        return valid
