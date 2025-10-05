import { Movie } from './Movie';

export interface WatchlistItem {
  id: number;
  memberId: number;
  movieId: number;
  status: string;
  addedAt: string;
  watchedAt: string | null;
  movie: Movie;
}

export interface WatchlistResponse {
  watchlist: WatchlistItem[];
  count: number;
}