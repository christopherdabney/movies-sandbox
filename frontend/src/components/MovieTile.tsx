import React from 'react';

interface Movie {
  id: number;
  title: string;
  director: string;
  release_year: number;
  genre: string;
  description: string;
  runtime_minutes: number;
  rating: string;
  poster_url?: string;
  imdb_rating?: number;
}

interface MovieTileProps {
  movie: Movie;
}

const MovieTile: React.FC<MovieTileProps> = ({ movie, onAddToWatchlist }) => {
  const initials = movie.title.split(' ')
    .map(word => word[0])
    .join('')
    .slice(0, 3)
    .toUpperCase();

  return (
    <div className="movie-tile">
      {movie.poster_url ? (
        <img 
          src={movie.poster_url} 
          alt={`${movie.title} poster`}
          className="movie-poster"
        />
      ) : (
        <div className="movie-poster-placeholder">
          <div className="movie-initials">{initials}</div>
        </div>
      )}
      <div className="movie-info">
        <h3 className="movie-title">{movie.title}</h3>
        <p className="movie-year">{movie.release_year}</p>
        <p className="movie-genre">{movie.genre}</p>
        {movie.inWatchlist === false && (
            <button 
              className="add-to-watchlist-btn"
              onClick={() => onAddToWatchlist(movie.id)}
            >
              + Add to Watchlist
            </button>
          )}
      </div>
    </div>
  );
};

export default MovieTile;