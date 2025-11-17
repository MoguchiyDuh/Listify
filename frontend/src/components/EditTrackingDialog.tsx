import { useState, useEffect } from "react";
import { Button } from "./ui/Button";
import { Input } from "./ui/Input";
import type { Tracking, TrackingStatus } from "../types";

interface EditTrackingDialogProps {
  tracking: Tracking | null;
  onConfirm: (data: {
    status: TrackingStatus;
    rating?: number;
    progress?: number;
    start_date?: string;
    end_date?: string;
    favorite: boolean;
    notes?: string;
  }) => void;
  onCancel: () => void;
  onDelete?: () => void;
  isOpen: boolean;
}

export function EditTrackingDialog({
  tracking,
  onConfirm,
  onCancel,
  onDelete,
  isOpen
}: EditTrackingDialogProps) {
  const [status, setStatus] = useState<TrackingStatus>("planned");
  const [rating, setRating] = useState<string>("");
  const [progress, setProgress] = useState<string>("");
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [favorite, setFavorite] = useState(false);
  const [notes, setNotes] = useState("");

  useEffect(() => {
    if (tracking) {
      setStatus(tracking.status);
      setRating(tracking.rating?.toString() || "");
      setProgress(tracking.progress?.toString() || "");
      setStartDate(tracking.start_date || "");
      setEndDate(tracking.end_date || "");
      setFavorite(tracking.favorite);
      setNotes(tracking.notes || "");
    }
  }, [tracking]);

  if (!isOpen || !tracking) return null;

  const handleSubmit = () => {
    onConfirm({
      status,
      rating: rating ? parseFloat(rating) : undefined,
      progress: progress ? parseInt(progress) : undefined,
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

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-card border border-border rounded-lg p-6 max-w-md w-full max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">Edit Tracking</h2>
        <p className="text-sm text-muted-foreground mb-4">{tracking.media?.title}</p>

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
                  onClick={() => setStatus(s.value)}
                >
                  {s.label}
                </Button>
              ))}
            </div>
          </div>

          {/* Progress */}
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

          {/* Rating */}
          <div>
            <label className="text-sm font-medium mb-2 block">Rating (0-10)</label>
            <Input
              type="number"
              min="0"
              max="10"
              step="0.1"
              value={rating}
              onChange={(e) => setRating(e.target.value)}
              placeholder="0-10"
            />
          </div>

          {/* Start Date */}
          <div>
            <label className="text-sm font-medium mb-2 block">Start Date</label>
            <Input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>

          {/* End Date */}
          <div>
            <label className="text-sm font-medium mb-2 block">End Date</label>
            <Input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>

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
              id="favorite-edit"
              checked={favorite}
              onChange={(e) => setFavorite(e.target.checked)}
              className="w-4 h-4"
            />
            <label htmlFor="favorite-edit" className="text-sm font-medium">
              Mark as favorite
            </label>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2 mt-6">
          <Button onClick={handleSubmit} className="flex-1">
            Save
          </Button>
          <Button onClick={onCancel} variant="outline" className="flex-1">
            Cancel
          </Button>
          {onDelete && (
            <Button onClick={onDelete} variant="outline" className="text-red-500 hover:text-red-600">
              Delete
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
