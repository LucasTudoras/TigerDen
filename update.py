import psycopg2
import PDF

def database_update(pdf_filepath, DATABASE_URL, user_id):
    rooms = PDF.main(pdf_filepath)

    # no rooms found
    if not rooms:
        return

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            cursor = conn.cursor()

            # wipe the availables table for the user
            query = """
                DELETE FROM availables
                WHERE user_id LIKE %s;
                """
            cursor.execute(query, (f"%{user_id}%",))
            conn.commit()

            query = """
                INSERT INTO availables (user_id, room_id) VALUES (%s, %s) ON CONFLICT (user_id, room_id) DO NOTHING;
                """
            
            # insert each room parsed from PDF.main back into the database for the user
            for room in rooms:
                room_id = room['RoomID']
                if room_id is None:
                    continue
                try:
                    cursor.execute(query, (user_id, room_id))
                except Exception as e:
                    print(f"error on {room_id}: {e}")

            print(f"{len(rooms)} inserted for {user_id}")

    except Exception as e:
        print(f"Error: {e}")

    return rooms
