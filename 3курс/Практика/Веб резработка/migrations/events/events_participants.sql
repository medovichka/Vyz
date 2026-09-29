CREATE TABLE IF NOT EXISTS events_participants (
    event_id INTEGER REFERENCES events(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    commentary TEXT DEFAULT NULL,
    rating INTEGER CHECK IN ("1","2","3","4","5","6","7","8","9","10"),
    paricipated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);