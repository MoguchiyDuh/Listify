import { useState, useEffect, useRef } from "react";
import { Button } from "./ui/Button";
import { Input } from "./ui/Input";
import { PrioritySelector } from "./PrioritySelector";
import type { Tracking, TrackingStatus, TrackingPriority, AnyMedia } from "../types";
import { api } from "../lib/api";
import { toast } from "sonner";
import { Upload } from "lucide-react";

interface EditTrackingDialogProps {
  tracking: Tracking | null;
  onConfirm: (
    trackingData: {
      status: TrackingStatus;
      priority?: TrackingPriority;
      rating?: number;
      progress?: number;
      start_date?: string;
      end_date?: string;
      favorite: boolean;
      notes?: string;
    },
    mediaData?: any
  ) => void;
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
  const [activeTab, setActiveTab] = useState<"tracking" | "media">("tracking");

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

  // Tracking state
  const [status, setStatus] = useState<TrackingStatus>("planned");
  const [priority, setPriority] = useState<TrackingPriority | null>(null);
  const [rating, setRating] = useState<string>("");
  const [progress, setProgress] = useState<string>("");
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [favorite, setFavorite] = useState(false);
  const [notes, setNotes] = useState("");

  // Media state (for custom media)
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [mediaReleaseDate, setMediaReleaseDate] = useState("");
  const [coverImageUrl, setCoverImageUrl] = useState("");
  const [tags, setTags] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Type-specific media fields
  const [runtime, setRuntime] = useState("");
  const [director, setDirector] = useState("");
  const [totalEpisodes, setTotalEpisodes] = useState("");
  const [totalSeasons, setTotalSeasons] = useState("");
  const [totalChapters, setTotalChapters] = useState("");
  const [totalVolumes, setTotalVolumes] = useState("");
  const [originalTitle, setOriginalTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [authors, setAuthors] = useState("");
  const [isbn, setIsbn] = useState("");
  const [pages, setPages] = useState("");
  const [publisher, setPublisher] = useState("");
  const [developer, setDeveloper] = useState("");
  const [platforms, setPlatforms] = useState("");

  useEffect(() => {
    if (tracking) {
      setStatus(tracking.status);
      setPriority(tracking.priority || null);
      setRating(tracking.rating?.toString() || "");
      setProgress(tracking.progress?.toString() || "");
      setStartDate(tracking.start_date || "");
      setEndDate(tracking.end_date || "");
      setFavorite(tracking.favorite);
      setNotes(tracking.notes || "");

      if (tracking.media && tracking.media.is_custom) {
        const m = tracking.media as any;
        setTitle(m.title || "");
        setDescription(m.description || "");
        setMediaReleaseDate(m.release_date || "");
        setCoverImageUrl(m.cover_image_url || "");
        setTags(m.tags?.join(", ") || "");

        // Set type-specific fields
        setRuntime(m.runtime?.toString() || "");
        setDirector(m.director || "");
        setTotalEpisodes(m.total_episodes?.toString() || "");
        setTotalSeasons(m.total_seasons?.toString() || "");
        setTotalChapters(m.total_chapters?.toString() || "");
        setTotalVolumes(m.total_volumes?.toString() || "");
        setOriginalTitle(m.original_title || "");
        setAuthor(m.author || "");
        setAuthors(m.authors?.join(", ") || "");
        setIsbn(m.isbn || "");
        setPages(m.pages?.toString() || "");
        setPublisher(m.publisher || "");
        setDeveloper(m.developer || "");
        setPlatforms(m.platforms?.join(", ") || "");
      }
    }
  }, [tracking]);

  if (!isOpen || !tracking) return null;

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith("image/")) {
      toast.error("Please upload an image file");
      return;
    }

    // Validate file size (e.g., 5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error("File size must be less than 5MB");
      return;
    }

    try {
      setIsUploading(true);
      const { url } = await api.uploadImage(file);
      setCoverImageUrl(url);
      toast.success("Image uploaded successfully");
    } catch (error) {
      console.error("Upload error:", error);
      toast.error("Failed to upload image");
    } finally {
      setIsUploading(false);
    }
  };

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
      if (newStatus === "completed" && tracking.media) {
        const maxProgress = getMaxProgress(tracking.media);
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
    const trackingData = {
      status,
      priority: priority || undefined,
      rating: rating ? parseFloat(rating) : undefined,
      progress: progress ? parseInt(progress) : 0,
      start_date: startDate || undefined,
      end_date: endDate || undefined,
      favorite,
      notes: notes || undefined,
    };

    let mediaData: any = undefined;
    if (tracking.media?.is_custom) {
      mediaData = {
        title,
        description: description || undefined,
        release_date: mediaReleaseDate || undefined,
        cover_image_url: coverImageUrl || undefined,
        tags: tags ? tags.split(',').map(t => t.trim()).filter(Boolean) : [],
      };

      // Add type-specific fields
      const type = tracking.media_type;
      if (type === "movie") {
        mediaData.runtime = runtime ? parseInt(runtime) : undefined;
        mediaData.director = director || undefined;
      } else if (type === "series") {
        mediaData.total_episodes = totalEpisodes ? parseInt(totalEpisodes) : undefined;
        mediaData.total_seasons = totalSeasons ? parseInt(totalSeasons) : undefined;
      } else if (type === "anime") {
        mediaData.original_title = originalTitle || undefined;
        mediaData.total_episodes = totalEpisodes ? parseInt(totalEpisodes) : undefined;
      } else if (type === "manga") {
        mediaData.original_title = originalTitle || undefined;
        mediaData.total_chapters = totalChapters ? parseInt(totalChapters) : undefined;
        mediaData.total_volumes = totalVolumes ? parseInt(totalVolumes) : undefined;
        mediaData.authors = authors ? authors.split(',').map(a => a.trim()) : undefined;
      } else if (type === "book") {
        mediaData.author = author || undefined;
        mediaData.isbn = isbn || undefined;
        mediaData.pages = pages ? parseInt(pages) : undefined;
        mediaData.publisher = publisher || undefined;
      } else if (type === "game") {
        mediaData.developer = developer || undefined;
        mediaData.publisher = publisher || undefined;
        mediaData.platforms = platforms ? platforms.split(',').map(p => p.trim()) : undefined;
      }
    }

    onConfirm(trackingData, mediaData);
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
        <h2 className="text-xl font-bold mb-4">Edit Entry</h2>
        
        {tracking.media?.is_custom && (
          <div className="flex border-b border-border mb-4">
            <button
              className={`px-4 py-2 text-sm font-medium ${activeTab === "tracking" ? "border-b-2 border-primary text-primary" : "text-muted-foreground"}`}
              onClick={() => setActiveTab("tracking")}
            >
              Tracking
            </button>
            <button
              className={`px-4 py-2 text-sm font-medium ${activeTab === "media" ? "border-b-2 border-primary text-primary" : "text-muted-foreground"}`}
              onClick={() => setActiveTab("media")}
            >
              Media Details
            </button>
          </div>
        )}

        <p className="text-sm text-muted-foreground mb-4">{tracking.media?.title}</p>

        {activeTab === "tracking" ? (
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
            {status === "planned" && (
              <div>
                <label className="text-sm font-medium mb-2 block">Priority</label>
                <PrioritySelector value={priority} onChange={setPriority} />
              </div>
            )}

            {/* Progress */}
            {status !== "planned" && (
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
            {(status === "completed" || status === "dropped") && (
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
            )}

            {/* Start Date */}
            {status !== "planned" && (
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
            {(status === "completed" || status === "dropped") && (
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
        ) : (
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Title *</label>
              <Input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter title"
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Description</label>
              <textarea
                className="w-full min-h-[100px] px-3 py-2 bg-background border border-input rounded-md"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Synopsis or description"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Release Date</label>
              <Input
                type="date"
                value={mediaReleaseDate}
                onChange={(e) => setMediaReleaseDate(e.target.value)}
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Cover Image</label>
              <div className="flex gap-2">
                <Input
                  value={coverImageUrl}
                  onChange={(e) => setCoverImageUrl(e.target.value)}
                  placeholder="https://... or upload a file"
                  className="flex-1"
                />
                <input
                  type="file"
                  ref={fileInputRef}
                  className="hidden"
                  accept="image/*"
                  onChange={handleImageUpload}
                />
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                  title="Upload image"
                >
                  <Upload className={`w-4 h-4 ${isUploading ? 'animate-pulse' : ''}`} />
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Provide a URL or upload a local file
              </p>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Tags (comma-separated)</label>
              <Input
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="action, drama, sci-fi"
              />
            </div>

            {/* Type-specific fields */}
            {tracking.media_type === "movie" && (
              <>
                <div>
                  <label className="text-sm font-medium mb-2 block">Runtime (minutes)</label>
                  <Input
                    type="number"
                    value={runtime}
                    onChange={(e) => setRuntime(e.target.value)}
                    placeholder="120"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Director</label>
                  <Input
                    value={director}
                    onChange={(e) => setDirector(e.target.value)}
                    placeholder="Director name"
                  />
                </div>
              </>
            )}

            {tracking.media_type === "series" && (
              <>
                <div>
                  <label className="text-sm font-medium mb-2 block">Total Episodes</label>
                  <Input
                    type="number"
                    value={totalEpisodes}
                    onChange={(e) => setTotalEpisodes(e.target.value)}
                    placeholder="24"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Total Seasons</label>
                  <Input
                    type="number"
                    value={totalSeasons}
                    onChange={(e) => setTotalSeasons(e.target.value)}
                    placeholder="2"
                  />
                </div>
              </>
            )}

            {tracking.media_type === "anime" && (
              <>
                <div>
                  <label className="text-sm font-medium mb-2 block">Original Title</label>
                  <Input
                    value={originalTitle}
                    onChange={(e) => setOriginalTitle(e.target.value)}
                    placeholder="Japanese title"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Total Episodes</label>
                  <Input
                    type="number"
                    value={totalEpisodes}
                    onChange={(e) => setTotalEpisodes(e.target.value)}
                    placeholder="12"
                  />
                </div>
              </>
            )}

            {tracking.media_type === "manga" && (
              <>
                <div>
                  <label className="text-sm font-medium mb-2 block">Original Title</label>
                  <Input
                    value={originalTitle}
                    onChange={(e) => setOriginalTitle(e.target.value)}
                    placeholder="Japanese title"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Total Chapters</label>
                  <Input
                    type="number"
                    value={totalChapters}
                    onChange={(e) => setTotalChapters(e.target.value)}
                    placeholder="150"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Total Volumes</label>
                  <Input
                    type="number"
                    value={totalVolumes}
                    onChange={(e) => setTotalVolumes(e.target.value)}
                    placeholder="20"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Authors (comma-separated)</label>
                  <Input
                    value={authors}
                    onChange={(e) => setAuthors(e.target.value)}
                    placeholder="Author 1, Author 2"
                  />
                </div>
              </>
            )}

            {tracking.media_type === "book" && (
              <>
                <div>
                  <label className="text-sm font-medium mb-2 block">Author</label>
                  <Input
                    value={author}
                    onChange={(e) => setAuthor(e.target.value)}
                    placeholder="Author name"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">ISBN</label>
                  <Input
                    value={isbn}
                    onChange={(e) => setIsbn(e.target.value)}
                    placeholder="978-..."
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Pages</label>
                  <Input
                    type="number"
                    value={pages}
                    onChange={(e) => setPages(e.target.value)}
                    placeholder="350"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Publisher</label>
                  <Input
                    value={publisher}
                    onChange={(e) => setPublisher(e.target.value)}
                    placeholder="Publisher name"
                  />
                </div>
              </>
            )}

            {tracking.media_type === "game" && (
              <>
                <div>
                  <label className="text-sm font-medium mb-2 block">Developer</label>
                  <Input
                    value={developer}
                    onChange={(e) => setDeveloper(e.target.value)}
                    placeholder="Developer name"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Publisher</label>
                  <Input
                    value={publisher}
                    onChange={(e) => setPublisher(e.target.value)}
                    placeholder="Publisher name"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Platforms (comma-separated)</label>
                  <Input
                    value={platforms}
                    onChange={(e) => setPlatforms(e.target.value)}
                    placeholder="PC, PlayStation, Xbox"
                  />
                </div>
              </>
            )}
          </div>
        )}

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
