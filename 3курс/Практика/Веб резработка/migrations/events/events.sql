CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    community_id INTEGER REFERENCES communities(id),
    description VARCHAR(607),
    location GEO DEFAULT KIROV,
    distance INTEGER,
    status VARCHAR(20) CHECK IN ("going""announced""tbgoing","ended")
    begin_date TIMESTAMP DEFAULT NULL,
    end_date TIMESTAMP DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);