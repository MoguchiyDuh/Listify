import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { Card, CardContent, CardDescription, CardHeader } from "../components/ui/Card";
import type { TrackingStats } from "../types";

const typeLabels: Record<string, string> = {
  movie: "Movies",
  series: "TV Series",
  anime: "Anime",
  manga: "Manga",
  book: "Books",
  game: "Video Games",
};

const typePaths: Record<string, string> = {
  movie: "/movies",
  series: "/series",
  anime: "/anime",
  manga: "/manga",
  book: "/books",
  game: "/games",
};

export function Dashboard() {
  const [stats, setStats] = useState<TrackingStats | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await api.getTrackingStats();
      setStats(data);
    } catch (error) {
      console.error("Failed to load stats:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatClick = (path?: string) => {
    if (path) {
      navigate(path);
    }
  };

  if (loading) {
    return <div className="text-center py-12">Loading...</div>;
  }

  if (!stats) {
    return <div className="text-center py-12 text-muted-foreground">No data available</div>;
  }

  const statCards = [
    { label: "Total", value: stats.total, color: "text-primary", path: "/library" },
    { label: "Completed", value: stats.completed, color: "text-green-500", path: "/library?status=completed" },
    { label: "In Progress", value: stats.in_progress, color: "text-blue-500", path: "/library?status=in_progress" },
    { label: "Planned", value: stats.plan_to_watch, color: "text-yellow-500", path: "/library?status=planned" },
    { label: "Dropped", value: stats.dropped, color: "text-red-500", path: "/library?status=dropped" },
    { label: "On Hold", value: stats.on_hold, color: "text-orange-500", path: "/library?status=on_hold" },
    { label: "Favorites", value: stats.favorites, color: "text-pink-500", path: "/favorites" },
    { label: "Avg Rating", value: stats.average_rating.toFixed(1), color: "text-purple-500" },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          Overview of your tracking statistics
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => (
          <Card 
            key={stat.label}
            className={stat.path ? "cursor-pointer hover:shadow-md transition-all hover:-translate-y-1" : ""}
            onClick={() => handleStatClick(stat.path)}
          >
            <CardHeader className="pb-2">
              <CardDescription>{stat.label}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${stat.color}`}>
                {stat.value}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {stats.by_type && (
        <div className="space-y-4">
          <h2 className="text-2xl font-bold">By Media Type</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {Object.entries(stats.by_type).map(([type, count]) => (
              <Card 
                key={type} 
                className="cursor-pointer hover:shadow-md transition-all hover:-translate-y-1"
                onClick={() => handleStatClick(typePaths[type])}
              >
                <CardHeader className="pb-2 text-center">
                  <CardDescription>{typeLabels[type] || type}</CardDescription>
                </CardHeader>
                <CardContent className="text-center">
                  <div className="text-2xl font-bold">
                    {count}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
