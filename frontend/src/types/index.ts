export type MediaType = "movie" | "series" | "anime" | "manga" | "book" | "game";

export type TrackingStatus = "planned" | "in_progress" | "completed" | "dropped" | "on_hold";

export type MediaStatus = "airing" | "finished" | "upcoming" | "cancelled";

export type AgeRating = "G" | "PG" | "PG-13" | "R" | "R+" | "Rx" | "NC-17" | "Unknown";

export type Platform = "PC" | "PlayStation" | "Xbox" | "Nintendo" | "Mobile" | "Other";

export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

export interface Media {
  id: number;
  media_type: MediaType;
  title: string;
  description?: string;
  release_date?: string;
  cover_image_url?: string;
  external_id?: string;
  external_source?: string;
  is_custom: boolean;
  tags?: string[];
  created_by_id?: number;
}

export interface Movie extends Media {
  media_type: "movie";
  runtime?: number;
  director?: string;
}

export interface Series extends Media {
  media_type: "series";
  total_episodes?: number;
  total_seasons?: number;
  status?: MediaStatus;
}

export interface Anime extends Media {
  media_type: "anime";
  original_title?: string;
  total_episodes?: number;
  studios?: string[];
  status?: MediaStatus;
  age_rating?: AgeRating;
}

export interface Manga extends Media {
  media_type: "manga";
  original_title?: string;
  total_chapters?: number;
  total_volumes?: number;
  authors?: string[];
  status?: MediaStatus;
  age_rating?: AgeRating;
}

export interface Book extends Media {
  media_type: "book";
  author?: string;
  isbn?: string;
  pages?: number;
  publisher?: string;
}

export interface Game extends Media {
  media_type: "game";
  platforms?: Platform[];
  developer?: string;
  publisher?: string;
}

export type AnyMedia = Movie | Series | Anime | Manga | Book | Game;

export interface Tracking {
  id: number;
  user_id: number;
  media_id: number;
  media_type: MediaType;
  status: TrackingStatus;
  rating?: number;
  progress: number;
  start_date?: string;
  end_date?: string;
  favorite: boolean;
  notes?: string;
  media?: AnyMedia;
}

export interface TrackingCreate {
  media_id: number;
  media_type: MediaType;
  status: TrackingStatus;
  rating?: number;
  progress?: number;
  start_date?: string;
  end_date?: string;
  favorite?: boolean;
  notes?: string;
}

export interface TrackingUpdate {
  status?: TrackingStatus;
  rating?: number;
  progress?: number;
  start_date?: string;
  end_date?: string;
  favorite?: boolean;
  notes?: string;
}

export interface TrackingStats {
  total: number;
  completed: number;
  in_progress: number;
  plan_to_watch: number;
  dropped: number;
  on_hold: number;
  favorites: number;
  average_rating: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface MediaUpdate {
  title?: string;
  description?: string;
  release_date?: string;
  cover_image_url?: string;
  tags?: string[];
}

export interface MovieUpdate extends MediaUpdate {
  runtime?: number;
  director?: string;
}

export interface SeriesUpdate extends MediaUpdate {
  total_episodes?: number;
  total_seasons?: number;
  status?: MediaStatus;
}

export interface AnimeUpdate extends MediaUpdate {
  original_title?: string;
  total_episodes?: number;
  studios?: string[];
  status?: MediaStatus;
  age_rating?: AgeRating;
}

export interface MangaUpdate extends MediaUpdate {
  original_title?: string;
  total_chapters?: number;
  total_volumes?: number;
  authors?: string[];
  status?: MediaStatus;
  age_rating?: AgeRating;
}

export interface BookUpdate extends MediaUpdate {
  author?: string;
  isbn?: string;
  pages?: number;
  publisher?: string;
}

export interface GameUpdate extends MediaUpdate {
  platforms?: Platform[];
  developer?: string;
  publisher?: string;
}

export type AnyMediaUpdate =
  | MovieUpdate
  | SeriesUpdate
  | AnimeUpdate
  | MangaUpdate
  | BookUpdate
  | GameUpdate;

export interface Token {
  access_token: string;
  token_type: string;
}
