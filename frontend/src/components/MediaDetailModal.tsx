import { X, Calendar, Star } from "lucide-react";
import { Button } from "./ui/Button";
import type { AnyMedia, Tracking, Movie, Series, Anime, Manga, Book, Game } from "../types";
import { API_BASE_URL } from "../lib/api";

interface MediaDetailModalProps {
  media: AnyMedia | null;
  tracking?: Tracking | null;
  onClose: () => void;
  onEdit?: (tracking: Tracking) => void;
  onEditMedia?: (media: AnyMedia) => void;
  currentUserId?: number;
  isOpen: boolean;
}

export function MediaDetailModal({ media, tracking, onClose, onEdit, onEditMedia, currentUserId, isOpen }: MediaDetailModalProps) {
  if (!isOpen || !media) return null;

  // Handle both internal media and external API results
  const isExternalMedia = !(media as any).media_type;

  const imageUrl = isExternalMedia
    ? (media as any).cover_image_url ||
      ((media as any).poster_path ? `https://image.tmdb.org/t/p/original${(media as any).poster_path}` : null) ||
      ((media as any).images?.jpg?.large_image_url) ||
      ((media as any).cover?.url ? `https:${(media as any).cover.url}` : null) ||
      ((media as any).cover_i ? `https://covers.openlibrary.org/b/id/${(media as any).cover_i}-L.jpg` : null)
    : media.cover_image_url?.startsWith("/static")
      ? `${API_BASE_URL}${media.cover_image_url}`
      : media.cover_image_url;

  const getMediaDetails = () => {
    const details: { label: string; value: string }[] = [];

    // If external media, return empty for now
    if (isExternalMedia) return details;

    switch (media.media_type) {
      case "movie":
        const movie = media as Movie;
        if (movie.runtime) details.push({ label: "Runtime", value: `${movie.runtime} min` });
        if (movie.director) details.push({ label: "Director", value: movie.director });
        break;
      case "series":
        const series = media as Series;
        if (series.total_seasons) details.push({ label: "Seasons", value: `${series.total_seasons}` });
        if (series.total_episodes) details.push({ label: "Episodes", value: `${series.total_episodes}` });
        if (series.status) details.push({ label: "Media Status", value: series.status });
        break;
      case "anime":
        const anime = media as Anime;
        if (anime.total_episodes) details.push({ label: "Episodes", value: `${anime.total_episodes}` });
        if (anime.studios?.length) details.push({ label: "Studios", value: anime.studios.join(", ") });
        if (anime.status) details.push({ label: "Media Status", value: anime.status });
        if (anime.age_rating) details.push({ label: "Age Rating", value: anime.age_rating });
        break;
      case "manga":
        const manga = media as Manga;
        if (manga.total_volumes) details.push({ label: "Volumes", value: `${manga.total_volumes}` });
        if (manga.total_chapters) details.push({ label: "Chapters", value: `${manga.total_chapters}` });
        if (manga.authors?.length) details.push({ label: "Authors", value: manga.authors.join(", ") });
        if (manga.status) details.push({ label: "Media Status", value: manga.status });
        if (manga.age_rating) details.push({ label: "Age Rating", value: manga.age_rating });
        break;
      case "book":
        const book = media as Book;
        if (book.author) details.push({ label: "Author", value: book.author });
        if (book.pages) details.push({ label: "Pages", value: `${book.pages}` });
        if (book.publisher) details.push({ label: "Publisher", value: book.publisher });
        if (book.isbn) details.push({ label: "ISBN", value: book.isbn });
        break;
      case "game":
        const game = media as Game;
        if (game.platforms?.length) details.push({ label: "Platforms", value: game.platforms.join(", ") });
        if (game.developer) details.push({ label: "Developer", value: game.developer });
        if (game.publisher) details.push({ label: "Publisher", value: game.publisher });
        break;
    }

    return details;
  };

  const mediaDetails = getMediaDetails();

  const title = (media as any).title || (media as any).name || "Unknown";
  const description = (media as any).description || (media as any).synopsis || (media as any).summary || (media as any).overview;
  const originalTitle = (media as any).original_title || (media as any).title_japanese;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div
        className="bg-card border border-border rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header with close button */}
        <div className="sticky top-0 bg-card border-b border-border p-4 flex justify-between items-center z-10">
          <h2 className="text-2xl font-bold">{title}</h2>
          <Button variant="outline" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="p-6">
          {/* Image and all info */}
          <div className="flex gap-6">
            {/* Left: Cover Image */}
            <div className="w-80 shrink-0">
              <div className="relative">
                {imageUrl ? (
                  <img
                    src={imageUrl}
                    alt={title}
                    className="w-full rounded-lg shadow-lg"
                    onError={(e) => {
                      e.currentTarget.src = "https://via.placeholder.com/300x450?text=No+Image";
                    }}
                  />
                ) : (
                  <div className="w-full aspect-[2/3] bg-muted rounded-lg flex items-center justify-center">
                    No Image
                  </div>
                )}

                {/* Rating badge on image */}
                {tracking?.rating && (
                  <div className="absolute top-3 left-3 bg-background/95 rounded px-3 py-1.5 shadow-lg">
                    <span className="text-lg font-bold">⭐ {tracking.rating}</span>
                  </div>
                )}

                {/* Favorite badge on image */}
                {tracking?.favorite && (
                  <div className="absolute top-3 right-3 bg-yellow-500 rounded-full p-2 shadow-lg">
                    <Star className="w-5 h-5 text-white fill-current" />
                  </div>
                )}
              </div>
            </div>

            {/* Right: All Info */}
            <div className="flex-1 space-y-6">
              {/* Original Title */}
              {originalTitle && (
                <div>
                  <p className="text-sm text-muted-foreground">Original Title</p>
                  <p className="text-xl font-medium">{originalTitle}</p>
                </div>
              )}

              {/* Release Date */}
              {((media as any).release_date || (media as any).first_air_date || (media as any).aired?.from || (media as any).published?.from) && (
                <div className="flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-muted-foreground" />
                  <span className="text-base">
                    {(media as any).release_date || (media as any).first_air_date || (media as any).aired?.from?.split('T')[0] || (media as any).published?.from?.split('T')[0]}
                  </span>
                </div>
              )}

              {/* Type Tags */}
              <div className="flex gap-2 flex-wrap">
                {!isExternalMedia && (
                  <span className="bg-primary/20 text-primary px-3 py-1 rounded-full text-xs font-medium">
                    {media.media_type.toUpperCase()}
                  </span>
                )}
                {!isExternalMedia && media.is_custom && (
                  <span className="bg-blue-500/20 text-blue-500 px-3 py-1 rounded-full text-xs font-medium">
                    CUSTOM
                  </span>
                )}
              </div>

              {/* Genre/Theme Tags */}
              {!isExternalMedia && media.tags && media.tags.length > 0 && (
                <div>
                  <p className="text-sm text-muted-foreground mb-2">Genres & Tags</p>
                  <div className="flex gap-2 flex-wrap">
                    {media.tags.map((tag, idx) => (
                      <span key={idx} className="bg-muted px-3 py-1 rounded-full text-xs">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Edit Media Button - Only for custom media owned by user */}
              {!isExternalMedia && media.is_custom && media.created_by_id === currentUserId && onEditMedia && (
                <div>
                  <Button variant="outline" size="sm" onClick={() => onEditMedia(media)}>
                    Edit Media Details
                  </Button>
                </div>
              )}

              {/* Media Details */}
              {mediaDetails.length > 0 && (
                <div className="grid grid-cols-2 gap-4">
                  {mediaDetails.map((detail, idx) => (
                    <div key={idx}>
                      <p className="text-sm text-muted-foreground">{detail.label}</p>
                      <p className="text-base font-medium">{detail.value}</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Description */}
              {description && (
                <div>
                  <h3 className="text-lg font-semibold mb-2">Description</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {description}
                  </p>
                </div>
              )}

              {/* External Source */}
              {!isExternalMedia && media.external_source && (
                <div className="text-xs text-muted-foreground">
                  Source: {media.external_source.toUpperCase()}
                  {media.external_id && ` (ID: ${media.external_id})`}
                </div>
              )}
            </div>
          </div>

          {/* Tracking Info */}
          {tracking && (
            <div className="border-t mt-6 pt-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">Your Tracking</h3>
                <Button variant="outline" size="sm" onClick={() => onEdit?.(tracking)}>
                  Edit
                </Button>
              </div>

              {/* Tracking Status Tags */}
              <div className="flex gap-2 flex-wrap mb-4">
                <span className={`${
                  tracking.status === "completed" ? "bg-green-500/20 text-green-500" :
                  tracking.status === "in_progress" ? "bg-blue-500/20 text-blue-500" :
                  tracking.status === "planned" ? "bg-purple-500/20 text-purple-500" :
                  tracking.status === "on_hold" ? "bg-yellow-500/20 text-yellow-500" :
                  "bg-red-500/20 text-red-500"
                } px-3 py-1 rounded-full text-sm font-medium capitalize`}>
                  {tracking.status.replace("_", " ")}
                </span>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">

                {/* Progress */}
                <div>
                  <p className="text-xs text-muted-foreground">Progress</p>
                  <p className="text-sm font-medium">{tracking.progress || 0}</p>
                </div>

                {/* Rating */}
                {tracking.rating && (
                  <div>
                    <p className="text-xs text-muted-foreground">Rating</p>
                    <p className="text-sm font-medium">⭐ {tracking.rating}/10</p>
                  </div>
                )}

                {/* Priority */}
                {tracking.priority && (
                  <div>
                    <p className="text-xs text-muted-foreground">Priority</p>
                    <p className="text-sm font-medium capitalize">{tracking.priority}</p>
                  </div>
                )}

                {/* Start Date */}
                {tracking.start_date && (
                  <div>
                    <p className="text-xs text-muted-foreground">Started</p>
                    <p className="text-sm font-medium">
                      {new Date(tracking.start_date).toLocaleDateString()}
                    </p>
                  </div>
                )}

                {/* End Date */}
                {tracking.end_date && (
                  <div>
                    <p className="text-xs text-muted-foreground">Finished</p>
                    <p className="text-sm font-medium">
                      {new Date(tracking.end_date).toLocaleDateString()}
                    </p>
                  </div>
                )}
              </div>

              {/* Notes */}
              {tracking.notes && (
                <div className="mt-4">
                  <p className="text-xs text-muted-foreground mb-1">Notes</p>
                  <p className="text-sm bg-muted p-3 rounded-md">
                    {tracking.notes}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
