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

    Butler = request.args.get("Butler")
    Forbes = request.args.get("Forbes")
    MidCampus = request.args.get("Mathey")
    NewCollege = request.args.get("New College West")
    Roma = request.args.get("Rocky")
    Slums = request.args.get("Upperclass")
    Whitman = request.args.get("Whitman")
    Yeh = request.args.get("Yeh College")

    Colleges = []
    if Butler:
        Colleges.append("Butler College")
    if Forbes:
        Colleges.append("Forbes College")
    if MidCampus:
        Colleges.append("Mathey College")
    if NewCollege:
        Colleges.append("New College West")
    if Roma:
        Colleges.append("Rockefeller College")
    if Slums:
        Colleges.append("UPPERCLASS")
    if Whitman:
        Colleges.append("Whitman College")
    if Yeh:
        Colleges.append("Yeh College")


    Single = request.args.get("Single")
    Double = request.args.get("Double")
    Triple = request.args.get("Triple")
    Quad = request.args.get("Quad")
    Quint = request.args.get("Quint")
    SixPerson = request.args.get("6-Person")
    
    types = []
    if Single:
        types.append("SINGLE")
    if Double:
        types.append("DOUBLE")
    if Triple:
        types.append("TRIPLE")
    if Quad:
        types.append("QUAD")
    if Quint:
        types.append("QUINT")
    if SixPerson:
        types.append("6PERSON")


    query = "SELECT * FROM rooms WHERE 1=1"
    params = []
    
    if Colleges:
        placeholder = ', '.join(['?'] * len(Colleges))
        query += f" AND College IN ({placeholder})"
        params.extend(Colleges)
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

@app.route("/room_details/<roomID>")
def room_details(roomID):
    query = "SELECT * FROM rooms WHERE 1=1"
    params = []
    query += " And RoomID = ?"
    params.append(roomID)
    cursor = get_db().execute(query, params)
    results = cursor.fetchall()
    cursor.close()

    column_names = [description[0] for description in cursor.description]
    room = [dict(zip(column_names, row)) for row in results]
    return render_template('room_details.html', results = room)