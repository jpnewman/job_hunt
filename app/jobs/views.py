from flask import Blueprint, Response, render_template, flash, redirect, session, url_for, request, g
from app import app, db
from app.jobs.forms import RegisterJobsForm
from app.jobs.models import Jobs


mod = Blueprint('jobs', __name__)


@mod.route('/jobs/', methods=['GET'])
def jobs_view_all():
    jobs = Jobs.query.all()
    return render_template('jobs/index.html', jobs=jobs)


@mod.route('/jobs/add', methods=['GET', 'POST'])
def jobs_add():
    form = RegisterJobsForm(request.form)
    jobs = Jobs.query.all()
    if form.validate_on_submit():
        job = Jobs()
        form.populate_obj(job)
        db.session.add(job)
        db.session.commit()
        return redirect('/jobs/')
    return render_template('jobs/add.html', form=form, jobs=jobs)
