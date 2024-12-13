import psycopg2
import os
import checkNetid
from operator import itemgetter

DATABASE = os.environ['DATABASE_URL']

def get_favorites(user_id):
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
    
    return sorted(favorite_rooms, key=itemgetter('is_available'))

def get_groups(username):
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

            return {
                'user_has_group': user_has_group,
                'organized_groups': organized_groups,
                'group_favorite_rooms': group_favorite_rooms
            }
        
def create_new_group(username, group_name, netids):
    
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

    return valid_name_list, invalid_netid_list, already_in_group

def add_group_member(username, netids):
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

    return invalid_netid_list, already_in_group, valid_name_list

def leave_from_group(username):
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