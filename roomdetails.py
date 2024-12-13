def get_room_details(username, roomID, get_db):
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

    return room