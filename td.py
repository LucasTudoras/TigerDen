import flask
import auth
import flask
import psycopg2
import os
from werkzeug.utils import secure_filename
from top import app
from colleges import collegesDict
import update
import checkNetid
from operator import itemgetter

# Database setup
DATABASE = os.environ['DATABASE_URL']
UPLOAD_FOLDER = '/tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# error handling
@app.errorhandler(404)
def not_found(e):
    return flask.render_template('error.html'), 404

@app.errorhandler(405)
def invalid_route405(e):
    return flask.render_template('error.html'), 405

@app.errorhandler(415)
def invalid_route415(e):
    return flask.render_template('error.html'), 415

@app.route('/')
def home():
    return flask.render_template('index.html')

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()

@app.route('/logout')
def logout():
    flask.session.clear()
    return flask.redirect('/')

@app.route('/favorite-rooms')
def favorite_rooms():
    user_id = username = auth.authenticate()

    # display the users favorites
    with psycopg2.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT rooms.*
            FROM rooms
            JOIN favorites ON rooms.RoomID = favorites.room_id
            WHERE favorites.user_id = %s
        """, (user_id,))
        rooms = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        favorite_rooms = [dict(zip(column_names, row)) for row in rooms]
        for room in favorite_rooms:
            cursor.execute(""" 
                SELECT user_id
                FROM availables
                WHERE room_id = %s AND user_id = %s          
                """,(room['roomid'], user_id,))
            available = cursor.fetchone()
            if available:
                room['is_available'] = '/static/images/GreenCheckMark.png'
            else:
                room['is_available'] = '/static/images/RedX.png'
            room['is_favorite'] = True
        cursor.close()
    
    sorted_by_availability = sorted(favorite_rooms, key=itemgetter('is_available'))

    return flask.render_template('favorite_rooms.html', favorite_rooms=sorted_by_availability)

@app.route('/groups')
def groups():
    username = auth.authenticate()
    with psycopg2.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Does user belong to a group
        cursor.execute("""
            SELECT groups.id, groups.name, members.user_id
            FROM groups
            JOIN members ON groups.id = members.group_id
            WHERE members.user_id = %s
        """, (username,))
        group_data = cursor.fetchall()

        # Organize group data
        organized_groups = []
        for group in group_data:
            organized_groups.append({'id': group[0], 'name': group[1]})

        user_has_group = bool(group_data)
        names_of_group = {}
        # Get all members of each group
        group_member_data = {}
        if user_has_group:
            for group in organized_groups:
                group_id = group['id']
                cursor.execute("""
                    SELECT user_id
                    FROM members
                    WHERE members.group_id = %s
                """, (group_id,))
                group_member_data[group_id] = [member[0] for member in cursor.fetchall()]

                # adds all the members in the group
                group['members'] = group_member_data[group_id]
                group['member_names'] = []
                for member in group['members']:
                    name = checkNetid.main(member)
                    names_of_group[member] = name
                    group['member_names'].append(name)        

        # queries all the favorite rooms of all the different members
        group_favorite_rooms = []
        if user_has_group:
            for group in organized_groups:
                group_id = group['id']
                cursor.execute("""
                    SELECT rooms.*,
                        MAX(CASE WHEN favorites.user_id IS NOT NULL THEN 1 ELSE 0 END) AS is_favorite
                    FROM rooms
                    LEFT JOIN favorites ON rooms.roomid = favorites.room_id
                    WHERE favorites.user_id IN (
                        SELECT user_id
                        FROM members
                        WHERE group_id = %s
                    )
                    GROUP BY rooms.roomid
                """, (group_id,))
                rooms = cursor.fetchall()
                
                column_names = [description[0] for description in cursor.description]
                group_favorite_rooms += [dict(zip(column_names, row)) for row in rooms]

                for room in group_favorite_rooms:
                    roomid = room['roomid']
                    cursor.execute("""
                        SELECT favorites.user_id
                        FROM favorites
                        INNER JOIN members ON favorites.user_id = members.user_id
                        WHERE favorites.room_id = %s AND members.group_id = %s
                    """, (roomid, group_id))

                    room['favorited_by_netid'] = cursor.fetchall()
                    room['favorited_by'] = []
                    for member in room['favorited_by_netid']:
                        room['favorited_by'].append(names_of_group[member[0]])

                    cursor.execute(""" 
                        SELECT user_id
                        FROM availables
                        WHERE room_id = %s AND user_id = %s      
                        """,(room['roomid'], username,))
                    available = cursor.fetchone()
                    if available:
                        room['is_available'] = '/static/images/GreenCheckMark.png'
                    else:
                        room['is_available'] = '/static/images/RedX.png'
                cursor.close()
            sorted_by_availability = sorted(group_favorite_rooms, key=itemgetter('is_available'))  
            if sorted_by_availability:
                group_favorite_rooms = sorted_by_availability

        return flask.render_template('groups.html', user_has_group=user_has_group, groups=organized_groups, rooms=group_favorite_rooms, username=username)

@app.route('/create_group', methods=['POST'])
def create_group():
    username = auth.authenticate()
    group_name = flask.request.form.get('group_name')
    netids = flask.request.form.get('netids')
    
    if not group_name or not netids:
        return flask.jsonify({'success': False, 'message': 'Group name and members are required'}), 400
    
    netids_list = [n.strip() for n in netids.split(',') if (n.strip())] 
    netids = set(netids_list)
    netids_list = list(netids)
    valid_netid_list = []
    valid_name_list = []
    invalid_netid_list = []

    # check netids
    for netid in netids_list:
        valid_NETID = checkNetid.main(netid)
        if valid_NETID:
            valid_name_list.append(valid_NETID)
            valid_netid_list.append(netid)
        else:
            invalid_netid_list.append(netid)


    with psycopg2.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO groups (name, admin_username) VALUES (%s, %s) RETURNING id', (group_name, username))

        group_id = cursor.fetchone()[0]
        
        cursor.execute('INSERT INTO members (user_id, group_id) VALUES (%s, %s)', (username, group_id))
        already_in_group = []

        for netid in valid_netid_list:
            cursor.execute("""
                SELECT 1 FROM members 
                WHERE user_id = %s
            """, (netid,))
            #checks to see if the netid is in group
            existing_group = cursor.fetchone()
            if existing_group:
                already_in_group.append(netid)
            else:
                cursor.execute('INSERT INTO members (user_id, group_id) VALUES (%s, %s)', (netid, group_id))

        cursor.execute(""" 
                    SELECT COUNT(*) FROM members WHERE group_id = %s
                """, (group_id,))
        memeber_count = cursor.fetchone()[0]
        if memeber_count <=1:
            cursor.execute("""
                DELETE FROM members WHERE group_id = %s
                """, (group_id,))
            cursor.execute("""
                DELETE FROM groups WHERE id = %s
                """, (group_id,))

        conn.commit()
        cursor.close()

    # Prepare response messages
    message = ""
    if invalid_netid_list:
            message += f"The following netids are not valid \'{', '.join(invalid_netid_list)} \'\n"
    elif already_in_group:
        message += f"Cannot add the following users as they are already in a group: \'{', '.join(already_in_group)} \'"
    else:
        message += f"Successfully added: \' {', '.join(valid_name_list)} \'"

    return flask.jsonify({'success': True, 'message': message})

@app.route('/add_member', methods=['POST'])
def add_member():
    username = auth.authenticate()
    #group_id = flask.request.form.get('group_id')
    netids = flask.request.form.get('netids')

    # if not group_id or not netids:
    # return flask.jsonify({'success': False, 'message': 'Group ID and NetIDs are required'}), 400

    netids_list = [n.strip() for n in netids.split(',') if n.strip()]
    netids_set = set(netids_list)
    netids_list = list(netids_set)
    valid_netid_list = []
    invalid_netid_list = []
    valid_name_list=[]

    # ensure valid netids
    for netid in netids_list:
        valid_NETID = checkNetid.main(netid)
        if valid_NETID:
            valid_name_list.append(valid_NETID)
            valid_netid_list.append(netid)
        else:
            invalid_netid_list.append(netid)

    already_in_group = []

    with psycopg2.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
                SELECT group_id FROM members WHERE user_id = %s
            """, (username,))
        group_id = cursor.fetchone()
        
        for netid in valid_netid_list:
            # Check if the user is already in another group
            cursor.execute("""
                SELECT group_id FROM members WHERE user_id = %s
            """, (netid,))
            existing_group = cursor.fetchone()

            if existing_group:  # User is in another group
                already_in_group.append(netid)
            else:
                cursor.execute("""
                    SELECT 1 FROM members WHERE user_id = %s AND group_id = %s
                """, (netid, group_id))
                if cursor.fetchone() is None:  # If the user is not already a member
                    cursor.execute("""
                        INSERT INTO members (user_id, group_id) VALUES (%s, %s)
                    """, (netid, group_id))

        conn.commit()
        cursor.close()

    # Prepare response messages
    message = ""
    if invalid_netid_list:
            message += f"The following netids are not valid \'{', '.join(invalid_netid_list)} \'\n"
    elif already_in_group:
        message += f"Cannot add the following users as they are already in a group: {', '.join(already_in_group)}."
    else:
        message += f"Successfully added members \'{', '.join(valid_name_list)} \'\n"


    return flask.jsonify({'success': True, 'message': message})

@app.route('/leave-group', methods=['GET', 'POST'])
def leave_group():
    username = auth.authenticate()
    if flask.request.method == 'POST':
        with psycopg2.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT group_id FROM members WHERE user_id = %s
            """, (username,))
            group_id = cursor.fetchone()
            if group_id:
                cursor.execute("""
                    DELETE FROM members WHERE user_id = %s AND group_id = %s
                """, (username, group_id[0]))

                cursor.execute(""" 
                    SELECT COUNT(*) FROM members WHERE group_id = %s
                """, (group_id[0],))
                memeber_count = cursor.fetchone()[0]
                cursor.execute(""" 
                    SELECT admin_username FROM groups WHERE id = %s
                """, (group_id[0],))
                admin = cursor.fetchone()[0]
                if memeber_count <=1 or admin== username:
                    cursor.execute("""
                        DELETE FROM members WHERE group_id = %s
                        """, (group_id[0],))
                    cursor.execute("""
                        DELETE FROM groups WHERE id = %s
                        """, (group_id[0],))

                conn.commit()
            cursor.close()
    return flask.redirect('/groups')

@app.route('/campus-map')
def campus_map():
    username = auth.authenticate()
    return flask.render_template('campus_map.html')

@app.route('/floor-plans')
def floor_plans():
    username = auth.authenticate()
    return flask.render_template('floor_plans.html')

def get_db():
    db = getattr(flask.g, '_database', None)
    if db is None:
        db = flask.g._database = psycopg2.connect(DATABASE)
    return db

@app.route("/room_details/<roomID>")
def room_details(roomID):
    username = auth.authenticate()
    query = """
        SELECT rooms.*,
        CASE WHEN favorites.user_id IS NOT NULL THEN 1 ELSE 0 END AS is_favorite
        FROM rooms
        LEFT JOIN favorites ON rooms.RoomID = favorites.room_id AND favorites.user_id = %s
        WHERE 1=1
        """
    params = [username]
    query += " And RoomID = %s"
    params.append(roomID)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    room = [dict(zip(column_names, row)) for row in results]
    cursor.close()

    return flask.render_template('room_details.html', results = room)

@app.route("/room_details_browsing/<roomID>")
def room_details_browsing(roomID):
    username = auth.authenticate()
    query = """
        SELECT rooms.*,
        CASE WHEN favorites.user_id IS NOT NULL THEN 1 ELSE 0 END AS is_favorite
        FROM rooms
        LEFT JOIN favorites ON rooms.RoomID = favorites.room_id AND favorites.user_id = %s
        WHERE 1=1
        """
    params = [username]
    query += " And RoomID = %s"
    params.append(roomID)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    room = [dict(zip(column_names, row)) for row in results]
    cursor.close()

    return flask.render_template('room_details_browsing.html', results = room)

@app.route("/room_details_groups/<roomID>")
def room_details_groups(roomID):
    username = auth.authenticate()
    query = """
        SELECT rooms.*,
        CASE WHEN favorites.user_id IS NOT NULL THEN 1 ELSE 0 END AS is_favorite
        FROM rooms
        LEFT JOIN favorites ON rooms.RoomID = favorites.room_id AND favorites.user_id = %s
        WHERE 1=1
        """
    params = [username]
    query += " And RoomID = %s"
    params.append(roomID)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    room = [dict(zip(column_names, row)) for row in results]
    cursor.close()

    return flask.render_template('room_details_groups.html', results = room)

@app.route("/room_details_favorites/<roomID>")
def room_details_favorites(roomID):
    username = auth.authenticate()
    query = """
        SELECT rooms.*,
        CASE WHEN favorites.user_id IS NOT NULL THEN 1 ELSE 0 END AS is_favorite
        FROM rooms
        LEFT JOIN favorites ON rooms.RoomID = favorites.room_id AND favorites.user_id = %s
        WHERE 1=1
        """
    params = [username]
    query += " And RoomID = %s"
    params.append(roomID)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    room = [dict(zip(column_names, row)) for row in results]
    cursor.close()

    return flask.render_template('room_details_favorites.html', results = room)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@app.route("/PDF", methods=["GET", "POST"])
@app.route("/upload-pdf", methods=["GET", "POST"])
def uploaded_PDF():
    username = auth.authenticate()
    print("in this method")
    if flask.request.method == "POST":
        print("POSTed something")
        if 'pdf' not in flask.request.files:
            return flask.jsonify({"success": False, "message": "No file part"}), 400
        
        file = flask.request.files['pdf']
        if file.filename == '':
            return flask.jsonify({"success": False, "message": "No selected file"}), 400
        
        if file and allowed_file(file.filename):
            # imported method
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # find method from pdf.py
            #uploaded_rooms = PDF.main(filepath)
            uploaded_rooms = update.database_update(filepath, DATABASE, username)
            os.remove(filepath)
            if uploaded_rooms is None:
                return flask.jsonify({"success": False, "message": "Please upload a valid Room Draw PDF"}), 200
            #print(uploaded_rooms)

            return flask.jsonify({"success": True, "message": "PDF uploaded successfully", "rooms": uploaded_rooms}), 200
        else:
            return flask.jsonify({"success": False, "message": "Invalid file format. Please upload a PDF."}), 400
    
    return flask.render_template('upload_pdf.html')

@app.route("/college/<college>")
def return_halls(college):
    username = auth.authenticate()
    halls = []
    if college == 'Butler College':
        halls = ['1967', '1976', 'Bloomberg', 'Bogle', 'Scully', 'Wilf', 'Yoseloff']

    elif college == 'Forbes College':
        halls = ['99Alexander', 'Annex', 'Main']

    elif college == 'Mathey College':
        halls = ['Blair', 'Campbell', 'Edwards', 'Hamilton', 'Joline', 'Little']
        
    elif college == 'New College West':
        halls = ['Addy', 'Jose E. Feliciano', 'Kanji', 'Kwanza Jones']
    
    elif college == 'Rockefeller College':
        halls = ['Buyers', 'Campbell', 'Holder', 'Witherspoon']

    elif college == 'Upperclass':
        halls = ['1901', 'Feinberg','Patton', '1903', 'Foulke', 'Pyne', 'Brown', 'Henry', 'Scully', 'Cuyler', 'Laughlin', 'Spelman', 'Dickinson Street, 2', 'Little', 'Walker', 'Dod', 'Lockhart', 'Wright']

    elif college == 'Whitman College':
        halls = ['1981', 'Baker E', 'Baker S', 'Fisher', 'Hargadon', 'Lauritzen', 'Murley', 'Wendell B', 'Wendell C']
    
    elif college == 'Yeh College':
        halls = ['Fu', 'Grousbeck', 'Hariri', 'Mannion']
    return flask.render_template('/halls.html', results = halls, college = college)

@app.route("/samehall/<hall> <room>")
def return_sameHallFloorPlan(hall, room):
    username = auth.authenticate()
    hallOG = hall
    hall = hall.title()
    colleges = collegesDict
    college = colleges[hall]
    directory_path = "FloorPlan/" + college + "/" + hall
    test = []
    filepaths = []
    for filename in os.listdir('static/' + directory_path):
        temp_name = filename.replace(".pdf", '')
        if temp_name == 'Lower':
            temp_name = 'Basement Floor'
        if temp_name == '0':
            temp_name = "0th Floor"
        if temp_name == '1':
            temp_name = '1st Floor'
        if temp_name == '2':
            temp_name = '2nd Floor'
        if temp_name == '3':
            temp_name = '3rd Floor'
        if temp_name == '4':
            temp_name = '4th Floor'
        if temp_name == '5':
            temp_name = '5th Floor'
        if temp_name == '6':
            temp_name = '6th Floor'
        if temp_name == '7':
            temp_name = '7th Floor'
        if temp_name == '8':
            temp_name = '8th Floor'
        temp = {
            'name': temp_name,
            'filepath': directory_path + "/" +filename
        }
        
        test.append(temp)
        filepaths.append(temp['filepath'])

    filepaths.sort()
    sorted_test = sorted(test, key=lambda x: x['name'])
    return flask.render_template('floors_roomsearch.html', results = filepaths, test = sorted_test, hall = hall, college = college, room = room, hallBack = hallOG)

@app.route("/samehall_favorites/<hall> <room>")
def return_sameHallFavoritesFloorPlan(hall, room):
    username = auth.authenticate()
    hallOG = hall
    hall = hall.title()
    colleges = collegesDict
    college = colleges[hall]
    directory_path = "FloorPlan/" + college + "/" + hall
    test = []
    filepaths = []
    for filename in os.listdir('static/' + directory_path):
        temp_name = filename.replace(".pdf", '')
        if temp_name == 'Lower':
            temp_name = 'Basement Floor'
        if temp_name == '0':
            temp_name = "0th Floor"
        if temp_name == '1':
            temp_name = '1st Floor'
        if temp_name == '2':
            temp_name = '2nd Floor'
        if temp_name == '3':
            temp_name = '3rd Floor'
        if temp_name == '4':
            temp_name = '4th Floor'
        if temp_name == '5':
            temp_name = '5th Floor'
        if temp_name == '6':
            temp_name = '6th Floor'
        if temp_name == '7':
            temp_name = '7th Floor'
        if temp_name == '8':
            temp_name = '8th Floor'
        temp = {
            'name': temp_name,
            'filepath': directory_path + "/" +filename
        }
        
        test.append(temp)
        filepaths.append(temp['filepath'])

    filepaths.sort()
    sorted_test = sorted(test, key=lambda x: x['name'])
    return flask.render_template('floors_favorites.html', results = filepaths, test = sorted_test, hall = hall, college = college, room = room, hallBack = hallOG)

@app.route("/samehall_groups/<hall> <room>")
def return_sameHallGroupsFloorPlan(hall, room):
    username = auth.authenticate()
    hallOG = hall
    hall = hall.title()
    colleges = collegesDict
    college = colleges[hall]
    directory_path = "FloorPlan/" + college + "/" + hall
    test = []
    filepaths = []
    for filename in os.listdir('static/' + directory_path):
        temp_name = filename.replace(".pdf", '')
        if temp_name == 'Lower':
            temp_name = 'Basement Floor'
        if temp_name == '0':
            temp_name = "0th Floor"
        if temp_name == '1':
            temp_name = '1st Floor'
        if temp_name == '2':
            temp_name = '2nd Floor'
        if temp_name == '3':
            temp_name = '3rd Floor'
        if temp_name == '4':
            temp_name = '4th Floor'
        if temp_name == '5':
            temp_name = '5th Floor'
        if temp_name == '6':
            temp_name = '6th Floor'
        if temp_name == '7':
            temp_name = '7th Floor'
        if temp_name == '8':
            temp_name = '8th Floor'
        temp = {
            'name': temp_name,
            'filepath': directory_path + "/" +filename
        }
        
        test.append(temp)
        filepaths.append(temp['filepath'])

    filepaths.sort()
    sorted_test = sorted(test, key=lambda x: x['name'])
    return flask.render_template('floors_groups.html', results = filepaths, test = sorted_test, hall = hall, college = college, room = room, hallBack = hallOG)

@app.route("/samehall_browsing/<hall> <room>")
def return_sameHallBrowsingFloorPlan(hall, room):
    username = auth.authenticate()
    hallOG = hall
    hall = hall.title()
    colleges = collegesDict
    college = colleges[hall]
    directory_path = "FloorPlan/" + college + "/" + hall
    test = []
    filepaths = []
    for filename in os.listdir('static/' + directory_path):
        temp_name = filename.replace(".pdf", '')
        if temp_name == 'Lower':
            temp_name = 'Basement Floor'
        if temp_name == '0':
            temp_name = "0th Floor"
        if temp_name == '1':
            temp_name = '1st Floor'
        if temp_name == '2':
            temp_name = '2nd Floor'
        if temp_name == '3':
            temp_name = '3rd Floor'
        if temp_name == '4':
            temp_name = '4th Floor'
        if temp_name == '5':
            temp_name = '5th Floor'
        if temp_name == '6':
            temp_name = '6th Floor'
        if temp_name == '7':
            temp_name = '7th Floor'
        if temp_name == '8':
            temp_name = '8th Floor'
        temp = {
            'name': temp_name,
            'filepath': directory_path + "/" +filename
        }
        
        test.append(temp)
        filepaths.append(temp['filepath'])

    filepaths.sort()
    sorted_test = sorted(test, key=lambda x: x['name'])
    return flask.render_template('floors_browsing.html', results = filepaths, test = sorted_test, hall = hall, college = college, room = room, hallBack = hallOG)

@app.route("/floors/<college> <hall>")
def return_floorplans(college, hall):
    username = auth.authenticate()
    if college == "New College West Jose E.":
        college = "New College West"
        hall = "Jose E. Feliciano"
    if college == "New College West Kwanza":
        college = "New College West"
        hall = "Kwanza Jones"
    if college == "Upperclass Dickinson Street,":
        college = 'Upperclass'
        hall = "Dickinson Street, 2"
    if college == "Whitman College Wendell" and hall == 'B':
        college = "Whitman College"
        hall = "Wendell B"
    if college == "Whitman College Wendell" and hall == 'C':
        college = "Whitman College"
        hall = "Wendell C"
    if college == "Whitman College Baker" and hall == 'E':
        college = "Whitman College"
        hall = "Baker E"
    if college == "Whitman College Baker" and hall == 'S':
        college = "Whitman College"
        hall = "Baker S"
    if hall == 'Kanji':
        hall = 'Aliya Kanji'
    

    if college == 'Upperclass' or college == 'New College West':
        directory_path = "FloorPlan/" + college + "/" + hall
        if college == 'New College West':
            college = 'NCW'
    else:
        directory_path = "FloorPlan/" + college + "/" + hall
    test = []
    filepaths = []
    
    for filename in os.listdir('static/' + directory_path):
        temp_name = filename.replace(".pdf", '')
        if temp_name == 'Lower':
            temp_name = 'Basement Floor'
        if temp_name == '0':
            temp_name = "0th Floor"
        if temp_name == '1':
            temp_name = '1st Floor'
        if temp_name == '2':
            temp_name = '2nd Floor'
        if temp_name == '3':
            temp_name = '3rd Floor'
        if temp_name == '4':
            temp_name = '4th Floor'
        if temp_name == '5':
            temp_name = '5th Floor'
        if temp_name == '6':
            temp_name = '6th Floor'
        if temp_name == '7':
            temp_name = '7th Floor'
        if temp_name == '8':
            temp_name = '8th Floor'
        temp = {
            'name': temp_name,
            'filepath': directory_path + "/" + filename
        }
        
        test.append(temp)
        filepaths.append(temp['filepath'])

    filepaths.sort()
    sorted_test = sorted(test, key=lambda x: x['name'])
    return flask.render_template('floors.html', results = filepaths, test = sorted_test, hall = hall, college = college)

@app.route('/favorite', methods=['POST', 'GET'])
def toggle_favorite():
    user_id = username = auth.authenticate()
    data = flask.request.get_json()
    room_id = data.get('room_id')
    if not room_id or not user_id:
        return flask.jsonify({"success": False, "message": "Invalid input"}), 400
    with psycopg2.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM favorites WHERE user_id = %s AND room_id = %s", (user_id, room_id))
        exists = cursor.fetchone()
        if exists:
            # unstar
            print("ALREADY FAV")
            cursor.execute("DELETE FROM favorites WHERE user_id =%s AND room_id = %s", (user_id, room_id))
            conn.commit()
            return flask.jsonify({'success': True, 'message': 'Room removed from favorites', 'is_favorite': False})
        else:
            # star
            print("WILL FAV")
            cursor.execute("INSERT INTO favorites (user_id, room_id) VALUES (%s, %s)", (user_id, room_id))
            conn.commit()
            return flask.jsonify({'success': True, 'message': 'Room added to favorites', 'is_favorite': True})


@app.route('/newtab/<hall> <room> <floor>')
def newtab(hall, room, floor):
    print(hall, room, floor)
    if hall == "Wendell":
        if room[0] == "B":
            hall = "Wendell B"
        else:
            hall = "Wendell C"
    if hall == "Baker":
        if room[0] == "S":
            hall = "Baker S"
        else:
            hall = "Baker E"

    hall = hall.title()
    colleges = collegesDict
    college = colleges[hall]
    directory_path = "/static/FloorPlan/" + college + "/" + hall +"/"+floor +".pdf"
    print(directory_path)
    if hall == "Wendell B" or hall == "Wendell C":
        hall = "Wendell"
    if hall == "Baker S" or hall == "Baker E":
        hall = "Baker"
    return flask.render_template('NewTab.html', filepath=directory_path, hall=hall, room=room)


@app.route('/search', methods=['GET'])
def searchHall():
    return handle_room_query('searchHall.html', availables_matter=True)

@app.route('/browsing', methods=['GET'])
def justBrowsing():
    return handle_room_query('justBrowsing.html', availables_matter=False)

@app.route('/rate-room', methods=['POST'])
def rate_room():
    username = auth.authenticate()
    room_id = flask.request.form.get('room_id')
    rating = int(flask.request.form.get('rating'))

    try:
        with psycopg2.connect(DATABASE) as conn:
            cursor = conn.cursor()

            # add or change rating
            cursor.execute("""
                INSERT INTO ratings (user_id, room_id, ratings)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, room_id) DO UPDATE
                SET ratings = EXCLUDED.ratings
            """, (username, room_id, rating))

            conn.commit()

        return flask.jsonify({'success': True, 'message': 'Rating submitted successfully.'})

    except Exception as e:
        return flask.jsonify({'success': False, 'message': "could not submit rating."}), 500



@app.route('/average-rating', methods=['GET'])
def average_rating():
    username = auth.authenticate()
    room_id = flask.request.args.get('room_id')
    try:
        with psycopg2.connect(DATABASE) as conn:
            #get group_id
            cursor = conn.cursor()
            cursor.execute("""
                    SELECT group_id FROM members WHERE user_id = %s
                """, (username,))
            group_id = cursor.fetchone()
            #get members
            cursor.execute("""SELECT user_id
                FROM members
                WHERE group_id = %s
            """, (group_id,))
            members = cursor.fetchall()
            ratings = []

            for member in members:
                user_id = member[0]
                #print(user_id, room_id)
                cursor.execute("""
                    SELECT ratings
                    FROM ratings
                    WHERE user_id = %s AND room_id = %s
                """, (user_id, room_id))
                
                rating = cursor.fetchone()
                #print("RATING:", rating)
                if rating:
                    ratings.append(rating[0])

            if ratings:
                average = sum(ratings) / len(ratings)
            else:
                average = 0
        return flask.jsonify({'success': True, 'average_rating': round(average, 2) if average else 'N/A'}), 200 
    except Exception as e:
        return flask.jsonify({'success': False, 'message': "could not get average rating."}), 500


@app.route('/get-rating', methods=['GET'])
def get_rating():
    user_id = auth.authenticate()
    room_id = flask.request.args.get('room_id')
    
    try:
        with psycopg2.connect(DATABASE) as conn:
            cursor = conn.cursor()

            # Query to get the user's rating for the specific room
            cursor.execute("""
                SELECT ratings
                FROM ratings
                WHERE room_id = %s AND user_id = %s
            """, (room_id, user_id))

            rating = cursor.fetchone()

        if rating:
            return flask.jsonify({'success': True, 'rating': rating[0]})
        else:
            return flask.jsonify({'success': False, 'message': 'No rating found for this room.'})
    except Exception as e:
        return flask.jsonify({'success': False, 'message': str(e)}), 500



def handle_room_query(template_name, availables_matter):
    username = auth.authenticate()
    sort_param = flask.request.args.get("sort", "Sqft DESC")  # Default sort if not provided

    halls = {
            '1967': "Butler College",
            '1976': "Butler College",
            'Bloomberg': "Butler College",
            'Bogle': "Butler College",
            'Scully': "Butler College",
            'Wilf': "Butler College",
            'Yoseloff': "Butler College",
            '99Alexander': "Forbes College",
            'Annex': "Forbes College",
            'Main': "Forbes College",
            'Blair': "Mathey College",
            'Campbell-Mathey': "Mathey College",
            'Edwards': "Mathey College",
            'Joline': "Mathey College",
            'Little-Mathey': "Mathey College",
            'Hamilton': "Mathey College", 
            'Addy': "New College West",
            'Jose Feliciano': "New College West",
            'Aliya Kanji': "New College West",
            'Kwanza Jones': "New College West",
            'Buyers': "Rockefeller College",
            'Campbell-Rocky': "Rockefeller College",
            'Holder': "Rockefeller College",
            'Witherspoon': "Rockefeller College",
            '1901': "Upperclass",
            'Feinberg': "Upperclass",
            'Patton': "Upperclass",
            '1903': "Upperclass",
            'Foulke': "Upperclass",
            'Pyne': "Upperclass",
            'Brown': "Upperclass",
            'Henry': "Upperclass",
            'Scully': "Upperclass",
            'Cuyler': "Upperclass",
            'Laughlin': "Upperclass",
            'Spelman': "Upperclass",
            'Dickinson Street, 2': "Upperclass",
            'Little-Upperclass': "Upperclass",
            'Walker': "Upperclass",
            'Dod': "Upperclass",
            'Lockhart': "Upperclass",
            'Wright': "Upperclass",
            '1981': "Whitman College",
            'Baker': "Whitman College",
            'Fisher': "Whitman College",
            'Hargadon': "Whitman College",
            'Lauritzen': "Whitman College",
            'Murley': "Whitman College",
            'Wendell': "Whitman College",
            'Fu': "Yeh College",
            'Grousbeck': "Yeh College",
            'Hariri': "Yeh College",
            'Mannion': "Yeh College",
        }

    selected_halls = []
    selected_colleges = []
    cookies_halls = []

    for hall, college in halls.items():
        if flask.request.args.get(hall):
            if hall == "Little-Mathey" or hall == "Little-Upperclass":
                selected_halls.append("Little")
                selected_colleges.append(college)
            if hall == "Campbell-Mathey" or hall == "Campbell-Rocky":
                selected_halls.append("Campbell")
                selected_colleges.append(college)
            else:
                selected_halls.append(hall)
                selected_colleges.append(college)
            cookies_halls.append(hall)
    
    if not selected_halls:
        for hall, college in halls.items():
            if flask.request.cookies.get(hall):
                if hall == "Little-Mathey" or hall == "Little-Upperclass":
                    selected_halls.append("Little")
                    selected_colleges.append(college)
                if hall == "Campbell-Mathey" or hall == "Campbell-Rocky":
                    selected_halls.append("Campbell")
                    selected_colleges.append(college)
                else:
                    selected_halls.append(hall)
                    selected_colleges.append(college)
                cookies_halls.append(hall)

    # Retrieve room type filters
    types = [
        ("SINGLE", "SINGLE"), ("DOUBLE", "DOUBLE"), ("TRIPLE", "TRIPLE"),
        ("QUAD", "QUAD"), ("QUINT", "QUINT"), ("6PERSON", "6PERSON")
    ]

    selected_types = [type_name for arg_name, type_name in types if flask.request.args.get(arg_name)]
    if not selected_types:
        selected_types = [type_name for arg_name, type_name in types if flask.request.cookies.get(arg_name)]

    # Build SQL query with filters and sorting
    query = """
        SELECT DISTINCT rooms.*,
        CASE WHEN favorites.user_id IS NOT NULL THEN 1 ELSE 0 END AS is_favorite
        FROM rooms
        JOIN availables ON rooms.roomid = availables.room_id
        LEFT JOIN favorites ON rooms.RoomID = favorites.room_id AND favorites.user_id = %s
        """

    # search page only shows rooms that are still available
    if availables_matter:
        query += "WHERE availables.user_id = %s"
        params = [username, username]

    # just browsing page shows all rooms
    else:
        query += "WHERE 1=1"
        params = [username]

    if selected_colleges:
        placeholder = ', '.join(['%s'] * len(selected_colleges))
        query += f" AND College IN ({placeholder})"
        params.extend(selected_colleges)
    if selected_types:
        placeholder = ', '.join(['%s'] * len(selected_types))
        query += f" AND Type IN ({placeholder})"
        params.extend(selected_types)
    if selected_halls:
        placeholder = ', '.join(['%s'] * len(selected_halls))
        query += f" AND hall IN ({placeholder})"
        params.extend(selected_halls)
    if sort_param:
        query += f" ORDER BY {sort_param}"
    
    # Execute query and fetch results
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    # Convert results to dictionary format
    column_names = [description[0] for description in cursor.description]
    rooms = [dict(zip(column_names, row)) for row in results]
    cursor.close()
    results = len(rooms)

    # Create response with updated cookies
    response = flask.make_response(flask.render_template(template_name, results=rooms, Sort=sort_param,
                 selected_colleges = selected_colleges, selected_types = selected_types, 
                 selected_halls=cookies_halls, check_all=selected_colleges, number=results))
    response.set_cookie("First Sort", sort_param)

    
    for arg_name, _ in types:
        if arg_name in selected_types:
            response.set_cookie(arg_name, '1', max_age=60*60*24*30)
        else:
            response.set_cookie(arg_name, '0', max_age=0)

    for hall, college in halls.items():
        if hall in cookies_halls:
            response.set_cookie(hall, '1', max_age=60*60*24*30)
        else:
            response.set_cookie(hall, '0', max_age=0)
        if college in selected_colleges:
            response.set_cookie(college, '1', max_age=60*60*24*30)
        else:
            response.set_cookie(college, '0', max_age=0)

    return response


@app.route('/name', methods=['GET'])
def name():    
    username = auth.authenticate()
    name = checkNetid.main(username)
    if name:
        return flask.jsonify({'success': True, 'name': name}), 200 
    