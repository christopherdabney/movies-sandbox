import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../constants/api';
import MovieTile from '../components/MovieTile';

import { useSelector } from 'react-redux';
import type { RootState } from '../store/store';
import LoginPrompt from '../components/LoginPrompt';

import type { Movie, MoviesResponse } from '../types';
import '../styles/Movies.css'; 

const Movies: React.FC = () => {
  const [moviesData, setMoviesData] = useState<MoviesResponse | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [initialLoad, setInitialLoad] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchInput, setSearchInput] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [genres, setGenres] = useState<string[]>([]);
  const [selectedGenre, setSelectedGenre] = useState('');
  const [showLoginPrompt, setShowLoginPrompt] = useState(false);
  const { account } = useSelector((state: RootState) => state.account);

  // Fetch genres on mount
  useEffect(() => {
    fetch(API_ENDPOINTS.MOVIES.GENRES, { credentials: 'include' })
      .then(res => res.json())
      .then(data => setGenres(data.genres));
  }, []);

  // Debounce effect - only updates debouncedSearch
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setDebouncedSearch(searchInput);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchInput]);

  // Reset to page 1 when search changes
  useEffect(() => {
    setCurrentPage(1);
  }, [debouncedSearch]);

  // Fetch effect - triggers on debouncedSearch or page change
  useEffect(() => {
    fetchMovies(currentPage, 24, debouncedSearch, selectedGenre);
  }, [debouncedSearch, currentPage, selectedGenre]);

  const fetchMovies = async (page: number, limit: number = 24, search: string = '', genre: string = '') => {
    setLoading(true);
    setError(null);
    
    try {
      const url = `${API_ENDPOINTS.MOVIES.LIST}?page=${page}&limit=${limit}&search=${encodeURIComponent(search)}&genre=${encodeURIComponent(genre)}`;
      const response = await fetch(url, {
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
      setInitialLoad(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch movies');
    } finally {
      setLoading(false);
    }
  };

  const handlePreviousPage = () => {
    if (moviesData && currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (moviesData && currentPage < moviesData.total_pages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const handleAddToWatchlist = async (movieId: number) => {
    if (!account) {
      setShowLoginPrompt(true);
      return;
    }

    try {
      const response = await fetch(API_ENDPOINTS.WATCHLIST.ADD, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ movieId }),
      });

      if (!response.ok) {
        throw new Error('Failed to add to watchlist');
      }

      setMoviesData(prevData => {
        if (!prevData) return prevData;
        
        return {
          ...prevData,
          movies: prevData.movies.map(movie => 
            movie.id === movieId 
              ? { ...movie, inWatchlist: true }
              : movie
          )
        };
      });
    } catch (err) {
      console.error('Error adding to watchlist:', err);
    }
  };

  if (loading && initialLoad) {
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
      <div className="movies-header">
        <input
          type="text"
          placeholder="Search movies..."
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          className="search-input"
        />
        <select 
          value={selectedGenre} 
          onChange={(e) => setSelectedGenre(e.target.value)}
          className="genre-select"
        >
          <option value="">All Genres</option>
          {genres.map(g => <option key={g} value={g}>{g}</option>)}
        </select>
        <div className="movies-count">
          Showing {moviesData.movies.length} of {moviesData.total_count} movies
          {loading && !initialLoad && <span> (searching...)</span>}
        </div>
      </div>

      <div className="movies-grid">
        {moviesData.movies.map((movie) => (
          <MovieTile
            key={movie.id}
            movie={movie}
            onAddToWatchlist={handleAddToWatchlist}
          />
        ))}
      </div>

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
      {showLoginPrompt && <LoginPrompt onClose={() => setShowLoginPrompt(false)} />}
    </div>
  );
};

export default Movies;