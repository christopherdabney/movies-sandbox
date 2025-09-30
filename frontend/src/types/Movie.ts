export interface Movie {
  id: number;
  title: string;
  director: string;
  release_year: number;
  genre: string;
  description: string;
  runtime_minutes: number;
  rating: string;
  poster_url?: string;
  imdb_rating?: number;
  inWatchlist?: boolean;
}

export interface MoviesResponse {
  movies: Movie[];
  page: number;
  per_page: number;
  total_count: number;
  total_pages: number;
}