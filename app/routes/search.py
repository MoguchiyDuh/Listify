from fastapi import APIRouter, Depends, Query

from app.core.logger import setup_logger
from app.models import User
from app.routes.deps import get_current_user
from app.services.igdb import IGDBService
from app.services.jikan import JikanService
from app.services.openlibrary import OpenLibraryService
from app.services.tmdb import TMDBService

logger = setup_logger("api.search")

router = APIRouter()


@router.get("/movies")
async def search_movies(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
):
    """Search movies using TMDB"""
    logger.info(f"User {current_user.username} searching TMDB movies for: {q}")

    async with TMDBService() as service:
        results = await service.search(q, limit=limit, media_type="movie")

    return {"results": results, "source": "tmdb"}


@router.get("/series")
async def search_series(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
):
    """Search TV series using TMDB"""
    logger.info(f"User {current_user.username} searching TMDB series for: {q}")

    async with TMDBService() as service:
        results = await service.search(q, limit=limit, media_type="tv")

    return {"results": results, "source": "tmdb"}


@router.get("/anime")
async def search_anime(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
):
    """Search anime using Jikan (MyAnimeList)"""
    logger.info(f"User {current_user.username} searching Jikan anime for: {q}")

    async with JikanService() as service:
        results = await service.search(q, limit=limit, media_type="anime")

    return {"results": results, "source": "jikan"}


@router.get("/manga")
async def search_manga(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
):
    """Search manga using Jikan (MyAnimeList)"""
    logger.info(f"User {current_user.username} searching Jikan manga for: {q}")

    async with JikanService() as service:
        results = await service.search(q, limit=limit, media_type="manga")

    return {"results": results, "source": "jikan"}


@router.get("/books")
async def search_books(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
):
    """Search books using Open Library"""
    logger.info(f"User {current_user.username} searching Open Library for: {q}")

    async with OpenLibraryService() as service:
        results = await service.search(q, limit=limit)

    return {"results": results, "source": "openlibrary"}


@router.get("/games")
async def search_games(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
):
    """Search games using IGDB"""
    logger.info(f"User {current_user.username} searching IGDB for: {q}")

    async with IGDBService() as service:
        results = await service.search(q, limit=limit)

    return {"results": results, "source": "igdb"}


@router.get("/movies/{movie_id}")
async def get_movie_details(
    movie_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get movie details from TMDB"""
    logger.info(f"User {current_user.username} fetching TMDB movie: {movie_id}")

    async with TMDBService() as service:
        result = await service.get_by_id(movie_id, media_type="movie")

    if not result:
        return {"error": "Movie not found"}, 404

    return {"result": result, "source": "tmdb"}


@router.get("/series/{series_id}")
async def get_series_details(
    series_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get series details from TMDB"""
    logger.info(f"User {current_user.username} fetching TMDB series: {series_id}")

    async with TMDBService() as service:
        result = await service.get_by_id(series_id, media_type="tv")

    if not result:
        return {"error": "Series not found"}, 404

    return {"result": result, "source": "tmdb"}


@router.get("/anime/{anime_id}")
async def get_anime_details(
    anime_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get anime details from Jikan"""
    logger.info(f"User {current_user.username} fetching Jikan anime: {anime_id}")

    async with JikanService() as service:
        result = await service.get_by_id(anime_id, media_type="anime")

    if not result:
        return {"error": "Anime not found"}, 404

    return {"result": result, "source": "jikan"}


@router.get("/manga/{manga_id}")
async def get_manga_details(
    manga_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get manga details from Jikan"""
    logger.info(f"User {current_user.username} fetching Jikan manga: {manga_id}")

    async with JikanService() as service:
        result = await service.get_by_id(manga_id, media_type="manga")

    if not result:
        return {"error": "Manga not found"}, 404

    return {"result": result, "source": "jikan"}


@router.get("/books/{book_id}")
async def get_book_details(
    book_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get book details from Open Library"""
    logger.info(f"User {current_user.username} fetching Open Library book: {book_id}")

    async with OpenLibraryService() as service:
        result = await service.get_by_id(book_id)

    if not result:
        return {"error": "Book not found"}, 404

    return {"result": result, "source": "openlibrary"}


@router.get("/games/{game_id}")
async def get_game_details(
    game_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get game details from IGDB"""
    logger.info(f"User {current_user.username} fetching IGDB game: {game_id}")

    async with IGDBService() as service:
        result = await service.get_by_id(game_id)

    if not result:
        return {"error": "Game not found"}, 404

    return {"result": result, "source": "igdb"}
