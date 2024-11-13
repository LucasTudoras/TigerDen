import sqlite3

def create_tables():
    conn = sqlite3.connect('rooms.db')
    cursor = conn.cursor()

    # Create the favorites table if it doesn't already exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            user_id TEXT,
            room_id TEXT,
            PRIMARY KEY (user_id, room_id),
            FOREIGN KEY (room_id) REFERENCES rooms(id)
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()