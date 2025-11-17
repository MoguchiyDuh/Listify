import { useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../lib/api";
import { MediaCard } from "../components/MediaCard";
import { MediaDetailModal } from "../components/MediaDetailModal";
import { EditTrackingDialog } from "../components/EditTrackingDialog";
import { AddCustomMediaDialog } from "../components/AddCustomMediaDialog";
import { AddMediaDialog } from "../components/AddMediaDialog";
import { Button } from "../components/ui/Button";
import type { Tracking, MediaType } from "../types";

interface MediaListProps {
  mediaType: MediaType;
  title: string;
}

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

  useEffect(() => {
    loadTracking();
  }, [mediaType]);

  const loadTracking = async () => {
    try {
      const data = await api.getTracking(undefined, mediaType);
      setTracking(data);
    } catch (error) {
      console.error("Failed to load tracking:", error);
    } finally {
      setLoading(false);
    }
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

  const handleConfirmEdit = async (data: any) => {
    if (!user || !editingTracking) return;

    try {
      await api.updateTracking(user.id, editingTracking.media_id, data);
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
        media_type: mediaType,
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

  if (loading) {
    return <div className="text-center">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{title}</h1>
          <p className="text-muted-foreground mt-1">
            {tracking.length} items in your list
          </p>
        </div>
        <Button onClick={handleAddNew}>Add New</Button>
      </div>

      {tracking.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          No {title.toLowerCase()} in your list yet
        </div>
      ) : (
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
        mediaType={mediaType}
        onConfirm={handleCustomMediaSubmit}
        onCancel={() => {
          setShowCustomDialog(false);
          setCustomMediaData(null);
        }}
        isOpen={showCustomDialog}
      />

      <AddMediaDialog
        mediaTitle={customMediaData?.title || ""}
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
