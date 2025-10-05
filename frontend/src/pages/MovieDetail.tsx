import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { API_ENDPOINTS } from '../constants/api';
import type { RootState } from '../store/store';
import type { Movie } from '../types';
import LoginPrompt from '../components/LoginPrompt';
import '../styles/MovieDetail.css';

const MovieDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { account } = useSelector((state: RootState) => state.account);
  const [movie, setMovie] = useState<Movie | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showLoginPrompt, setShowLoginPrompt] = useState(false);

  useEffect(() => {
    fetchMovie();
  }, [id]);

  const fetchMovie = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.MOVIES.DETAIL(id), {
        credentials: 'include',
      });
      
      if (!response.ok) throw new Error('Movie not found');
      
      const data = await response.json();
      setMovie(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load movie');
    } finally {
      setLoading(false);
    }
  };

  const handleAddToWatchlist = async () => {
    if (!account) {
      setShowLoginPrompt(true);
      return;
    }

    try {
      const response = await fetch(API_ENDPOINTS.WATCHLIST.ADD, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ movieId: movie?.id }),
      });

      if (!response.ok) {
        throw new Error('Failed to add to watchlist');
      }
      window.dispatchEvent(new CustomEvent('watchlist-changed'));
      
      fetchMovie(); // Refresh to show updated watchlist status
    } catch (err) {
      console.error('Error adding to watchlist:', err);
    }
  };

  const handleRemoveFromWatchlist = async () => {
    if (!account) {
      setShowLoginPrompt(true);
      return;
    }

    try {
      const response = await fetch(API_ENDPOINTS.WATCHLIST.REMOVE(movie.id), {
        method: 'DELETE',
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to remove from watchlist');
      }
      window.dispatchEvent(new CustomEvent('watchlist-changed'));

      fetchMovie(); // Refresh to show updated watchlist status
    } catch (err) {
      console.error('Error removing from watchlist:', err);
    }
  };

  if (loading) return <div className="movie-detail-container"><div className="loading-text">Loading...</div></div>;
  if (error) return <div className="movie-detail-container"><div className="error-text">{error}</div></div>;
  if (!movie) return <div className="movie-detail-container"><div className="error-text">Movie not found</div></div>;

  const initials = movie.title.split(' ').map(w => w[0]).join('').slice(0, 3).toUpperCase();

  return (
    <div className="movie-detail-container">
      <button onClick={() => navigate(-1)} className="back-btn">← Back</button>
      
      <div className="movie-detail-content">
        <div className="movie-detail-poster">
          {movie.poster_url ? (
            <img src={movie.poster_url} alt={`${movie.title} poster`} />
          ) : (
            <div className="poster-placeholder">
              <div className="poster-initials">{initials}</div>
            </div>
          )}
        </div>

        <div className="movie-detail-info">
          <h1>{movie.title}</h1>
          <div className="movie-meta">
            <span>{movie.release_year}</span>
            <span>•</span>
            <span>{movie.runtime_minutes} min</span>
            <span>•</span>
            <span>{movie.rating}</span>
            {movie.imdb_rating && (
              <>
                <span>•</span>
                <span>⭐ {movie.imdb_rating}</span>
              </>
            )}
          </div>
          
          <p className="movie-genre">{movie.genre}</p>
          <p className="movie-director">Directed by {movie.director}</p>
          
          <p className="movie-description">{movie.description}</p>

          {!movie.inWatchlist && (
            <button onClick={handleAddToWatchlist} className="add-btn">
              + Add to Watchlist
            </button>
          )}
          
          {movie.inWatchlist && (
            <div className="watchlist-actions">
              <div className="watchlist-status">
                {movie.watchlistStatus === 'watched' ? '✓ Watched' : 'In Watchlist'}
              </div>
              <button onClick={handleRemoveFromWatchlist} className="remove-btn">
                Remove
              </button>
            </div>
          )}
        </div>
      </div>

      {showLoginPrompt && <LoginPrompt onClose={() => setShowLoginPrompt(false)} />}
    </div>
  );
};

export default MovieDetail;