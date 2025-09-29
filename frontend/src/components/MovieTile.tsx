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
  poster_url?: string;
  imdb_rating?: number;
}

interface MovieTileProps {
  movie: Movie;
}

const MovieTile: React.FC<MovieTileProps> = ({ movie }) => {
  const initials = movie.title.split(' ')
    .map(word => word[0])
    .join('')
    .slice(0, 3)
    .toUpperCase();

  console.log(movie.poster_url);

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