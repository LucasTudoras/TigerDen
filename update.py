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

            # Get all valid room IDs from the rooms table
            cursor.execute("SELECT RoomID FROM rooms")
            valid_room_ids = set(row[0] for row in cursor.fetchall())

            # wipe the availables table for the user
            cursor.execute("""
                DELETE FROM availables
                WHERE user_id = %s;
            """, (user_id,))
            conn.commit()

            insert_query = """
                INSERT INTO availables (user_id, room_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id, room_id) DO NOTHING;
            """

            inserted_count = 0
            for room in rooms:
                room_id = room.get('RoomID')
                if not room_id:
                    continue
                if room_id not in valid_room_ids:
                    print(f"Skipping {room_id}: not found in rooms table")
                    continue
                try:
                    cursor.execute(insert_query, (user_id, room_id))
                    inserted_count += 1
                except Exception as e:
                    print(f"Error on {room_id}: {e}")

            conn.commit()
            print(f"{inserted_count} inserted for {user_id}")

    except Exception as e:
        print(f"Error: {e}")

    return rooms

