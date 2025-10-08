import type { Movie } from './Movie';

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

// Enum for valid backend watchlist status values
export enum WatchlistStatus {
  QUEUED = 'queued',
  WATCHED = 'watched',
}

// Constant object for using filter values in code
export const WatchlistFilterValue = {
  ALL: 'all',
  QUEUED: WatchlistStatus.QUEUED,
  WATCHED: WatchlistStatus.WATCHED,
} as const;

// Type for filter values (union of possible string values)
export type WatchlistFilter = typeof WatchlistFilterValue[keyof typeof WatchlistFilterValue];