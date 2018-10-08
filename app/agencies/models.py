from app import db
from app.mixins import CRUDMixin


class Agency(CRUDMixin, db.Model):
    __tablename__ = 'agencies'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Text, index=True)
    address = db.Column(db.Text)
    phone_number = db.Column(db.Text)
    email = db.Column(db.Text, index=True)
    website = db.Column(db.Text, index=True)

    recruiters = db.relationship('Recruiter', back_populates='agency',
                                 lazy='select')

    def __init__(self,
                 name=None,
                 address=None,
                 phone_number=None,
                 email=None,
                 website=None):
        self.name = name
        self.address = address
        self.phone_number = phone_number
        self.email = email
        self.website = website

    def __repr__(self):
        return '%s' % (self.name)
