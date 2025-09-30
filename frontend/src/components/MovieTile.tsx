import React from 'react';
import type { Movie } from '../types';
import '../styles/MovieTile.css';

interface MovieTileProps {
  movie: Movie;
  onAddToWatchlist?: (movieId: number) => void;
  watchlistStatus?: string;
  onRemoveFromWatchlist?: (movieId: number) => void;
  onMarkAsWatched?: (movieId: number) => void;
}

const MovieTile: React.FC<MovieTileProps> = ({ 
  movie, 
  onAddToWatchlist,
  watchlistStatus,
  onRemoveFromWatchlist,
  onMarkAsWatched
}) => {
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
        {
            !movie.inWatchlist && onAddToWatchlist && (
            <button 
              className="add-to-watchlist-btn"
              onClick={() => onAddToWatchlist(movie.id)}
            >
              + Add to Watchlist
            </button>
        )}
        {onRemoveFromWatchlist && onMarkAsWatched && (
          <div className="watchlist-actions">
            <button 
              className="remove-btn"
              onClick={() => onRemoveFromWatchlist(movie.id)}
            >
              Remove
            </button>
            {watchlistStatus === 'queued' && (
              <button 
                className="mark-watched-btn"
                onClick={() => onMarkAsWatched(movie.id)}
              >
                Mark Watched
              </button>
            )}
            {watchlistStatus === 'watched' && (
              <span className="watched-badge">✓ Watched</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MovieTile;