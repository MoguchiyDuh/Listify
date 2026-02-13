import { Card } from "./ui/Card";
import { Button } from "./ui/Button";
import { Star, Plus } from "lucide-react";
import type { AnyMedia, Tracking, Series, Anime, Manga } from "../types";
import { API_BASE_URL } from "../lib/api";

interface MediaCardProps {
  media: AnyMedia;
  tracking?: Tracking;
  onAddToList?: () => void;
  onClick?: () => void;
  adding?: boolean;
}

export function MediaCard({ media, tracking, onAddToList, onClick, adding }: MediaCardProps) {
  const imageUrl = media.cover_image_url?.startsWith("/static")
    ? `${API_BASE_URL}${media.cover_image_url}`
    : media.cover_image_url;

  const getStatusTag = () => {
    if (media.media_type === "series" || media.media_type === "anime" || media.media_type === "manga") {
      const status = (media as Series | Anime | Manga).status;
      if (status === "airing") return { text: "AIRING", color: "bg-green-500/20 text-green-500" };
      if (status === "finished") return { text: "FINISHED", color: "bg-blue-500/20 text-blue-500" };
      if (status === "upcoming") return { text: "UPCOMING", color: "bg-purple-500/20 text-purple-500" };
      if (status === "cancelled") return { text: "CANCELLED", color: "bg-red-500/20 text-red-500" };
    }
    return null;
  };

  const getTrackingStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "bg-green-500/20 text-green-500";
      case "in_progress": return "bg-blue-500/20 text-blue-500";
      case "planned": return "bg-purple-500/20 text-purple-500";
      case "on_hold": return "bg-yellow-500/20 text-yellow-500";
      case "dropped": return "bg-red-500/20 text-red-500";
      default: return "bg-gray-500/20 text-gray-500";
    }
  };

  const getProgressLabel = () => {
    switch (media.media_type) {
      case "game":
        return "Hours";
      case "book":
        return "Pages";
      case "manga":
        return "Chapters";
      case "anime":
      case "series":
        return "Episodes";
      default:
        return "Progress";
    }
  };

  const formatDate = (date: string | null | undefined) => {
    if (!date) return null;
    return new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const statusTag = getStatusTag();

  return (
    <Card className="overflow-hidden hover:border-primary/50 transition-colors cursor-pointer" onClick={onClick}>
      <div className="aspect-[2/3] bg-muted relative">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={media.title}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.currentTarget.src = "https://via.placeholder.com/300x450?text=No+Image";
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-muted-foreground">
            No Image
          </div>
        )}

        {/* Badges on image */}
        {tracking?.favorite && (
          <div className="absolute top-2 right-2 bg-yellow-500 rounded-full p-1.5 shadow-lg">
            <Star className="w-4 h-4 text-white fill-current" />
          </div>
        )}

        {tracking?.rating && (
          <div className="absolute top-2 left-2 bg-background/95 rounded px-2 py-1 shadow-lg">
            <span className="text-sm font-bold">⭐ {tracking.rating}</span>
          </div>
        )}
      </div>

      {/* Card content */}
      <div className="p-3 flex flex-col gap-3">
        {/* Title */}
        <h3 className="font-semibold text-lg line-clamp-2">
          {media.title}
        </h3>

        {/* Status Tags */}
        <div className="flex gap-1 flex-wrap">
          {/* Media status tag */}
          {statusTag && (
            <span className={`${statusTag.color} px-2 py-0.5 rounded-full text-xs font-medium`}>
              {statusTag.text}
            </span>
          )}

          {/* Tracking status tag */}
          {tracking && (
            <span className={`${getTrackingStatusColor(tracking.status)} px-2 py-0.5 rounded-full text-xs font-medium capitalize`}>
              {tracking.status.replace("_", " ")}
            </span>
          )}

          {/* Progress tag */}
          {tracking && tracking.progress > 0 && (
            <span className="bg-muted px-2 py-0.5 rounded-full text-xs font-medium">
              {tracking.progress} {getProgressLabel()}
            </span>
          )}
        </div>

        {/* Genre Tags - show first 5 */}
        {media.tags && media.tags.length > 0 && (
          <div className="flex gap-1 flex-wrap">
            {media.tags.slice(0, 5).map((tag, idx) => (
              <span key={idx} className="bg-muted/50 px-2 py-0.5 rounded-full text-xs text-muted-foreground">
                {tag}
              </span>
            ))}
            {media.tags.length > 5 && (
              <span className="bg-muted/50 px-2 py-0.5 rounded-full text-xs text-muted-foreground">
                +{media.tags.length - 5}
              </span>
            )}
          </div>
        )}

        {/* Dates at bottom */}
        {tracking && (tracking.start_date || tracking.end_date) && (
          <div className="text-sm text-muted-foreground mt-auto pt-3 border-t border-border/50">
            {tracking.start_date && (
              <div>Started: {formatDate(tracking.start_date)}</div>
            )}
            {tracking.end_date && (
              <div>Finished: {formatDate(tracking.end_date)}</div>
            )}
          </div>
        )}

        {/* Add to list button */}
        {!tracking && onAddToList && (
          <Button
            variant="default"
            size="sm"
            className="w-full mt-2"
            onClick={(e) => {
              e.stopPropagation();
              onAddToList();
            }}
            disabled={adding}
          >
            <Plus className="w-4 h-4 mr-1" />
            {adding ? "Adding..." : "Add to List"}
          </Button>
        )}
      </div>
    </Card>
  );
}
