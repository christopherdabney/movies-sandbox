-- Enum types
CREATE TYPE watchliststatus AS ENUM ('queued', 'watched');

-- Member table
CREATE TABLE IF NOT EXISTS member (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Movie table
CREATE TABLE IF NOT EXISTS movie (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    director VARCHAR(100),
    release_year INTEGER,
    genre VARCHAR(50),
    description TEXT,
    runtime_minutes INTEGER,
    rating VARCHAR(10),
    imdb_rating DECIMAL(3,1),
    poster_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Watchlist table
CREATE TABLE IF NOT EXISTS watchlist (
    id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES member(id) ON DELETE CASCADE,
    movie_id INTEGER NOT NULL REFERENCES movie(id) ON DELETE CASCADE,
    status watchliststatus NOT NULL DEFAULT 'queued',
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    watched_at TIMESTAMP NULL,
    UNIQUE(member_id, movie_id)
);

-- Chat message table
CREATE TABLE IF NOT EXISTS chat_message (
    id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES member(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    recommended_movie_ids INTEGER[],
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);