from flask_wtf import FlaskForm
from wtforms import TextField
from wtforms.validators import Required, Email, Length
from app.jobs.models import Jobs
from app import db


class RegisterJobsForm(FlaskForm):
    name = TextField(validators=[Required()])
    address = TextField()
