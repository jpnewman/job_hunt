from flask import Blueprint, Response, render_template, flash, redirect, session, url_for, request, g, send_file
from app import app, db
from app.emails.models import Emails, EmailAttachments
from sqlalchemy import desc
from io import BytesIO


mod = Blueprint('emails', __name__)


@mod.route('/emails/', methods=['GET'])
def emails_view():
    emails = Emails.query.order_by(desc(Emails.date)).all()
    return render_template('emails/index.html', emails=emails)


@mod.route('/emails/attachment/<int:id>', methods=['GET'])
def attachments_view(id):
    attachment = EmailAttachments.query.get(id)

    return send_file(
                BytesIO(attachment.binary),
                attachment_filename=attachment.name,
                mimetype=attachment.content_type,
                as_attachment=True,
                cache_timeout=-1
            )
