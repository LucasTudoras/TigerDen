import psycopg2
import PDF

def database_update(pdf_filepath, DATABASE_URL, user_id):
    rooms = PDF.main(pdf_filepath)
    if not rooms:
        print("no rooms parsed from uploaded PDF")
        rooms = []

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            cursor = conn.cursor()

            query = """
                DELETE FROM availables
                WHERE user_id = %s;
                """
            cursor.execute(query, (user_id,))
            conn.commit()

            # this is horrible, remember to remove ignore and fix everything later
            query = """
                INSERT INTO availables (user_id, room_id) VALUES (%s, %s);
                """
            
            for room in rooms:
                room_id = room['RoomID']
                if room_id is None:
                    continue
                try:
                    cursor.execute(query, (user_id, room_id))
                except Exception as e:
                    print(f"error on {room_id}: {e}")

            conn.commit()
            print(f"{len(rooms)} inserted for {user_id}")

    except Exception as e:
        print(f"Error: {e}")

    return rooms
