import flask
import auth
from flask import Flask, render_template, request, g, make_response
import sqlite3
from top import app


@app.route('/')
def home():
    return flask.render_template('index.html')

@app.route('/groups')
def groups():
    return flask.render_template('groups.html')

@app.route('/campus-map')
def campus_map():
    return flask.render_template('campus_map.html')

@app.route('/floor-plans')
def floor_plans():
    return flask.render_template('floor_plans.html')

@app.route('/upload-pdf')
def upload_pdf():
    return flask.render_template('upload_pdf.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = auth.authenticate()
    selected_colleges = ['Butler', 'Forbes', 'Mathey', 'New College West', 'Rocky',
                        'Upperclass', 'Whitman', 'Yeh',]
    
    selected_types = ['Single', 'Double','Triple', 'Quad', 'Quint', '6-Person']
    
    if request.method == 'POST':
        print("REQUEST ARRIVED")
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/x-www-form-urlencoded':
            selected_colleges = request.form.getlist('CollegeOptions')
            selected_types = request.form.getlist('TypeOptions')

    search_data = {
        'FirstSort': request.args.get('FirstSort', request.cookies.get('FirstSort', 'Sqft')),
        'SecondSort': request.args.get('SecondSort', request.cookies.get('SecondSort', 'College')),
        'FirstOrder': request.args.get('FirstOrder', request.cookies.get('FirstOrder', 'DESC')),
        'SecondOrder': request.args.get('SecondOrder', request.cookies.get('SecondOrder', 'ASC')),
        'selected_colleges': selected_colleges,
        'selected_types': selected_types
    }
    name_discreptancies = {
        'Butler': 'Butler College',
        'Forbes': 'Forbes College',
        'Mathey': 'Mathey College',
        'New College West': 'New College West',
        'Rocky': 'Rockefeller College',    
        'Upperclass': 'UPPERCLASS',    
        'Whitman': 'Whitman College',    
        'Yeh': 'Yeh College',    
        'Single': 'SINGLE',
        'Double': 'DOUBLE',
        'Triple': 'TRIPLE',
        'Quad': 'QUAD',
        'Quint': 'QUINT',
        '6-Person': '6PERSON'
    }
    

    colleges = [name_discreptancies[college] for college in selected_colleges]
    types = [name_discreptancies[type] for type in selected_types]
    sort_clauses = [search_data['FirstSort'] + ' ' + search_data['FirstOrder'],
                    search_data['SecondSort'] + ' ' + search_data['SecondOrder']]

    query = "SELECT * FROM rooms WHERE 1=1"
    params = []
    
    if not colleges or not types:
        return flask.render_template('inland.html', username=username, user_data=search_data, results=[])

    if colleges:
        placeholder = ', '.join(['?'] * len(colleges))
        query += f" AND College IN ({placeholder})"
        params.extend(colleges)
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
    print(search_data)
    response = make_response(render_template('inland.html', username=username, user_data=search_data, results=rooms))
    print(search_data)
    for key, value in search_data.items():
        if type(value) is not list:
            response.set_cookie(key, value)
    return response

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
    if db is not None:
        db.close()



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