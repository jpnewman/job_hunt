from flask_wtf import FlaskForm
from wtforms import TextField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required, Email, Length
from app.agencies.models import Agency
from app import db


class RegisterAgencyForm(FlaskForm):
    name = TextField(validators=[Required()])
    address = TextField()
    phone_number = TextField()
    email = EmailField()
    website = TextField()
