import flask
import auth
from flask import Flask, render_template, request, g
import sqlite3
from top import app


@app.route('/')
def home():
    return flask.render_template('index.html')

@app.route('/login')
def login():
    username = auth.authenticate()
    print(username)
    return flask.render_template('inland.html', username=username)

@app.route('/logout')
def logout():
    flask.session.clear()
    return flask.redirect('/')

# Database setup
DATABASE = '../Database/rooms.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db != None:
        db.close()

# Search route
@app.route('/search', methods=['GET'])
def search():
    hall = request.args.get('hall', '').strip()
    college = request.args.get('college', '').strip()

    regions = []

    if request.args.get("Butler", '').strip() != '':
        regions.append("BUTLER")
    if request.args.get("Forbes", '').strip() != '':
        regions.append("FORBES")
    if request.args.get("Mid-Campus", '').strip() != '':
        regions.append("MID-CAMPUS")
    if request.args.get("New College", '').strip() != '':
        regions.append("NEW COLLEGE")
    if request.args.get("Roma", '').strip() != '':
        regions.append("ROMA")
    if request.args.get("Slums", '').strip() != '':
        regions.append("SLUMS")
    if request.args.get("Spelman", '').strip() != '':
        regions.append("SPELMAN")
    if request.args.get("Whitman", '').strip() != '':
        regions.append("WHIT")
    
    query = "SELECT * FROM rooms WHERE 1=1"
    params = []
    
    if hall:
        query += " AND Hall LIKE ?"
        params.append(f"%{hall}%")
    if college:
        query += " AND College LIKE ?"
        params.append(f"%{college}%")
    if regions:
        placeholder = ', '.join(['?'] * len(regions))
        query += f" AND Region IN ({placeholder})"
        params.extend(regions)
    print("Query:", query)
    print("Params:", params)
    cursor = get_db().execute(query, params)
    results = cursor.fetchall()
    cursor.close()

    # Map results to dictionary for template rendering
    column_names = [description[0] for description in cursor.description]
    rooms = [dict(zip(column_names, row)) for row in results]

    return render_template('search.html', results=rooms)

