import flask
import os
app = flask.Flask('app', template_folder='./templates')
app.secret_key = os.environ['SECRET_KEY']


