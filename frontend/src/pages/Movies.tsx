import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { API_ENDPOINTS } from '../constants/api';
import type { RootState } from '../store/store';
import type { Movie, MoviesResponse } from '../types';
import MovieTile from '../components/MovieTile';
import LoginPrompt from '../components/LoginPrompt';
import '../styles/Movies.css';

const Movies: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { account } = useSelector((state: RootState) => state.account);
  
  // Read from URL
  const searchQuery = searchParams.get('search') || '';
  const genreFilter = searchParams.get('genre') || '';
  const currentPage = parseInt(searchParams.get('page') || '1');
  
  const [moviesData, setMoviesData] = useState<MoviesResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [initialLoad, setInitialLoad] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [genres, setGenres] = useState<string[]>([]);
  const [showLoginPrompt, setShowLoginPrompt] = useState(false);
  
  // Local state for debouncing search input
  const [searchInput, setSearchInput] = useState(searchQuery);

  // Fetch genres on mount
  useEffect(() => {
    fetch(API_ENDPOINTS.MOVIES.GENRES, { credentials: 'include' })
      .then(res => res.json())
      .then(data => setGenres(data.genres));
  }, []);

  // Debounce: Update URL params after user stops typing
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchInput !== searchQuery) {
        setSearchParams({
          search: searchInput,
          genre: genreFilter,
          page: '1'
        });
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchInput]);

  // Sync local input with URL (for back/forward navigation)
  useEffect(() => {
    setSearchInput(searchQuery);
  }, [searchQuery]);

  // Fetch movies when URL params change
  useEffect(() => {
    fetchMovies(currentPage, 24, searchQuery, genreFilter);
  }, [searchQuery, genreFilter, currentPage]);

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

  const handleGenreChange = (value: string) => {
    setSearchParams({
      search: searchQuery,
      genre: value,
      page: '1'
    });
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setSearchParams({
        search: searchQuery,
        genre: genreFilter,
        page: String(currentPage - 1)
      });
    }
  };

  const handleNextPage = () => {
    if (moviesData && currentPage < moviesData.total_pages) {
      setSearchParams({
        search: searchQuery,
        genre: genreFilter,
        page: String(currentPage + 1)
      });
    }
  };

  const handleFirstPage = () => {
    setSearchParams({
      search: searchQuery,
      genre: genreFilter,
      page: '1'
    });
  };

  const handleLastPage = () => {
    if (moviesData) {
      setSearchParams({
        search: searchQuery,
        genre: genreFilter,
        page: String(moviesData.total_pages)
      });
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
          value={genreFilter} 
          onChange={(e) => handleGenreChange(e.target.value)}
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
          onClick={handleFirstPage}
          disabled={currentPage === 1}
          className="pagination-btn"
        >
          ⏮ First
        </button>
        
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
        
        <button
          onClick={handleLastPage}
          disabled={currentPage === moviesData.total_pages}
          className="pagination-btn"
        >
          Last ⏭
        </button>
      </div>

      {showLoginPrompt && <LoginPrompt onClose={() => setShowLoginPrompt(false)} />}
    </div>
  );
};

export default Movies;