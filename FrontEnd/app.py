from flask import Flask, render_template, make_response, session, redirect, url_for
import auth


app = Flask(__name__)
app.secret_key = 'some_secret'


@app.route('/')
def home():
    username = auth.authenticate()
    return render_template('index.html', username=username)


if __name__ == '__main__':
    app.run(debug=True)
