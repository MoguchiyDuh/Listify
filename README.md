# Listify

Self-hosted media tracking application for movies, series, anime, manga, books, and games.

## Features

- Track 6 media types: movies, series, anime, manga, books, games
- Progress tracking (episodes, pages, hours)
- Rating system (0-10 scale)
- Status management (planned, in progress, completed, on hold, dropped)
- Favorites and personal notes
- External API integration (TMDB, Jikan, IGDB, OpenLibrary)
- Custom media entries
- Dashboard statistics

## Tech Stack

**Backend:** Python, FastAPI, SQLAlchemy, JWT auth
**Frontend:** React 19, TypeScript, Vite, Tailwind CSS

## Installation

### Prerequisites

- Python 3.8+
- Node.js 20.0.0+

### Setup

1. Clone and setup:

```bash
git clone <your-repo-url>
cd Listify
chmod +x setup.sh
./setup.sh
```

2. Configure environment:

```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env (SECRET_KEY, CORS_ORIGINS, API keys)

# Frontend
cp frontend/.env.example frontend/.env
# Edit frontend/.env (VITE_API_BASE_URL)
```

3. Start:

```bash
chmod +x start.sh stop.sh
./start.sh
```

4. Access:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Scripts

- `./setup.sh` - Install dependencies and run migrations
- `./start.sh` - Start servers
- `./stop.sh` - Stop servers

## Configuration

### Network Access

To access from other devices:

**backend/.env:**

```env
CORS_ORIGINS=http://YOUR_IP:5173
COOKIE_DOMAIN=YOUR_IP
```

**frontend/.env:**

```env
VITE_API_BASE_URL=http://YOUR_IP:8000
```
