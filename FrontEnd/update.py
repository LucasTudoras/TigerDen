import psycopg2
import PDF

def database_update(pdf_filepath, DATABASE_URL, user_id):
    rooms = PDF.main(pdf_filepath)
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            cursor = conn.cursor()

            query = """
                DELETE FROM availables
                WHERE user_id = %s;
                """
            cursor.execute(query, (user_id,))


            # this is horrible, remember to remove ignore and fix everything later
            query = """
                INSERT INTO availables (user_id, room_id) VALUES (%s, %s) ON CONFLICT (user_id, room_id) DO NOTHING;
                """
            
            for room in rooms:
                room_id = room['RoomID']
                cursor.execute(query, (user_id, room_id))


    except Exception as e:
        print(f"Error: {e}")

    return rooms
