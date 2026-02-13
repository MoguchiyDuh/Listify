import { Link, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Button } from "./ui/Button";
import {
  Film,
  Tv,
  Sparkles,
  BookOpen,
  Book,
  Gamepad2,
  Star,
  BarChart3,
  LogOut,
  Search,
  LayoutGrid,
} from "lucide-react";

export function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const navItems = [
    { to: "/", icon: BarChart3, label: "Dashboard" },
    { to: "/search", icon: Search, label: "Search" },
    { to: "/favorites", icon: Star, label: "Favorites" },
    { divider: true },
    { to: "/library", icon: LayoutGrid, label: "My Library" },
    { to: "/movies", icon: Film, label: "Movies" },
    { to: "/series", icon: Tv, label: "Series" },
    { to: "/anime", icon: Sparkles, label: "Anime" },
    { to: "/manga", icon: BookOpen, label: "Manga" },
    { to: "/books", icon: Book, label: "Books" },
    { to: "/games", icon: Gamepad2, label: "Games" },
  ];

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-card border-r border-border flex flex-col">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-primary">Listify</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {user?.username}
          </p>
        </div>

        <nav className="flex-1 px-4 space-y-1">
          {navItems.map((item, index) => {
            if ("divider" in item) {
              return <div key={index} className="h-px bg-border my-4" />;
            }

            const Icon = item.icon!;
            return (
              <Link
                key={item.to}
                to={item.to!}
                className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
              >
                <Icon className="w-5 h-5" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-border">
          <Button
            variant="ghost"
            className="w-full justify-start"
            onClick={handleLogout}
          >
            <LogOut className="w-5 h-5 mr-3" />
            Logout
          </Button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
