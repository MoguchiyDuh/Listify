import { useState, useEffect } from "react";
import { Button } from "./ui/Button";
import { Input } from "./ui/Input";
import { PrioritySelector } from "./PrioritySelector";
import type { TrackingStatus, TrackingPriority, AnyMedia } from "../types";

interface AddMediaDialogProps {
  media: AnyMedia | null;
  onConfirm: (data: {
    status: TrackingStatus;
    priority?: TrackingPriority;
    rating?: number;
    progress?: number;
    start_date?: string;
    end_date?: string;
    favorite: boolean;
    notes?: string;
  }) => void;
  onCancel: () => void;
  isOpen: boolean;
}

export function AddMediaDialog({ media, onConfirm, onCancel, isOpen }: AddMediaDialogProps) {
  const getTodayDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  const getMaxProgress = (media: AnyMedia): number | null => {
    switch (media.media_type) {
      case "series":
      case "anime":
        return (media as any).total_episodes || null;
      case "manga":
        return (media as any).total_chapters || null;
      case "book":
        return (media as any).pages || null;
      default:
        return null;
    }
  };

  const [status, setStatus] = useState<TrackingStatus>("planned");
  const [priority, setPriority] = useState<TrackingPriority | null>(null);
  const [rating, setRating] = useState<string>("");
  const [progress, setProgress] = useState<string>("0");
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [favorite, setFavorite] = useState(false);
  const [notes, setNotes] = useState("");

  // Reset state when dialog opens
  useEffect(() => {
    if (isOpen) {
      setStatus("planned");
      setPriority(null);
      setRating("");
      setProgress("0");
      setStartDate("");
      setEndDate("");
      setFavorite(false);
      setNotes("");
    }
  }, [isOpen]);

  if (!isOpen || !media) return null;

  const handleStatusChange = (newStatus: TrackingStatus) => {
    setStatus(newStatus);

    if (newStatus === "in_progress" && !startDate) {
      setStartDate(getTodayDate());
    }

    if (newStatus === "completed" || newStatus === "dropped") {
      if (!endDate) {
        setEndDate(getTodayDate());
      }
      if (!startDate) {
        setStartDate(getTodayDate());
      }
      if (newStatus === "completed" && media) {
        const maxProgress = getMaxProgress(media);
        if (maxProgress) {
          setProgress(maxProgress.toString());
        }
      }
    }

    if (newStatus === "planned") {
      setProgress("0");
      setRating("");
      setStartDate("");
      setEndDate("");
    } else {
      setPriority(null);
    }
  };

  const handleSubmit = () => {
    onConfirm({
      status,
      priority: priority || undefined,
      rating: rating ? parseFloat(rating) : undefined,
      progress: progress ? parseInt(progress) : 0,
      start_date: startDate || undefined,
      end_date: endDate || undefined,
      favorite,
      notes: notes || undefined,
    });
  };

  const statuses: { value: TrackingStatus; label: string }[] = [
    { value: "planned", label: "Planned" },
    { value: "in_progress", label: "In Progress" },
    { value: "completed", label: "Completed" },
    { value: "on_hold", label: "On Hold" },
    { value: "dropped", label: "Dropped" },
  ];

  const showProgress = status !== "planned";
  const showRating = status === "completed" || status === "dropped";
  const showStartDate = status !== "planned";
  const showEndDate = status === "completed" || status === "dropped";
  const showPriority = status === "planned";

  const title = media.title || (media as any).name || "Unknown";

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-card border border-border rounded-lg p-6 max-w-md w-full max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">Add to List</h2>
        <p className="text-sm text-muted-foreground mb-4">{title}</p>

        <div className="space-y-4">
          {/* Status */}
          <div>
            <label className="text-sm font-medium mb-2 block">Status</label>
            <div className="flex gap-2 flex-wrap">
              {statuses.map((s) => (
                <Button
                  key={s.value}
                  variant={status === s.value ? "default" : "outline"}
                  size="sm"
                  onClick={() => handleStatusChange(s.value)}
                >
                  {s.label}
                </Button>
              ))}
            </div>
          </div>

          {/* Priority - only show if planned */}
          {showPriority && (
            <div>
              <label className="text-sm font-medium mb-2 block">Priority</label>
              <PrioritySelector value={priority} onChange={setPriority} />
            </div>
          )}

          {/* Progress */}
          {showProgress && (
            <div>
              <label className="text-sm font-medium mb-2 block">Progress</label>
              <Input
                type="number"
                min="0"
                value={progress}
                onChange={(e) => setProgress(e.target.value)}
                placeholder="Episodes/Chapters/Pages"
              />
            </div>
          )}

          {/* Rating */}
          {showRating && (
            <div>
              <label className="text-sm font-medium mb-2 block">Rating (1-10)</label>
              <Input
                type="number"
                min="1"
                max="10"
                step="0.5"
                value={rating}
                onChange={(e) => setRating(e.target.value)}
                placeholder="1-10"
              />
            </div>
          )}

          {/* Start Date */}
          {showStartDate && (
            <div>
              <label className="text-sm font-medium mb-2 block">Start Date</label>
              <Input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
          )}

          {/* End Date */}
          {showEndDate && (
            <div>
              <label className="text-sm font-medium mb-2 block">End Date</label>
              <Input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          )}

          {/* Notes */}
          <div>
            <label className="text-sm font-medium mb-2 block">Notes</label>
            <textarea
              className="w-full min-h-[100px] px-3 py-2 bg-background border border-input rounded-md"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Your thoughts..."
            />
          </div>

          {/* Favorite */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="favorite"
              checked={favorite}
              onChange={(e) => setFavorite(e.target.checked)}
              className="w-4 h-4"
            />
            <label htmlFor="favorite" className="text-sm font-medium">
              Mark as favorite
            </label>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2 mt-6">
          <Button onClick={handleSubmit} className="flex-1">
            Add to List
          </Button>
          <Button onClick={onCancel} variant="outline" className="flex-1">
            Cancel
          </Button>
        </div>
      </div>
    </div>
  );
}
