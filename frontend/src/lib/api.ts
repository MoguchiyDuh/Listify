import type {
  User,
  LoginRequest,
  RegisterRequest,
  Token,
  AnyMedia,
  Tracking,
  TrackingCreate,
  TrackingUpdate,
  TrackingStats,
  MediaType,
  TrackingStatus,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const config: RequestInit = {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      credentials: "include", // Include cookies
    };

    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: "An error occurred",
      }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // Auth endpoints
  async register(data: RegisterRequest): Promise<User> {
    return this.request<User>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async login(data: LoginRequest): Promise<Token> {
    return this.request<Token>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async logout(): Promise<void> {
    return this.request<void>("/api/auth/logout", {
      method: "POST",
    });
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>("/api/auth/me");
  }

  // Media endpoints
  async getMovies(skip = 0, limit = 100): Promise<AnyMedia[]> {
    return this.request<AnyMedia[]>(`/api/media/movies?skip=${skip}&limit=${limit}`);
  }

  async createMovie(data: any): Promise<AnyMedia> {
    return this.request<AnyMedia>("/api/media/movies", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async createSeries(data: any): Promise<AnyMedia> {
    return this.request<AnyMedia>("/api/media/series", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async createAnime(data: any): Promise<AnyMedia> {
    return this.request<AnyMedia>("/api/media/anime", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async createManga(data: any): Promise<AnyMedia> {
    return this.request<AnyMedia>("/api/media/manga", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async createBook(data: any): Promise<AnyMedia> {
    return this.request<AnyMedia>("/api/media/books", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async createGame(data: any): Promise<AnyMedia> {
    return this.request<AnyMedia>("/api/media/games", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getSeries(skip = 0, limit = 100): Promise<AnyMedia[]> {
    return this.request<AnyMedia[]>(`/api/media/series?skip=${skip}&limit=${limit}`);
  }

  async getAnime(skip = 0, limit = 100): Promise<AnyMedia[]> {
    return this.request<AnyMedia[]>(`/api/media/anime?skip=${skip}&limit=${limit}`);
  }

  async getManga(skip = 0, limit = 100): Promise<AnyMedia[]> {
    return this.request<AnyMedia[]>(`/api/media/manga?skip=${skip}&limit=${limit}`);
  }

  async getBooks(skip = 0, limit = 100): Promise<AnyMedia[]> {
    return this.request<AnyMedia[]>(`/api/media/books?skip=${skip}&limit=${limit}`);
  }

  async getGames(skip = 0, limit = 100): Promise<AnyMedia[]> {
    return this.request<AnyMedia[]>(`/api/media/games?skip=${skip}&limit=${limit}`);
  }

  async searchMedia(query: string, mediaType?: MediaType, limit = 100): Promise<AnyMedia[]> {
    const params = new URLSearchParams({ q: query, limit: limit.toString() });
    if (mediaType) params.append("media_type", mediaType);
    return this.request<AnyMedia[]>(`/api/media/search?${params}`);
  }

  // External search endpoints
  async searchMovies(query: string, limit = 10): Promise<{ results: any[]; source: string }> {
    return this.request<{ results: any[]; source: string }>(
      `/api/search/movies?q=${encodeURIComponent(query)}&limit=${limit}`
    );
  }

  async searchSeries(query: string, limit = 10): Promise<{ results: any[]; source: string }> {
    return this.request<{ results: any[]; source: string }>(
      `/api/search/series?q=${encodeURIComponent(query)}&limit=${limit}`
    );
  }

  async searchAnime(query: string, limit = 10): Promise<{ results: any[]; source: string }> {
    return this.request<{ results: any[]; source: string }>(
      `/api/search/anime?q=${encodeURIComponent(query)}&limit=${limit}`
    );
  }

  async searchManga(query: string, limit = 10): Promise<{ results: any[]; source: string }> {
    return this.request<{ results: any[]; source: string }>(
      `/api/search/manga?q=${encodeURIComponent(query)}&limit=${limit}`
    );
  }

  async searchBooks(query: string, limit = 10): Promise<{ results: any[]; source: string }> {
    return this.request<{ results: any[]; source: string }>(
      `/api/search/books?q=${encodeURIComponent(query)}&limit=${limit}`
    );
  }

  async searchGames(query: string, limit = 10): Promise<{ results: any[]; source: string }> {
    return this.request<{ results: any[]; source: string }>(
      `/api/search/games?q=${encodeURIComponent(query)}&limit=${limit}`
    );
  }

  // Convert external API data to our schema
  async convertMovie(externalData: any): Promise<any> {
    return this.request<any>("/api/search/convert/movie", {
      method: "POST",
      body: JSON.stringify(externalData),
    });
  }

  async convertSeries(externalData: any): Promise<any> {
    return this.request<any>("/api/search/convert/series", {
      method: "POST",
      body: JSON.stringify(externalData),
    });
  }

  async convertAnime(externalData: any): Promise<any> {
    return this.request<any>("/api/search/convert/anime", {
      method: "POST",
      body: JSON.stringify(externalData),
    });
  }

  async convertManga(externalData: any): Promise<any> {
    return this.request<any>("/api/search/convert/manga", {
      method: "POST",
      body: JSON.stringify(externalData),
    });
  }

  async convertBook(externalData: any): Promise<any> {
    return this.request<any>("/api/search/convert/book", {
      method: "POST",
      body: JSON.stringify(externalData),
    });
  }

  async convertGame(externalData: any): Promise<any> {
    return this.request<any>("/api/search/convert/game", {
      method: "POST",
      body: JSON.stringify(externalData),
    });
  }

  // Tracking endpoints
  async getTracking(
    status?: TrackingStatus,
    mediaType?: MediaType,
    skip = 0,
    limit = 100
  ): Promise<Tracking[]> {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() });
    if (status) params.append("status", status);
    if (mediaType) params.append("media_type", mediaType);
    return this.request<Tracking[]>(`/api/tracking?${params}`);
  }

  async getTrackingById(userId: number, mediaId: number): Promise<Tracking> {
    return this.request<Tracking>(`/api/tracking/${userId}/${mediaId}`);
  }

  async createTracking(data: TrackingCreate): Promise<Tracking> {
    return this.request<Tracking>("/api/tracking", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateTracking(userId: number, mediaId: number, data: TrackingUpdate): Promise<Tracking> {
    return this.request<Tracking>(`/api/tracking/${mediaId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteTracking(userId: number, mediaId: number): Promise<void> {
    return this.request<void>(`/api/tracking/${mediaId}`, {
      method: "DELETE",
    });
  }

  async getTrackingStats(mediaType?: MediaType): Promise<TrackingStats> {
    const params = mediaType ? `?media_type=${mediaType}` : "";
    return this.request<TrackingStats>(`/api/tracking/statistics${params}`);
  }

  async getFavorites(mediaType?: MediaType, skip = 0, limit = 100): Promise<Tracking[]> {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() });
    if (mediaType) params.append("media_type", mediaType);
    return this.request<Tracking[]>(`/api/tracking/favorites?${params}`);
  }

  // Image upload
  async uploadImage(file: File): Promise<{ url: string }> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/api/media/upload-image`, {
      method: "POST",
      body: formData,
      credentials: "include",
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: "Upload failed",
      }));
      throw new Error(error.detail);
    }

    return response.json();
  }
}

export const api = new ApiClient();
