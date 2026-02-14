import { useState } from "react";
import { toast } from "sonner";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../lib/api";
import { MediaCard } from "../components/MediaCard";
import { MediaDetailModal } from "../components/MediaDetailModal";
import { AddMediaDialog } from "../components/AddMediaDialog";
import { Input } from "../components/ui/Input";
import { Button } from "../components/ui/Button";
import { Card, CardContent } from "../components/ui/Card";
import { Search as SearchIcon } from "lucide-react";
import type { MediaType } from "../types";

export function Search() {
  const { user } = useAuth();
  const [query, setQuery] = useState("");
  const [mediaType, setMediaType] = useState<MediaType>("anime");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [adding, setAdding] = useState<number | null>(null);
  const [showDialog, setShowDialog] = useState(false);
  const [selectedMedia, setSelectedMedia] = useState<any>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [detailMedia, setDetailMedia] = useState<any>(null);

  const mediaTypes: { value: MediaType; label: string }[] = [
    { value: "movie", label: "Movies" },
    { value: "series", label: "Series" },
    { value: "anime", label: "Anime" },
    { value: "manga", label: "Manga" },
    { value: "book", label: "Books" },
    { value: "game", label: "Games" },
  ];

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      let response;
      switch (mediaType) {
        case "movie":
          response = await api.searchMovies(query);
          break;
        case "series":
          response = await api.searchSeries(query);
          break;
        case "anime":
          response = await api.searchAnime(query);
          break;
        case "manga":
          response = await api.searchManga(query);
          break;
        case "book":
          response = await api.searchBooks(query);
          break;
        case "game":
          response = await api.searchGames(query);
          break;
      }
      // Normalize results to have consistent fields
      const normalizedResults = response.results.map((result: any) => normalizeExternalMedia(result));
      setResults(normalizedResults);
    } catch (error) {
      console.error("Search failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const normalizeExternalMedia = (external: any) => {
    // Normalize external API response to have consistent field names
    const normalized: any = { ...external };

    // Normalize title
    if (!normalized.title && normalized.name) {
      normalized.title = normalized.name;
    }

    // Normalize cover image
    if (!normalized.cover_image_url) {
      if (external.poster_path) {
        // TMDB - use original quality
        normalized.cover_image_url = `https://image.tmdb.org/t/p/original${external.poster_path}`;
      } else if (external.images?.jpg?.large_image_url) {
        // Jikan
        normalized.cover_image_url = external.images.jpg.large_image_url;
      } else if (external.cover?.url) {
        // IGDB
        normalized.cover_image_url = `https:${external.cover.url}`;
      } else if (external.cover_i) {
        // Open Library
        normalized.cover_image_url = `https://covers.openlibrary.org/b/id/${external.cover_i}-L.jpg`;
      }
    }

    return normalized;
  };

  const handleAddToList = (externalMedia: any, index: number) => {
    setSelectedMedia({ data: externalMedia, index });
    setShowDialog(true);
  };

  const handleConfirmAdd = async (trackingData: any) => {
    if (!user || !selectedMedia) return;

    const { data: externalMedia, index } = selectedMedia;
    setAdding(index);
    setShowDialog(false);

    try {
      // Step 1: Convert external API data using backend conversion
      let convertedData;
      switch (mediaType) {
        case "movie":
          convertedData = await api.convertMovie(externalMedia);
          break;
        case "series":
          convertedData = await api.convertSeries(externalMedia);
          break;
        case "anime":
          convertedData = await api.convertAnime(externalMedia);
          break;
        case "manga":
          convertedData = await api.convertManga(externalMedia);
          break;
        case "book":
          convertedData = await api.convertBook(externalMedia);
          break;
        case "game":
          convertedData = await api.convertGame(externalMedia);
          break;
        default:
          throw new Error("Invalid media type");
      }

      // Step 2: Create media from converted data
      let createdMedia;
      switch (mediaType) {
        case "movie":
          createdMedia = await api.createMovie(convertedData);
          break;
        case "series":
          createdMedia = await api.createSeries(convertedData);
          break;
        case "anime":
          createdMedia = await api.createAnime(convertedData);
          break;
        case "manga":
          createdMedia = await api.createManga(convertedData);
          break;
        case "book":
          createdMedia = await api.createBook(convertedData);
          break;
        case "game":
          createdMedia = await api.createGame(convertedData);
          break;
        default:
          throw new Error("Invalid media type");
      }

      // Step 3: Create tracking entry with user-provided data
      await api.createTracking({
        media_id: createdMedia.id,
        media_type: mediaType,
        ...trackingData,
      });

      toast.success(`Added "${externalMedia.title || externalMedia.name}" to your list!`);
    } catch (error: any) {
      console.error("Failed to add to list:", error);
      const errorMsg = error.message || "Failed to add to list";
      toast.error(errorMsg);
    } finally {
      setAdding(null);
      setSelectedMedia(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Search</h1>
        <p className="text-muted-foreground mt-1">
          Search for media from external sources
        </p>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 flex gap-2">
              <Input
                placeholder="Search for media..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                className="flex-1"
              />
              <Button onClick={handleSearch} disabled={loading}>
                <SearchIcon className="w-4 h-4 mr-2" />
                {loading ? "Searching..." : "Search"}
              </Button>
            </div>
          </div>

          <div className="flex gap-2 mt-4 flex-wrap">
            {mediaTypes.map((type) => (
              <Button
                key={type.value}
                variant={mediaType === type.value ? "default" : "outline"}
                size="sm"
                onClick={() => setMediaType(type.value)}
              >
                {type.label}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {results.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-4">
            Results ({results.length})
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {results.map((result, index) => (
              <MediaCard
                key={index}
                media={result}
                onAddToList={() => handleAddToList(result, index)}
                onClick={() => {
                  setDetailMedia(result);
                  setShowDetailModal(true);
                }}
                adding={adding === index}
              />
            ))}
          </div>
        </div>
      )}

      <MediaDetailModal
        media={detailMedia}
        tracking={null}
        onClose={() => {
          setShowDetailModal(false);
          setDetailMedia(null);
        }}
        isOpen={showDetailModal}
      />

      <AddMediaDialog
        media={selectedMedia?.data || null}
        onConfirm={handleConfirmAdd}
        onCancel={() => {
          setShowDialog(false);
          setSelectedMedia(null);
        }}
        isOpen={showDialog}
      />
    </div>
  );
}
