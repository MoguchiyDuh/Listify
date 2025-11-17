import uuid
from pathlib import Path
from typing import List, Optional

from core.database import get_db
from crud import media_crud, tag_crud
from fastapi import (APIRouter, Depends, File, HTTPException, Query,
                     UploadFile, status)
from models import MediaTypeEnum, User
from schemas import (AnimeCreate, AnimeResponse, AnimeUpdate, BookCreate,
                     BookResponse, BookUpdate, GameCreate, GameResponse,
                     GameUpdate, MangaCreate, MangaResponse, MangaUpdate,
                     MovieCreate, MovieResponse, MovieUpdate, SeriesCreate,
                     SeriesResponse, SeriesUpdate)
from sqlalchemy.orm import Session

from .base import logger
from .deps import get_current_user

logger = logger.getChild("media")

router = APIRouter()


@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload an image and return the file URL"""
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}",
        )

    file_ext = file.filename.split(".")[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_ext}"

    static_dir = Path(__file__).parent.parent.parent / "static" / "images"
    static_dir.mkdir(parents=True, exist_ok=True)

    file_path = static_dir / unique_filename

    try:
        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // 1024 // 1024}MB",
            )

        with open(file_path, "wb") as f:
            f.write(content)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")

    return {"url": f"/static/images/{unique_filename}"}


# Movie endpoints
@router.post(
    "/movies", response_model=MovieResponse, status_code=status.HTTP_201_CREATED
)
def create_movie(
    movie: MovieCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new movie"""
    logger.info(f"User {current_user.username} creating movie: {movie.title}")
    return media_crud.create_movie(db, obj_in=movie, user_id=current_user.id)


@router.get("/movies", response_model=List[MovieResponse])
def get_movies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all movies"""
    logger.debug(f"User {current_user.username} fetching movies")
    return media_crud.get_all(
        db, media_type=MediaTypeEnum.MOVIE, skip=skip, limit=limit
    )


@router.get("/movies/{movie_id}", response_model=MovieResponse)
def get_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific movie"""
    logger.debug(f"User {current_user.username} fetching movie: {movie_id}")
    movie = media_crud.get_by_id(db, id=movie_id, media_type=MediaTypeEnum.MOVIE)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.put("/movies/{movie_id}", response_model=MovieResponse)
def update_movie(
    movie_id: int,
    movie: MovieUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a movie"""
    logger.info(f"User {current_user.username} updating movie: {movie_id}")
    try:
        updated_movie = media_crud.update_movie(
            db, id=movie_id, obj_in=movie, user_id=current_user.id
        )
        if not updated_movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        return updated_movie
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a movie"""
    logger.info(f"User {current_user.username} deleting movie: {movie_id}")
    try:
        if not media_crud.delete(db, id=movie_id, user_id=current_user.id):
            raise HTTPException(status_code=404, detail="Movie not found")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# Series endpoints
@router.post(
    "/series", response_model=SeriesResponse, status_code=status.HTTP_201_CREATED
)
def create_series(
    series: SeriesCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new series"""
    logger.info(f"User {current_user.username} creating series: {series.title}")
    return media_crud.create_series(db, obj_in=series, user_id=current_user.id)


@router.get("/series", response_model=List[SeriesResponse])
def get_series_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all series"""
    logger.debug(f"User {current_user.username} fetching series")
    return media_crud.get_all(
        db, media_type=MediaTypeEnum.SERIES, skip=skip, limit=limit
    )


@router.get("/series/{series_id}", response_model=SeriesResponse)
def get_series(
    series_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific series"""
    logger.debug(f"User {current_user.username} fetching series: {series_id}")
    series = media_crud.get_by_id(db, id=series_id, media_type=MediaTypeEnum.SERIES)
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")
    return series


@router.put("/series/{series_id}", response_model=SeriesResponse)
def update_series(
    series_id: int,
    series: SeriesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a series"""
    logger.info(f"User {current_user.username} updating series: {series_id}")
    try:
        updated_series = media_crud.update_series(
            db, id=series_id, obj_in=series, user_id=current_user.id
        )
        if not updated_series:
            raise HTTPException(status_code=404, detail="Series not found")
        return updated_series
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/series/{series_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_series(
    series_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a series"""
    logger.info(f"User {current_user.username} deleting series: {series_id}")
    try:
        if not media_crud.delete(db, id=series_id, user_id=current_user.id):
            raise HTTPException(status_code=404, detail="Series not found")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# Anime endpoints
@router.post(
    "/anime", response_model=AnimeResponse, status_code=status.HTTP_201_CREATED
)
def create_anime(
    anime: AnimeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new anime"""
    logger.info(f"User {current_user.username} creating anime: {anime.title}")
    return media_crud.create_anime(db, obj_in=anime, user_id=current_user.id)


@router.get("/anime", response_model=List[AnimeResponse])
def get_anime_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all anime"""
    logger.debug(f"User {current_user.username} fetching anime")
    return media_crud.get_all(
        db, media_type=MediaTypeEnum.ANIME, skip=skip, limit=limit
    )


@router.get("/anime/{anime_id}", response_model=AnimeResponse)
def get_anime(
    anime_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific anime"""
    logger.debug(f"User {current_user.username} fetching anime: {anime_id}")
    anime = media_crud.get_by_id(db, id=anime_id, media_type=MediaTypeEnum.ANIME)
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    return anime


@router.put("/anime/{anime_id}", response_model=AnimeResponse)
def update_anime(
    anime_id: int,
    anime: AnimeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an anime"""
    logger.info(f"User {current_user.username} updating anime: {anime_id}")
    try:
        updated_anime = media_crud.update_anime(
            db, id=anime_id, obj_in=anime, user_id=current_user.id
        )
        if not updated_anime:
            raise HTTPException(status_code=404, detail="Anime not found")
        return updated_anime
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/anime/{anime_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_anime(
    anime_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an anime"""
    logger.info(f"User {current_user.username} deleting anime: {anime_id}")
    try:
        if not media_crud.delete(db, id=anime_id, user_id=current_user.id):
            raise HTTPException(status_code=404, detail="Anime not found")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# Manga endpoints
@router.post(
    "/manga", response_model=MangaResponse, status_code=status.HTTP_201_CREATED
)
def create_manga(
    manga: MangaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new manga"""
    logger.info(f"User {current_user.username} creating manga: {manga.title}")
    return media_crud.create_manga(db, obj_in=manga, user_id=current_user.id)


@router.get("/manga", response_model=List[MangaResponse])
def get_manga_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all manga"""
    logger.debug(f"User {current_user.username} fetching manga")
    return media_crud.get_all(
        db, media_type=MediaTypeEnum.MANGA, skip=skip, limit=limit
    )


@router.get("/manga/{manga_id}", response_model=MangaResponse)
def get_manga(
    manga_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific manga"""
    logger.debug(f"User {current_user.username} fetching manga: {manga_id}")
    manga = media_crud.get_by_id(db, id=manga_id, media_type=MediaTypeEnum.MANGA)
    if not manga:
        raise HTTPException(status_code=404, detail="Manga not found")
    return manga


@router.put("/manga/{manga_id}", response_model=MangaResponse)
def update_manga(
    manga_id: int,
    manga: MangaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a manga"""
    logger.info(f"User {current_user.username} updating manga: {manga_id}")
    try:
        updated_manga = media_crud.update_manga(
            db, id=manga_id, obj_in=manga, user_id=current_user.id
        )
        if not updated_manga:
            raise HTTPException(status_code=404, detail="Manga not found")
        return updated_manga
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/manga/{manga_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_manga(
    manga_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a manga"""
    logger.info(f"User {current_user.username} deleting manga: {manga_id}")
    try:
        if not media_crud.delete(db, id=manga_id, user_id=current_user.id):
            raise HTTPException(status_code=404, detail="Manga not found")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# Book endpoints
@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new book"""
    logger.info(f"User {current_user.username} creating book: {book.title}")
    return media_crud.create_book(db, obj_in=book, user_id=current_user.id)


@router.get("/books", response_model=List[BookResponse])
def get_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all books"""
    logger.debug(f"User {current_user.username} fetching books")
    return media_crud.get_all(db, media_type=MediaTypeEnum.BOOK, skip=skip, limit=limit)


@router.get("/books/{book_id}", response_model=BookResponse)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific book"""
    logger.debug(f"User {current_user.username} fetching book: {book_id}")
    book = media_crud.get_by_id(db, id=book_id, media_type=MediaTypeEnum.BOOK)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.put("/books/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a book"""
    logger.info(f"User {current_user.username} updating book: {book_id}")
    try:
        updated_book = media_crud.update_book(
            db, id=book_id, obj_in=book, user_id=current_user.id
        )
        if not updated_book:
            raise HTTPException(status_code=404, detail="Book not found")
        return updated_book
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a book"""
    logger.info(f"User {current_user.username} deleting book: {book_id}")
    try:
        if not media_crud.delete(db, id=book_id, user_id=current_user.id):
            raise HTTPException(status_code=404, detail="Book not found")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# Game endpoints
@router.post("/games", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
def create_game(
    game: GameCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new game"""
    logger.info(f"User {current_user.username} creating game: {game.title}")
    return media_crud.create_game(db, obj_in=game, user_id=current_user.id)


@router.get("/games", response_model=List[GameResponse])
def get_games(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all games"""
    logger.debug(f"User {current_user.username} fetching games")
    return media_crud.get_all(db, media_type=MediaTypeEnum.GAME, skip=skip, limit=limit)


@router.get("/games/{game_id}", response_model=GameResponse)
def get_game(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific game"""
    logger.debug(f"User {current_user.username} fetching game: {game_id}")
    game = media_crud.get_by_id(db, id=game_id, media_type=MediaTypeEnum.GAME)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.put("/games/{game_id}", response_model=GameResponse)
def update_game(
    game_id: int,
    game: GameUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a game"""
    logger.info(f"User {current_user.username} updating game: {game_id}")
    try:
        updated_game = media_crud.update_game(
            db, id=game_id, obj_in=game, user_id=current_user.id
        )
        if not updated_game:
            raise HTTPException(status_code=404, detail="Game not found")
        return updated_game
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a game"""
    logger.info(f"User {current_user.username} deleting game: {game_id}")
    try:
        if not media_crud.delete(db, id=game_id, user_id=current_user.id):
            raise HTTPException(status_code=404, detail="Game not found")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# Search endpoint
@router.get("/search")
def search_media(
    q: str = Query(..., min_length=1),
    media_type: Optional[MediaTypeEnum] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search across all media types"""
    logger.info(f"User {current_user.username} searching for: {q}")
    results = media_crud.search(db, query=q, media_type=media_type, limit=limit)
    return results
