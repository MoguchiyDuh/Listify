import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { Layout } from "./components/Layout";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";
import { Dashboard } from "./pages/Dashboard";
import { MediaList } from "./pages/MediaList";
import { Search } from "./pages/Search";
import { Favorites } from "./pages/Favorites";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={user ? <Navigate to="/" replace /> : <Login />}
      />
      <Route
        path="/register"
        element={user ? <Navigate to="/" replace /> : <Register />}
      />
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/search" element={<Search />} />
        <Route path="/favorites" element={<Favorites />} />
        <Route
          path="/library"
          element={<MediaList mediaType="all" title="My Library" />}
        />
        <Route
          path="/movies"
          element={<MediaList mediaType="movie" title="Movies" />}
        />
        <Route
          path="/series"
          element={<MediaList mediaType="series" title="Series" />}
        />
        <Route
          path="/anime"
          element={<MediaList mediaType="anime" title="Anime" />}
        />
        <Route
          path="/manga"
          element={<MediaList mediaType="manga" title="Manga" />}
        />
        <Route
          path="/books"
          element={<MediaList mediaType="book" title="Books" />}
        />
        <Route
          path="/games"
          element={<MediaList mediaType="game" title="Games" />}
        />
      </Route>
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
