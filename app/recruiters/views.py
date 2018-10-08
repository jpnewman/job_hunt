from flask import Blueprint, Response, render_template, flash, redirect, session, url_for, request, g
from app import app, db
from app.recruiters.forms import RegisterRecruiterForm
from app.recruiters.models import Recruiter


mod = Blueprint('recruiters', __name__)


@mod.route('/recruiters/', methods=['GET'])
def recruiters_view_all():
    recruiters = Recruiter.query.all()
    return render_template('recruiters/index.html', recruiters=recruiters)


@mod.route('/recruiters/add', methods=['GET', 'POST'])
def recruiters_add():
    form = RegisterRecruiterForm(request.form)
    recruiters = Recruiter.query.all()
    if form.validate_on_submit():
        recruiter = Recruiters()
        form.populate_obj(recruiter)
        db.session.add(recruiter)
        db.session.commit()
        return redirect('/recruiters/')
    return render_template('recruiters/add.html', form=form, recruiters=recruiters)
