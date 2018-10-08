from app import db
from app.mixins import CRUDMixin


class Jobs(CRUDMixin, db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Text, index=True)
    address = db.Column(db.Text)

    def __init__(self,
                 name=None,
                 address=None):
        self.name = name
        self.address = address

    def __repr__(self):
        return '<Jobs %r>' % (self.name)
