CREATE TABLE IF NOT EXISTS member (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS movie (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    release_year INTEGER,
    runtime_minutes INTEGER,
    director VARCHAR(255),
    genre VARCHAR(100),
    rating VARCHAR(10),  -- 'PG', 'R', 'PG-13', etc.
    imdb_rating DECIMAL(3,1),  -- 7.5, 8.2, etc.
    poster_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS watchlist (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES member(id) ON DELETE CASCADE,
    movie_id INTEGER REFERENCES movie(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'queued',  -- 'queued', 'watched'
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    watched_at TIMESTAMP NULL,  -- Set when status changes to 'watched'
    UNIQUE(user_id, movie_id)
);