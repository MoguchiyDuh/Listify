import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Card, CardContent, CardDescription, CardHeader } from "../components/ui/Card";
import type { TrackingStats } from "../types";

export function Dashboard() {
  const [stats, setStats] = useState<TrackingStats | null>(null);
  const [loading, setLoading] = useState(true);

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

  if (loading) {
    return <div className="text-center">Loading...</div>;
  }

  if (!stats) {
    return <div className="text-center text-muted-foreground">No data available</div>;
  }

  const statCards = [
    { label: "Total", value: stats.total, color: "text-primary" },
    { label: "Completed", value: stats.completed, color: "text-green-500" },
    { label: "In Progress", value: stats.in_progress, color: "text-blue-500" },
    { label: "Planned", value: stats.plan_to_watch, color: "text-yellow-500" },
    { label: "Dropped", value: stats.dropped, color: "text-red-500" },
    { label: "On Hold", value: stats.on_hold, color: "text-orange-500" },
    { label: "Favorites", value: stats.favorites, color: "text-pink-500" },
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
          <Card key={stat.label}>
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
    </div>
  );
}
