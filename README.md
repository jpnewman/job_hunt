
# Job Hunt

This is a Flask based application for tracking jobs and recruiters.

## References

- AWS EB: <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html>
- Google API: <https://developers.google.com/gmail/api/quickstart/python>

## Setup Environment

### Install python 3.5 (Mac OS X)

~~~
brew install pyenv

pyenv install 3.5.0
~~~

### Create Virtual Environment (Desktop Environment)

~~~
virtualenv -p ~/.pyenv/versions/3.5.0/bin/python3.5 venv
~~~

## Activate Virtual Environment (Desktop Environment)

~~~
source venv/bin/activate
~~~

## Check python version (Desktop Environment)

~~~
python -V
~~~

## Install python requirements (Desktop Environment)

~~~bash
pip install -r requirements.txt
~~~

## Freeze requirements (Desktop Environment)

~~~
pip freeze > requirements.txt
~~~

## Databases (Flask-Migrate)

### Init

~~~
flask db init
~~~

### Migrate

~~~
flask db migrate
~~~

### Upgrade

~~~
flask db upgrade
~~~

## Download E-Mails to Database

Create file ```credentials.json```.

~~~
./gmail.py
~~~

### Reprocess

~~~
./gmail.py --reprocess
~~~

### Max Downloads

~~~
./gmail.py --max-download 1
~~~

## Run (Desktop Environment)

~~~bash
python run.py
~~~

~~~
./run.py
~~~

## Deactivate Virtual Environment (Desktop Environment)

~~~
deactivate
~~~
