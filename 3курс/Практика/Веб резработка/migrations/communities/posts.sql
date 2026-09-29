CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    event_id INTEGER REFERENCES events(id) ON DELETE CASCADE,
    status NOT NULL CHECK IN ("deleted","posted","banned"),
    creator_id INTEGER REFERENCES events(id) ON DELETE CASCADE,
    community_id INTEGER REFERENCES communities(id),
    lifespan,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);