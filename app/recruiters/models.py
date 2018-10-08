from app import db
from app.mixins import CRUDMixin


class Recruiter(CRUDMixin, db.Model):
    __tablename__ = 'recruiters'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Text, index=True)
    phone_number = db.Column(db.Text, index=True)
    email = db.Column(db.Text, index=True)

    agency_id = db.Column(db.Integer, db.ForeignKey('agencies.id'))
    agency = db.relationship('Agency', back_populates='recruiters')

    def __init__(self,
                 name=None,
                 phone_number=None,
                 email=None):
        self.name = name
        self.phone_number = phone_number
        self.email = email

    def __repr__(self):
        return '<Recruiter %r>' % (self.name)
