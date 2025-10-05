import React from 'react';
import { useNavigate } from 'react-router-dom';
import type { Movie } from '../types';
import '../styles/MovieRecommendationTile.css';

interface MovieRecommendationTileProps {
  movie: Movie;
  reason?: string;
}

const MovieRecommendationTile: React.FC<MovieRecommendationTileProps> = ({ movie, reason }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/movies/${movie.id}`);
  };

  const initials = movie.title.split(' ')
    .map(word => word[0])
    .join('')
    .slice(0, 3)
    .toUpperCase();

  return (
    <div className="movie-recommendation-tile" onClick={handleClick}>
      <div className="recommendation-poster">
        {movie.poster_url ? (
          <img src={movie.poster_url} alt={`${movie.title} poster`} />
        ) : (
          <div className="recommendation-poster-placeholder">
            <div className="recommendation-initials">{initials}</div>
          </div>
        )}
      </div>
      <div className="recommendation-info">
        <div className="recommendation-title">{movie.title}</div>
        <div className="recommendation-meta">{movie.genre}, {movie.release_year}</div>
        {reason && <div className="recommendation-reason">"{reason}"</div>}
      </div>
    </div>
  );
};

export default MovieRecommendationTile;