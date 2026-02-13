import { Filter, SortAsc } from "lucide-react";
import type { TrackingStatus, MediaType } from "../types";

export type SortOption = "priority" | "title" | "rating" | "created_at";

interface LibraryToolbarProps {
  statusFilter: TrackingStatus | "all";
  mediaTypeFilter: MediaType | "all";
  sortBy: SortOption;
  onStatusChange: (status: TrackingStatus | "all") => void;
  onMediaTypeChange: (type: MediaType | "all") => void;
  onSortChange: (sort: SortOption) => void;
  showMediaTypeFilter?: boolean;
}

export function LibraryToolbar({
  statusFilter,
  mediaTypeFilter,
  sortBy,
  onStatusChange,
  onMediaTypeChange,
  onSortChange,
  showMediaTypeFilter = true,
}: LibraryToolbarProps) {
  return (
    <div className="flex flex-wrap items-center gap-4 bg-card p-4 rounded-lg border shadow-sm">
      <div className="flex items-center gap-2">
        <Filter className="w-4 h-4 text-muted-foreground" />
        <span className="text-sm font-medium">Filters:</span>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <select
          value={statusFilter}
          onChange={(e) => onStatusChange(e.target.value as TrackingStatus | "all")}
          className="bg-background border rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="all">All Statuses</option>
          <option value="planned">Planned</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="dropped">Dropped</option>
          <option value="on_hold">On Hold</option>
        </select>

        {showMediaTypeFilter && (
          <select
            value={mediaTypeFilter}
            onChange={(e) => onMediaTypeChange(e.target.value as MediaType | "all")}
            className="bg-background border rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="all">All Media Types</option>
            <option value="movie">Movies</option>
            <option value="series">Series</option>
            <option value="anime">Anime</option>
            <option value="manga">Manga</option>
            <option value="book">Books</option>
            <option value="game">Games</option>
          </select>
        )}
      </div>

      <div className="h-6 w-px bg-border mx-2 hidden md:block" />

      <div className="flex items-center gap-2">
        <SortAsc className="w-4 h-4 text-muted-foreground" />
        <span className="text-sm font-medium">Sort by:</span>
      </div>

      <select
        value={sortBy}
        onChange={(e) => onSortChange(e.target.value as SortOption)}
        className="bg-background border rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
      >
        <option value="priority">Priority</option>
        <option value="title">Title</option>
        <option value="rating">Rating</option>
        <option value="created_at">Date Added</option>
      </select>
    </div>
  );
}
