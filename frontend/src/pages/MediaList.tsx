import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../lib/api";
import { MediaCard } from "../components/MediaCard";
import { MediaDetailModal } from "../components/MediaDetailModal";
import { EditTrackingDialog } from "../components/EditTrackingDialog";
import { AddCustomMediaDialog } from "../components/AddCustomMediaDialog";
import { AddMediaDialog } from "../components/AddMediaDialog";
import { Button } from "../components/ui/Button";
import { LibraryToolbar } from "../components/LibraryToolbar";
import type { SortOption } from "../components/LibraryToolbar";
import type { Tracking, MediaType, TrackingStatus } from "../types";

interface MediaListProps {
  mediaType: MediaType | "all";
  title: string;
}

const ITEMS_PER_PAGE = 100;

export function MediaList({ mediaType, title }: MediaListProps) {
  const { user } = useAuth();
  const [tracking, setTracking] = useState<Tracking[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTracking, setSelectedTracking] = useState<Tracking | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [editingTracking, setEditingTracking] = useState<Tracking | null>(null);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showCustomDialog, setShowCustomDialog] = useState(false);
  const [showTrackingDialog, setShowTrackingDialog] = useState(false);
  const [customMediaData, setCustomMediaData] = useState<any>(null);
  const [searchParams, setSearchParams] = useSearchParams();

  // Filter and sort state
  const [statusFilter, setStatusFilter] = useState<TrackingStatus | "all">(
    (searchParams.get("status") as TrackingStatus) || "all"
  );
  const [mediaTypeFilter, setMediaTypeFilter] = useState<MediaType | "all">(
    mediaType === "all" 
      ? (searchParams.get("type") as MediaType || "all")
      : mediaType
  );
  const [sortBy, setSortBy] = useState<SortOption>("created_at");
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    // If the prop mediaType changes (e.g. navigation), update the filter
    setMediaTypeFilter(mediaType);
    setCurrentPage(1);
  }, [mediaType]);

  useEffect(() => {
    const params: Record<string, string> = {};
    if (statusFilter !== "all") params.status = statusFilter;
    if (mediaType === "all" && mediaTypeFilter !== "all") {
      params.type = mediaTypeFilter;
    }
    setSearchParams(params, { replace: true });
  }, [statusFilter, mediaTypeFilter, mediaType, setSearchParams]);

  useEffect(() => {
    loadTracking();
  }, [mediaTypeFilter, statusFilter, sortBy, currentPage]);

  const loadTracking = async () => {
    try {
      setLoading(true);
      const skip = (currentPage - 1) * ITEMS_PER_PAGE;
      const data = await api.getTracking(
        statusFilter === "all" ? undefined : statusFilter,
        mediaTypeFilter === "all" ? undefined : mediaTypeFilter,
        sortBy,
        skip,
        ITEMS_PER_PAGE
      );
      setTracking(data);
    } catch (error) {
      console.error("Failed to load tracking:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = (status: TrackingStatus | "all") => {
    setStatusFilter(status);
    setCurrentPage(1);
    if (status === "planned") {
      setSortBy("priority");
    }
  };

  const handleMediaTypeChange = (type: MediaType | "all") => {
    setMediaTypeFilter(type);
    setCurrentPage(1);
  };

  const handleSortChange = (sort: SortOption) => {
    setSortBy(sort);
    setCurrentPage(1);
  };

  const handleCardClick = (trackingItem: Tracking) => {
    setSelectedTracking(trackingItem);
    setShowDetailModal(true);
  };

  const handleEdit = (trackingItem: Tracking) => {
    setEditingTracking(trackingItem);
    setShowEditDialog(true);
    setShowDetailModal(false);
  };

  const handleConfirmEdit = async (trackingData: any, mediaData?: any) => {
    if (!user || !editingTracking) return;

    try {
      // Step 1: Update media if provided (only for custom media)
      if (mediaData && editingTracking.media?.is_custom) {
        const mediaId = editingTracking.media_id;
        switch (editingTracking.media_type) {
          case "movie":
            await api.updateMovie(mediaId, mediaData);
            break;
          case "series":
            await api.updateSeries(mediaId, mediaData);
            break;
          case "anime":
            await api.updateAnime(mediaId, mediaData);
            break;
          case "manga":
            await api.updateManga(mediaId, mediaData);
            break;
          case "book":
            await api.updateBook(mediaId, mediaData);
            break;
          case "game":
            await api.updateGame(mediaId, mediaData);
            break;
        }
      }

      // Step 2: Update tracking
      await api.updateTracking(user.id, editingTracking.media_id, trackingData);
      
      setShowEditDialog(false);
      setEditingTracking(null);
      await loadTracking();
    } catch (error) {
      console.error("Failed to update tracking:", error);
      alert("Failed to update tracking");
    }
  };

  const handleDelete = async () => {
    if (!user || !editingTracking) return;

    if (!confirm("Are you sure you want to remove this from your list?")) return;

    try {
      await api.deleteTracking(user.id, editingTracking.media_id);
      setShowEditDialog(false);
      setEditingTracking(null);
      await loadTracking();
    } catch (error) {
      console.error("Failed to delete tracking:", error);
      alert("Failed to delete tracking");
    }
  };

  const handleAddNew = () => {
    setShowCustomDialog(true);
  };

  const handleCustomMediaSubmit = (mediaData: any) => {
    setCustomMediaData(mediaData);
    setShowCustomDialog(false);
    setShowTrackingDialog(true);
  };

  const handleTrackingSubmit = async (trackingData: any) => {
    if (!user || !customMediaData) return;

    try {
      // Step 1: Create custom media
      let createdMedia;
      switch (mediaType) {
        case "movie":
          createdMedia = await api.createMovie(customMediaData);
          break;
        case "series":
          createdMedia = await api.createSeries(customMediaData);
          break;
        case "anime":
          createdMedia = await api.createAnime(customMediaData);
          break;
        case "manga":
          createdMedia = await api.createManga(customMediaData);
          break;
        case "book":
          createdMedia = await api.createBook(customMediaData);
          break;
        case "game":
          createdMedia = await api.createGame(customMediaData);
          break;
        default:
          throw new Error("Invalid media type");
      }

      // Step 2: Create tracking entry
      await api.createTracking({
        media_id: createdMedia.id,
        media_type: createdMedia.media_type as MediaType,
        ...trackingData,
      });

      setShowTrackingDialog(false);
      setCustomMediaData(null);
      await loadTracking();
      alert("Custom media added successfully!");
    } catch (error: any) {
      console.error("Failed to add custom media:", error);
      alert("Failed to add custom media: " + (error.message || "Unknown error"));
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{title}</h1>
          <p className="text-muted-foreground mt-1">
            Viewing your collection
          </p>
        </div>
        {mediaType !== "all" && <Button onClick={handleAddNew}>Add New</Button>}
      </div>

      <LibraryToolbar
        statusFilter={statusFilter}
        mediaTypeFilter={mediaTypeFilter}
        sortBy={sortBy}
        onStatusChange={handleStatusChange}
        onMediaTypeChange={handleMediaTypeChange}
        onSortChange={handleSortChange}
        showMediaTypeFilter={mediaType === "all"}
      />

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : tracking.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          No {title.toLowerCase()} found matching your filters
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {tracking.map((item) => {
              if (!item.media) {
                console.error("Tracking item missing media:", item);
                return null;
              }
              return (
                <MediaCard
                  key={item.id}
                  media={item.media}
                  tracking={item}
                  onClick={() => handleCardClick(item)}
                />
              );
            })}
          </div>

          <div className="flex items-center justify-between mt-8 border-t pt-6">
            <Button
              variant="outline"
              onClick={() => {
                setCurrentPage((prev) => Math.max(prev - 1, 1));
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }}
              disabled={currentPage === 1 || loading}
            >
              Previous
            </Button>
            <span className="text-sm text-muted-foreground font-medium">
              Page {currentPage}
            </span>
            <Button
              variant="outline"
              onClick={() => {
                setCurrentPage((prev) => prev + 1);
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }}
              disabled={tracking.length < ITEMS_PER_PAGE || loading}
            >
              Next
            </Button>
          </div>
        </>
      )}

      <MediaDetailModal
        media={selectedTracking?.media || null}
        tracking={selectedTracking}
        onClose={() => {
          setShowDetailModal(false);
          setSelectedTracking(null);
        }}
        onEdit={handleEdit}
        isOpen={showDetailModal}
      />

      <EditTrackingDialog
        tracking={editingTracking}
        onConfirm={handleConfirmEdit}
        onCancel={() => {
          setShowEditDialog(false);
          setEditingTracking(null);
        }}
        onDelete={handleDelete}
        isOpen={showEditDialog}
      />

      <AddCustomMediaDialog
        mediaType={mediaType as MediaType}
        onConfirm={handleCustomMediaSubmit}
        onCancel={() => {
          setShowCustomDialog(false);
          setCustomMediaData(null);
        }}
        isOpen={showCustomDialog}
      />

      <AddMediaDialog
        media={customMediaData ? { ...customMediaData, media_type: mediaType === "all" ? customMediaData.media_type : mediaType } : null}
        onConfirm={handleTrackingSubmit}
        onCancel={() => {
          setShowTrackingDialog(false);
          setCustomMediaData(null);
        }}
        isOpen={showTrackingDialog}
      />
    </div>
  );
}
