import uuid
from pathlib import Path
from typing import List, Optional

import magic
from fastapi import APIRouter, Depends, File, Query, UploadFile, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.exceptions import NotFound, PermissionDenied, ValidationError
from core.limiter import limiter
from crud import media_crud, tag_crud
from models import MediaTypeEnum, User
from schemas import (
    AnimeCreate,
    AnimeResponse,
    AnimeUpdate,
    BookCreate,
    BookResponse,
    BookUpdate,
    GameCreate,
    GameResponse,
    GameUpdate,
    MangaCreate,
    MangaResponse,
    MangaUpdate,
    MovieCreate,
    MovieResponse,
    MovieUpdate,
    SeriesCreate,
    SeriesResponse,
    SeriesUpdate,
)

from .base import logger
from .deps import get_current_user

logger = logger.bind(module="media")

router = APIRouter()


@router.post("/upload-image")
@limiter.limit("10/minute")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload an image and return the file URL"""
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]

    if file.content_type not in allowed_types:
        raise ValidationError(
            f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )

    file_ext = file.filename.split(".")[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_ext}"

    static_dir = Path(__file__).parent.parent / "static" / "images"
    static_dir.mkdir(parents=True, exist_ok=True)

    file_path = static_dir / unique_filename

    try:
        content = await file.read()

        # Magic number validation
        mime = magic.from_buffer(content, mime=True)
        if mime not in allowed_types:
            raise ValidationError(
                f"Invalid file content. Detected: {mime}. Allowed types: {', '.join(allowed_types)}"
            )

        if len(content) > MAX_FILE_SIZE:
            raise ValidationError(
                f"File too large. Maximum size: {MAX_FILE_SIZE // 1024 // 1024}MB"
            )

        with open(file_path, "wb") as f:
            f.write(content)
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise ValidationError("Failed to save file")

    return {"url": f"/static/images/{unique_filename}"}


# Movie endpoints
@router.post(
    "/movies", response_model=MovieResponse, status_code=status.HTTP_201_CREATED
)
async def create_movie(
    movie: MovieCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new movie"""
    logger.info(f"User {current_user.username} creating movie: {movie.title}")
    return await media_crud.create_movie(db, obj_in=movie, user_id=current_user.id)


@router.get("/movies", response_model=List[MovieResponse])
async def get_movies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all movies"""
    logger.debug(f"User {current_user.username} fetching movies")
    return await media_crud.get_all(
        db, media_type=MediaTypeEnum.MOVIE, skip=skip, limit=limit
    )


@router.get("/movies/{movie_id}", response_model=MovieResponse)
async def get_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific movie"""
    logger.debug(f"User {current_user.username} fetching movie: {movie_id}")
    movie = await media_crud.get_by_id(db, id=movie_id, media_type=MediaTypeEnum.MOVIE)
    if not movie:
        raise NotFound("Movie", str(movie_id))
    return movie


@router.put("/movies/{movie_id}", response_model=MovieResponse)
async def update_movie(
    movie_id: int,
    movie: MovieUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a movie"""
    logger.info(f"User {current_user.username} updating movie: {movie_id}")
    updated_movie = await media_crud.update_movie(
        db, id=movie_id, obj_in=movie, user_id=current_user.id
    )
    if not updated_movie:
        raise NotFound("Movie", str(movie_id))
    return updated_movie


@router.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a movie"""
    logger.info(f"User {current_user.username} deleting movie: {movie_id}")
    if not await media_crud.delete(db, id=movie_id, user_id=current_user.id):
        raise NotFound("Movie", str(movie_id))


# Series endpoints
@router.post(
    "/series", response_model=SeriesResponse, status_code=status.HTTP_201_CREATED
)
async def create_series(
    series: SeriesCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new series"""
    logger.info(f"User {current_user.username} creating series: {series.title}")
    return await media_crud.create_series(db, obj_in=series, user_id=current_user.id)


@router.get("/series", response_model=List[SeriesResponse])
async def get_series_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all series"""
    logger.debug(f"User {current_user.username} fetching series")
    return await media_crud.get_all(
        db, media_type=MediaTypeEnum.SERIES, skip=skip, limit=limit
    )


@router.get("/series/{series_id}", response_model=SeriesResponse)
async def get_series(
    series_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific series"""
    logger.debug(f"User {current_user.username} fetching series: {series_id}")
    series = await media_crud.get_by_id(
        db, id=series_id, media_type=MediaTypeEnum.SERIES
    )
    if not series:
        raise NotFound("Series", str(series_id))
    return series


@router.put("/series/{series_id}", response_model=SeriesResponse)
async def update_series(
    series_id: int,
    series: SeriesUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a series"""
    logger.info(f"User {current_user.username} updating series: {series_id}")
    updated_series = await media_crud.update_series(
        db, id=series_id, obj_in=series, user_id=current_user.id
    )
    if not updated_series:
        raise NotFound("Series", str(series_id))
    return updated_series


@router.delete("/series/{series_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_series(
    series_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a series"""
    logger.info(f"User {current_user.username} deleting series: {series_id}")
    if not await media_crud.delete(db, id=series_id, user_id=current_user.id):
        raise NotFound("Series", str(series_id))


# Anime endpoints
@router.post(
    "/anime", response_model=AnimeResponse, status_code=status.HTTP_201_CREATED
)
async def create_anime(
    anime: AnimeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new anime"""
    logger.info(f"User {current_user.username} creating anime: {anime.title}")
    return await media_crud.create_anime(db, obj_in=anime, user_id=current_user.id)


@router.get("/anime", response_model=List[AnimeResponse])
async def get_anime_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all anime"""
    logger.debug(f"User {current_user.username} fetching anime")
    return await media_crud.get_all(
        db, media_type=MediaTypeEnum.ANIME, skip=skip, limit=limit
    )


@router.get("/anime/{anime_id}", response_model=AnimeResponse)
async def get_anime(
    anime_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific anime"""
    logger.debug(f"User {current_user.username} fetching anime: {anime_id}")
    anime = await media_crud.get_by_id(db, id=anime_id, media_type=MediaTypeEnum.ANIME)
    if not anime:
        raise NotFound("Anime", str(anime_id))
    return anime


@router.put("/anime/{anime_id}", response_model=AnimeResponse)
async def update_anime(
    anime_id: int,
    anime: AnimeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an anime"""
    logger.info(f"User {current_user.username} updating anime: {anime_id}")
    updated_anime = await media_crud.update_anime(
        db, id=anime_id, obj_in=anime, user_id=current_user.id
    )
    if not updated_anime:
        raise NotFound("Anime", str(anime_id))
    return updated_anime


@router.delete("/anime/{anime_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_anime(
    anime_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an anime"""
    logger.info(f"User {current_user.username} deleting anime: {anime_id}")
    if not await media_crud.delete(db, id=anime_id, user_id=current_user.id):
        raise NotFound("Anime", str(anime_id))


# Manga endpoints
@router.post(
    "/manga", response_model=MangaResponse, status_code=status.HTTP_201_CREATED
)
async def create_manga(
    manga: MangaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new manga"""
    logger.info(f"User {current_user.username} creating manga: {manga.title}")
    return await media_crud.create_manga(db, obj_in=manga, user_id=current_user.id)


@router.get("/manga", response_model=List[MangaResponse])
async def get_manga_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all manga"""
    logger.debug(f"User {current_user.username} fetching manga")
    return await media_crud.get_all(
        db, media_type=MediaTypeEnum.MANGA, skip=skip, limit=limit
    )


@router.get("/manga/{manga_id}", response_model=MangaResponse)
async def get_manga(
    manga_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific manga"""
    logger.debug(f"User {current_user.username} fetching manga: {manga_id}")
    manga = await media_crud.get_by_id(db, id=manga_id, media_type=MediaTypeEnum.MANGA)
    if not manga:
        raise NotFound("Manga", str(manga_id))
    return manga


@router.put("/manga/{manga_id}", response_model=MangaResponse)
async def update_manga(
    manga_id: int,
    manga: MangaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a manga"""
    logger.info(f"User {current_user.username} updating manga: {manga_id}")
    updated_manga = await media_crud.update_manga(
        db, id=manga_id, obj_in=manga, user_id=current_user.id
    )
    if not updated_manga:
        raise NotFound("Manga", str(manga_id))
    return updated_manga


@router.delete("/manga/{manga_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_manga(
    manga_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a manga"""
    logger.info(f"User {current_user.username} deleting manga: {manga_id}")
    if not await media_crud.delete(db, id=manga_id, user_id=current_user.id):
        raise NotFound("Manga", str(manga_id))


# Book endpoints
@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: BookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new book"""
    logger.info(f"User {current_user.username} creating book: {book.title}")
    return await media_crud.create_book(db, obj_in=book, user_id=current_user.id)


@router.get("/books", response_model=List[BookResponse])
async def get_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all books"""
    logger.debug(f"User {current_user.username} fetching books")
    return await media_crud.get_all(
        db, media_type=MediaTypeEnum.BOOK, skip=skip, limit=limit
    )


@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific book"""
    logger.debug(f"User {current_user.username} fetching book: {book_id}")
    book = await media_crud.get_by_id(db, id=book_id, media_type=MediaTypeEnum.BOOK)
    if not book:
        raise NotFound("Book", str(book_id))
    return book


@router.put("/books/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book: BookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a book"""
    logger.info(f"User {current_user.username} updating book: {book_id}")
    updated_book = await media_crud.update_book(
        db, id=book_id, obj_in=book, user_id=current_user.id
    )
    if not updated_book:
        raise NotFound("Book", str(book_id))
    return updated_book


@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a book"""
    logger.info(f"User {current_user.username} deleting book: {book_id}")
    if not await media_crud.delete(db, id=book_id, user_id=current_user.id):
        raise NotFound("Book", str(book_id))


# Game endpoints
@router.post("/games", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_game(
    game: GameCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new game"""
    logger.info(f"User {current_user.username} creating game: {game.title}")
    return await media_crud.create_game(db, obj_in=game, user_id=current_user.id)


@router.get("/games", response_model=List[GameResponse])
async def get_games(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all games"""
    logger.debug(f"User {current_user.username} fetching games")
    return await media_crud.get_all(
        db, media_type=MediaTypeEnum.GAME, skip=skip, limit=limit
    )


@router.get("/games/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific game"""
    logger.debug(f"User {current_user.username} fetching game: {game_id}")
    game = await media_crud.get_by_id(db, id=game_id, media_type=MediaTypeEnum.GAME)
    if not game:
        raise NotFound("Game", str(game_id))
    return game


@router.put("/games/{game_id}", response_model=GameResponse)
async def update_game(
    game_id: int,
    game: GameUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a game"""
    logger.info(f"User {current_user.username} updating game: {game_id}")
    updated_game = await media_crud.update_game(
        db, id=game_id, obj_in=game, user_id=current_user.id
    )
    if not updated_game:
        raise NotFound("Game", str(game_id))
    return updated_game


@router.delete("/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(
    game_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a game"""
    logger.info(f"User {current_user.username} deleting game: {game_id}")
    if not await media_crud.delete(db, id=game_id, user_id=current_user.id):
        raise NotFound("Game", str(game_id))


# Search endpoint
@router.get("/search")
@limiter.limit("30/minute")
async def search_media(
    request: Request,
    q: str = Query(..., min_length=1),
    media_type: Optional[MediaTypeEnum] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search across all media types"""
    logger.info(f"User {current_user.username} searching for: {q}")
    results = await media_crud.search(db, query=q, media_type=media_type, limit=limit)
    return results


@router.post("/gc", status_code=status.HTTP_200_OK)
async def trigger_garbage_collection(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger manual garbage collection of orphaned media"""
    logger.info(f"User {current_user.username} triggered garbage collection")
    deleted_count = await media_crud.cleanup_orphaned_media(db)
    return {"deleted_count": deleted_count}
