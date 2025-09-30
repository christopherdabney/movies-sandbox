// src/constants/api.js
const API_BASE_URL = 'http://localhost:5000';

export const API_ENDPOINTS = {
  MEMBER: {
    REGISTER: `${API_BASE_URL}/member/register`,
    LOGIN: `${API_BASE_URL}/member/login`, 
    LOGOUT: `${API_BASE_URL}/member/logout`,
    ACCOUNT: `${API_BASE_URL}/member`,
  },
  MOVIES: {
    LIST: `${API_BASE_URL}/movies`,
    DETAIL: (id) => `${API_BASE_URL}/movies/${id}`,
    GENRES: `${API_BASE_URL}/movies/genres`,
  },
  WATCHLIST: {
    LIST: `${API_BASE_URL}/watchlist`,
    ADD: `${API_BASE_URL}/watchlist`,
    REMOVE: (id) => `${API_BASE_URL}/watchlist/${id}`,
    UPDATE: (id) => `${API_BASE_URL}/watchlist/${id}`,
  }
};