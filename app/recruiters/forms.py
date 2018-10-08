from flask_wtf import FlaskForm
from wtforms import TextField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required, Email, Length
from app.recruiters.models import Recruiter
from app.agencies.models import Agency
from app import db


def enabled_agencies():
    return Agency.query.all()


class RegisterRecruiterForm(FlaskForm):
    name = TextField(validators=[Required()])
    phone_number = TextField()
    email = EmailField()
    agency = QuerySelectField(query_factory=enabled_agencies,
                              allow_blank=True)
