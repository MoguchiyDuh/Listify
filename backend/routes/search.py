from fastapi import APIRouter, Body, Depends, Query

from core.exceptions import NotFound
from models import User
from schemas import (
    AnimeCreate,
    BookCreate,
    GameCreate,
    MangaCreate,
    MovieCreate,
    SeriesCreate,
)
from services import IGDBService, JikanService, OpenLibraryService, TMDBService

from .base import logger
from .deps import get_current_user

logger = logger.bind(module="search")

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
        raise NotFound("Movie", movie_id)

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
        raise NotFound("Series", series_id)

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
        raise NotFound("Anime", anime_id)

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
        raise NotFound("Manga", manga_id)

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
        raise NotFound("Book", book_id)

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
        raise NotFound("Game", game_id)

    return {"result": result, "source": "igdb"}


@router.post("/convert/movie", response_model=MovieCreate)
async def convert_movie(
    external_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
):
    """Convert TMDB movie data to MovieCreate schema"""
    async with TMDBService() as service:
        # If no genres in data (search result), fetch full details
        if "genres" not in external_data and external_data.get("id"):
            logger.debug(f"Fetching full movie details for ID: {external_data['id']}")
            full_data = await service.get_by_id(
                str(external_data["id"]), media_type="movie"
            )
            if full_data:
                external_data = full_data

        return service.to_movie_create(external_data)


@router.post("/convert/series", response_model=SeriesCreate)
async def convert_series(
    external_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
):
    """Convert TMDB series data to SeriesCreate schema"""
    async with TMDBService() as service:
        # If no genres in data (search result), fetch full details
        if "genres" not in external_data and external_data.get("id"):
            logger.debug(f"Fetching full series details for ID: {external_data['id']}")
            full_data = await service.get_by_id(
                str(external_data["id"]), media_type="tv"
            )
            if full_data:
                external_data = full_data

        return service.to_series_create(external_data)


@router.post("/convert/anime", response_model=AnimeCreate)
async def convert_anime(
    external_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
):
    """Convert Jikan anime data to AnimeCreate schema"""
    service = JikanService()
    return service.to_anime_create(external_data)


@router.post("/convert/manga", response_model=MangaCreate)
async def convert_manga(
    external_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
):
    """Convert Jikan manga data to MangaCreate schema"""
    service = JikanService()
    return service.to_manga_create(external_data)


@router.post("/convert/game", response_model=GameCreate)
async def convert_game(
    external_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
):
    """Convert IGDB game data to GameCreate schema"""
    service = IGDBService()
    return service.to_game_create(external_data)


@router.post("/convert/book", response_model=BookCreate)
async def convert_book(
    external_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
):
    """Convert Open Library book data to BookCreate schema"""
    async with OpenLibraryService() as service:
        return service.to_book_create(external_data)
