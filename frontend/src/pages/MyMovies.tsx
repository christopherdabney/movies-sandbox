import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../constants/api';
import MovieTile from '../components/MovieTile';
import type { WatchlistResponse, WatchlistFilter } from '../types/Watchlist';
import { WatchlistFilterValue } from '../types/Watchlist';

import '../styles/MyMovies.css';

const MyMovies: React.FC = () => {
  const [watchlistData, setWatchlistData] = useState<WatchlistResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<WatchlistFilter>(WatchlistFilterValue.ALL);

  const fetchWatchlist = async (status?: string) => {
    setLoading(true);
    setError(null);
    try {
      const url = status 
        ? `${API_ENDPOINTS.WATCHLIST.LIST}?status=${status}`
        : API_ENDPOINTS.WATCHLIST.LIST;
      const response = await fetch(url, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error(`Failed to fetch watchlist: ${response.status}`);
      }
      const data: WatchlistResponse = await response.json();
      setWatchlistData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch watchlist');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const handleFilterChange = (filter: WatchlistFilter) => {
    setActiveFilter(filter);
    if (filter === WatchlistFilterValue.ALL) {
      fetchWatchlist();
    } else {
      fetchWatchlist(filter);
    }
  };

  const handleRemoveFromWatchlist = async (movieId: number) => {
    try {
      const response = await fetch(API_ENDPOINTS.WATCHLIST.REMOVE(movieId), {
        method: 'DELETE',
        credentials: 'include',
      });
      if (!response.ok) {
        throw new Error('Failed to remove from watchlist');
      }
      setWatchlistData(prevData => {
        if (!prevData) return prevData;
        return {
          ...prevData,
          watchlist: prevData.watchlist.filter(item => item.movieId !== movieId),
          count: prevData.count - 1
        };
      });
      window.dispatchEvent(new CustomEvent('watchlist-changed'));
    } catch (err) {
      console.error('Error removing from watchlist:', err);
    }
  };

  const handleMarkAsWatched = async (movieId: number) => {
    try {
      const response = await fetch(API_ENDPOINTS.WATCHLIST.UPDATE(movieId), {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ status: WatchlistFilterValue.WATCHED }),
      });
      if (!response.ok) {
        throw new Error('Failed to update watchlist');
      }
      setWatchlistData(prevData => {
        if (!prevData) return prevData;
        return {
          ...prevData,
          watchlist: prevData.watchlist.map(item => 
            item.movieId === movieId 
              ? { ...item, status: WatchlistFilterValue.WATCHED, watchedAt: new Date().toISOString() }
              : item
          )
        };
      });
    } catch (err) {
      console.error('Error marking as watched:', err);
    }
  };

  if (loading) {
    return (
      <div className="my-movies-container">
        <div className="loading-state">
          <div className="loading-text">Loading your movies...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="my-movies-container">
        <div className="error-state">
          <div className="error-text">Error: {error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="my-movies-container">
      {/* Filter tabs */}
      <div className="filter-tabs">
        <button
          className={`filter-tab ${activeFilter === WatchlistFilterValue.ALL ? 'active' : ''}`}
          onClick={() => handleFilterChange(WatchlistFilterValue.ALL)}
        >
          All ({watchlistData?.count || 0})
        </button>
        <button
          className={`filter-tab ${activeFilter === WatchlistFilterValue.QUEUED ? 'active' : ''}`}
          onClick={() => handleFilterChange(WatchlistFilterValue.QUEUED)}
        >
          To Watch
        </button>
        <button
          className={`filter-tab ${activeFilter === WatchlistFilterValue.WATCHED ? 'active' : ''}`}
          onClick={() => handleFilterChange(WatchlistFilterValue.WATCHED)}
        >
          Watched
        </button>
      </div>
      {/* Movies grid */}
      {!watchlistData || watchlistData.count === 0 ? (
        <div className="empty-state">
          <div className="empty-text">
            {activeFilter === WatchlistFilterValue.ALL 
              ? "You haven't added any movies to your watchlist yet."
              : `No ${activeFilter} movies in your watchlist.`}
          </div>
        </div>
      ) : (
        <div className="movies-grid">
          {watchlistData.watchlist.map((item) => (
            <MovieTile
              key={item.movieId}
              movie={item.movie}
              watchlistStatus={item.status}
              onRemoveFromWatchlist={handleRemoveFromWatchlist}
              onMarkAsWatched={handleMarkAsWatched}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default MyMovies;