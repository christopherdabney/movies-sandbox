import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../constants/api';
import MovieTile from '../components/MovieTile';
import '../styles/Movies.css';

interface Movie {
  id: number;
  title: string;
  director: string;
  release_year: number;
  genre: string;
  description: string;
  runtime_minutes: number;
  rating: string;
  imdb_id: string;
}

interface MoviesResponse {
  movies: Movie[];
  page: number;
  per_page: number;
  total_count: number;
  total_pages: number;
}

const Movies: React.FC = () => {
  const [moviesData, setMoviesData] = useState<MoviesResponse | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMovies = async (page: number, limit: number = 16) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_ENDPOINTS.MOVIES.LIST}?page=${page}&limit=${limit}`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch movies: ${response.status}`);
      }
      
      const data: MoviesResponse = await response.json();
      setMoviesData(data);
      setCurrentPage(page);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch movies');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMovies(1);
  }, []);

  const handlePreviousPage = () => {
    if (moviesData && currentPage > 1) {
      fetchMovies(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (moviesData && currentPage < moviesData.total_pages) {
      fetchMovies(currentPage + 1);
    }
  };

  if (loading) {
    return (
      <div className="movies-container">
        <div className="loading-state">
          <div className="loading-text">Loading movies...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="movies-container">
        <div className="error-state">
          <div className="error-text">Error: {error}</div>
        </div>
      </div>
    );
  }

  if (!moviesData) {
    return (
      <div className="movies-container">
        <div className="empty-state">
          <div className="empty-text">No movies found</div>
        </div>
      </div>
    );
  }

  return (
    <div className="movies-container">
      {/* Header with pagination info */}
      <div className="movies-header">
        <h1 className="movies-title">Classic Movies</h1>
        <div className="movies-count">
          Showing {moviesData.movies.length} of {moviesData.total_count} movies
        </div>
      </div>

      {/* Movie grid */}
      <div className="movies-grid">
        {moviesData.movies.map((movie) => (
          <MovieTile key={movie.id} movie={movie} />
        ))}
      </div>

      {/* Pagination controls */}
      <div className="pagination-controls">
        <button
          onClick={handlePreviousPage}
          disabled={currentPage === 1}
          className="pagination-btn"
        >
          ← Previous
        </button>
        
        <div className="page-info">
          Page {currentPage} of {moviesData.total_pages}
        </div>
        
        <button
          onClick={handleNextPage}
          disabled={currentPage === moviesData.total_pages}
          className="pagination-btn"
        >
          Next →
        </button>
      </div>
    </div>
  );
};

export default Movies;