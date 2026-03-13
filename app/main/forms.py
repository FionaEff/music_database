from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from app import db
import sqlalchemy as sa


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")