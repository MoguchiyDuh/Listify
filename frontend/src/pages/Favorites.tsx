import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { MediaCard } from "../components/MediaCard";
import type { Tracking } from "../types";

export function Favorites() {
  const [favorites, setFavorites] = useState<Tracking[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFavorites();
  }, []);

  const loadFavorites = async () => {
    try {
      const data = await api.getFavorites();
      setFavorites(data);
    } catch (error) {
      console.error("Failed to load favorites:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Favorites</h1>
        <p className="text-muted-foreground mt-1">
          {favorites.length} favorite items
        </p>
      </div>

      {favorites.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          No favorites yet
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {favorites.map((item) => (
            <MediaCard
              key={item.id}
              media={item.media!}
              tracking={item}
            />
          ))}
        </div>
      )}
    </div>
  );
}
