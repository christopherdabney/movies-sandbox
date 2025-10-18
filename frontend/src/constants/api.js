// src/constants/api.js
const API_BASE_URL = 'http://localhost:5000';

export const API_ENDPOINTS = {
  MEMBER: {
    REGISTER: `${API_BASE_URL}/member/register`,
    LOGIN: `${API_BASE_URL}/member/login`, 
    LOGOUT: `${API_BASE_URL}/member/logout`,
    ACCOUNT: `${API_BASE_URL}/member`,
    VERIFY: `${API_BASE_URL}/member/verify-email`,
    RESEND: `${API_BASE_URL}/member/resend-verification`,
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
    OVERVIEW: `${API_BASE_URL}/watchlist/overview`,
  },
  CHAT: {
    MESSAGE: `${API_BASE_URL}/chat/message`,
    HISTORY: `${API_BASE_URL}/chat/history`,
    CLEAR: `${API_BASE_URL}/chat/clear`,
  }
};