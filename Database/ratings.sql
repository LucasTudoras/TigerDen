CREATE TABLE ratings (user_id TEXT, room_id TEXT, ratings INTEGER, PRIMARY KEY (user_id, room_id), FOREIGN KEY (room_id) REFERENCES rooms(roomid));