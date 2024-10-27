from flask import Flask, render_template, make_response, session, redirect, url_for
import flask
import auth

from top import app


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    username = auth.authenticate()
    print(username)
    return render_template('inland.html', username=username)

@app.route('/logout')
def logout():
    flask.session.clear()
    return redirect('/')
