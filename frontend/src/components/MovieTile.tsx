// MovieTile.tsx
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
  imdb_rating?: number;
}

interface MovieTileProps {
  movie: Movie;
}

const MovieTile: React.FC<MovieTileProps> = ({ movie }) => {
  // Generate initials for placeholder poster
  const initials = movie.title.split(' ')
    .map(word => word[0])
    .join('')
    .slice(0, 3)
    .toUpperCase();

  return (
    <div className="movie-tile">
      <div className="movie-poster-placeholder">
        <div className="movie-initials">{initials}</div>
      </div>
      <div className="movie-info">
        <h3 className="movie-title">{movie.title}</h3>
        <p className="movie-details">
          {movie.genre} ({movie.release_year})
        </p>
        <p className="movie-rating">
          Rating: {movie.imdb_rating ? movie.imdb_rating.toFixed(1) : 'N/A'}
        </p>
      </div>
    </div>
  );
};

export default MovieTile;