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
    first_sort = request.args.get("First Sort")
    second_sort = request.args.get("Second Sort")
    sort_clauses = []

    if first_sort != '':
        sort_clauses.append(f"{first_sort}")
        if second_sort != '':
            sort_clauses.append(f"{second_sort}")

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


    types = []
    if request.args.get("Single", '').strip() != '':
        types.append("SINGLE")
    if request.args.get("Double", '').strip() != '':
        types.append("DOUBLE")
    if request.args.get("Triple", '').strip() != '':
        types.append("TRIPLE")
    if request.args.get("Quad", '').strip() != '':
        types.append("QUAD")
    if request.args.get("Quint", '').strip() != '':
        types.append("Quint")
    if request.args.get("6-Person", '').strip() != '':
        types.append("6PERSON")


    query = "SELECT * FROM rooms WHERE 1=1"
    params = []
    
    if regions:
        placeholder = ', '.join(['?'] * len(regions))
        query += f" AND Region IN ({placeholder})"
        params.extend(regions)
    if types:
        placeholder1 = ', '.join(['?'] * len(types))
        query += f" AND Type IN ({placeholder1})"
        params.extend(types)
    if sort_clauses:
        query += " ORDER BY " + ", ".join(sort_clauses)
    else:
        query += " ORDER BY College ASC, Region ASC, Hall ASC, Room ASC"
            

    cursor = get_db().execute(query, params)
    results = cursor.fetchall()
    cursor.close()

    # Map results to dictionary for template rendering
    column_names = [description[0] for description in cursor.description]
    rooms = [dict(zip(column_names, row)) for row in results]

    return render_template('search.html', results=rooms)

