import { useState } from "react";
import { Button } from "./ui/Button";
import { Input } from "./ui/Input";
import type { MediaType } from "../types";

interface AddCustomMediaDialogProps {
  mediaType: MediaType;
  onConfirm: (mediaData: any) => void;
  onCancel: () => void;
  isOpen: boolean;
}

export function AddCustomMediaDialog({
  mediaType,
  onConfirm,
  onCancel,
  isOpen
}: AddCustomMediaDialogProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [releaseDate, setReleaseDate] = useState("");
  const [coverImageUrl, setCoverImageUrl] = useState("");

  // Type-specific fields
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

  if (!isOpen) return null;

  const handleSubmit = () => {
    const baseData: any = {
      title,
      description: description || undefined,
      release_date: releaseDate || undefined,
      cover_image_url: coverImageUrl || undefined,
      is_custom: true,
    };

    // Add type-specific fields
    if (mediaType === "movie") {
      baseData.runtime = runtime ? parseInt(runtime) : undefined;
      baseData.director = director || undefined;
    } else if (mediaType === "series") {
      baseData.total_episodes = totalEpisodes ? parseInt(totalEpisodes) : undefined;
      baseData.total_seasons = totalSeasons ? parseInt(totalSeasons) : undefined;
    } else if (mediaType === "anime") {
      baseData.original_title = originalTitle || undefined;
      baseData.total_episodes = totalEpisodes ? parseInt(totalEpisodes) : undefined;
    } else if (mediaType === "manga") {
      baseData.original_title = originalTitle || undefined;
      baseData.total_chapters = totalChapters ? parseInt(totalChapters) : undefined;
      baseData.total_volumes = totalVolumes ? parseInt(totalVolumes) : undefined;
      baseData.authors = authors ? authors.split(',').map(a => a.trim()) : undefined;
    } else if (mediaType === "book") {
      baseData.author = author || undefined;
      baseData.isbn = isbn || undefined;
      baseData.pages = pages ? parseInt(pages) : undefined;
      baseData.publisher = publisher || undefined;
    } else if (mediaType === "game") {
      baseData.developer = developer || undefined;
      baseData.publisher = publisher || undefined;
      baseData.platforms = platforms ? platforms.split(',').map(p => p.trim()) : undefined;
    }

    onConfirm(baseData);
    resetForm();
  };

  const resetForm = () => {
    setTitle("");
    setDescription("");
    setReleaseDate("");
    setCoverImageUrl("");
    setRuntime("");
    setDirector("");
    setTotalEpisodes("");
    setTotalSeasons("");
    setTotalChapters("");
    setTotalVolumes("");
    setOriginalTitle("");
    setAuthor("");
    setAuthors("");
    setIsbn("");
    setPages("");
    setPublisher("");
    setDeveloper("");
    setPlatforms("");
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-card border border-border rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">Add Custom {mediaType.charAt(0).toUpperCase() + mediaType.slice(1)}</h2>

        <div className="space-y-4">
          {/* Title */}
          <div>
            <label className="text-sm font-medium mb-2 block">Title *</label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter title"
              required
            />
          </div>

          {/* Original Title (for anime/manga) */}
          {(mediaType === "anime" || mediaType === "manga") && (
            <div>
              <label className="text-sm font-medium mb-2 block">Original Title</label>
              <Input
                value={originalTitle}
                onChange={(e) => setOriginalTitle(e.target.value)}
                placeholder="Japanese title"
              />
            </div>
          )}

          {/* Description */}
          <div>
            <label className="text-sm font-medium mb-2 block">Description</label>
            <textarea
              className="w-full min-h-[100px] px-3 py-2 bg-background border border-input rounded-md"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Synopsis or description"
            />
          </div>

          {/* Release Date */}
          <div>
            <label className="text-sm font-medium mb-2 block">Release Date</label>
            <Input
              type="date"
              value={releaseDate}
              onChange={(e) => setReleaseDate(e.target.value)}
            />
          </div>

          {/* Cover Image URL */}
          <div>
            <label className="text-sm font-medium mb-2 block">Cover Image URL</label>
            <Input
              value={coverImageUrl}
              onChange={(e) => setCoverImageUrl(e.target.value)}
              placeholder="https://..."
            />
          </div>

          {/* Type-specific fields */}
          {mediaType === "movie" && (
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

          {mediaType === "series" && (
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

          {mediaType === "anime" && (
            <div>
              <label className="text-sm font-medium mb-2 block">Total Episodes</label>
              <Input
                type="number"
                value={totalEpisodes}
                onChange={(e) => setTotalEpisodes(e.target.value)}
                placeholder="12"
              />
            </div>
          )}

          {mediaType === "manga" && (
            <>
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

          {mediaType === "book" && (
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

          {mediaType === "game" && (
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

        {/* Actions */}
        <div className="flex gap-2 mt-6">
          <Button onClick={handleSubmit} className="flex-1" disabled={!title}>
            Add Media
          </Button>
          <Button onClick={() => { onCancel(); resetForm(); }} variant="outline" className="flex-1">
            Cancel
          </Button>
        </div>
      </div>
    </div>
  );
}
