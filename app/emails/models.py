from app import db
from app.mixins import CRUDMixin


class Emails(CRUDMixin, db.Model):
    __tablename__ = 'emails'
    id = db.Column(db.Integer, primary_key=True)

    message_id = db.Column(db.Text, index=True)
    sender = db.Column(db.Text, index=True)
    from_address = db.Column(db.Text, index=True)
    subject = db.Column(db.Text)
    date = db.Column(db.DateTime)
    plain_text = db.Column(db.Text)
    html = db.Column(db.Text)
    raw = db.Column(db.Text)

    contents = db.relationship('EmailContents', back_populates='email',
                                 lazy='select')

    attachments = db.relationship('EmailAttachments', back_populates='email',
                                 lazy='select')

    def __init__(self,
                 message_id=None,
                 sender=None,
                 from_address=None,
                 subject=None,
                 date=None,
                 plain_text=None,
                 html = html,
                 raw=None):
        self.message_id = message_id
        self.sender = sender
        self.from_address = from_address
        self.subject = subject
        self.date = date
        self.plain_text = plain_text
        self.html = html
        self.raw = raw

    def __repr__(self):
        return '<Email %r %r %r>' % (self.sender, self.date.strftime('%m/%d/%Y %H:%M:%S'), self.subject)


class EmailContents(CRUDMixin, db.Model):
    __tablename__ = 'emailcontents'
    id = db.Column(db.Integer, primary_key=True)

    email_id = db.Column(db.Integer, db.ForeignKey('emails.id'))
    email = db.relationship('Emails', back_populates='contents')


class EmailAttachments(CRUDMixin, db.Model):
    __tablename__ = 'emailattachments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    size = db.Column(db.Text)
    content_type = db.Column(db.Text)
    create_date = db.Column(db.Text)
    mod_date = db.Column(db.Text)
    read_date = db.Column(db.Text)
    checksum = db.Column(db.Text)
    binary = db.Column(db.LargeBinary)

    email_id = db.Column(db.Integer, db.ForeignKey('emails.id'))
    email = db.relationship('Emails', back_populates='attachments')
