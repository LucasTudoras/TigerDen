import flask

app = flask.Flask('app', template_folder='./templates')
app.secret_key = 'some_secret'


